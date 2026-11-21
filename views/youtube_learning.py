import time

import streamlit as st

from config.settings import (
    ANALYSIS_CACHE_MAX_ENTRIES,
    CACHE_TTL_SECONDS,
    DEFAULT_LEVEL,
    LONG_TRANSCRIPT_CHARS,
    settings,
)
from models.schemas import QuizQuestion, TutorAnalysis
from prompts.tutor_prompt import PROMPT_VERSION
from services.gemini_service import MISSING_API_KEY_MESSAGE, analyze_transcript, is_configured
from services.lesson_service import save_lesson
from services.session_service import clear_lesson, current_level, current_user_id, show_lesson
from services.youtube_service import get_transcript
from utils.timing import StageTimer
from utils.ui import Page, login_link, option_label, page_header
from utils.validators import extract_video_id


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def cached_transcript(video_id: str, _timer: StageTimer) -> str:
    """Tham số bắt đầu bằng "_" không nằm trong khóa cache."""
    return get_transcript(video_id, timer=_timer)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False, max_entries=ANALYSIS_CACHE_MAX_ENTRIES)
def cached_analysis(
    video_id: str,
    model: str,
    prompt_version: str,
    thinking_budget: int | None,
    learner_level: str,
    _transcript: str,
    _timer: StageTimer,
) -> TutorAnalysis:
    """
    Bài học chỉ phụ thuộc video công khai + level + cấu hình model/prompt (đều nằm trong khóa cache),
    nên dùng chung cache giữa các người dùng được. Transcript đã được xác định bởi `video_id`.
    """
    return analyze_transcript(_transcript, timer=_timer, learner_level=learner_level)


def load_transcript(video_id: str, timer: StageTimer, force_refresh: bool) -> str:
    if force_refresh:
        return get_transcript(video_id, timer=timer)
    return cached_transcript(video_id, timer)


def load_analysis(
    video_id: str, transcript: str, learner_level: str, timer: StageTimer, force_refresh: bool
) -> TutorAnalysis:
    if force_refresh:
        return analyze_transcript(transcript, timer=timer, learner_level=learner_level)
    return cached_analysis(
        video_id,
        settings.gemini_model,
        PROMPT_VERSION,
        settings.gemini_thinking_budget,
        learner_level,
        transcript,
        timer,
    )


def run_analysis(url: str, force_refresh: bool, learner_level: str) -> None:
    timer = StageTimer()

    with timer.measure("URL Validation"):
        video_id = extract_video_id(url)

    if not video_id:
        st.error("URL YouTube không hợp lệ. Vui lòng kiểm tra lại đường dẫn.")
        return

    with st.status("Đang xử lý video...", expanded=True) as status:
        try:
            st.write("1/2 · Đang lấy phụ đề từ YouTube...")
            transcript = load_transcript(video_id, timer, force_refresh)
            st.write(f"✓ Đã có phụ đề ({len(transcript):,} ký tự).")

            if len(transcript) > LONG_TRANSCRIPT_CHARS:
                st.warning(
                    "Video này có phụ đề rất dài. Thời gian xử lý có thể lâu hơn "
                    "và có thể vượt giới hạn của model."
                )

            st.write("2/2 · Gemini đang tạo bài học, bước này có thể mất một lúc...")
            result = load_analysis(video_id, transcript, learner_level, timer, force_refresh)

            status.update(label="Phân tích video thành công!", state="complete", expanded=False)
        except Exception as exc:
            status.update(label="Có lỗi xảy ra", state="error", expanded=True)
            st.error(str(exc))
            return

    # Không có bước "Gemini API" nghĩa là kết quả lấy từ cache.
    timer.info["from_cache"] = "Gemini API" not in timer.stages
    show_lesson(result, url, learner_level, timings={"stages": timer.stages, "info": timer.info})

    user_id = current_user_id()
    if not user_id:
        st.info("Đăng nhập để lưu bài học này và xem lại sau.")
        return
    try:
        save_lesson(user_id, video_id, url, learner_level, PROMPT_VERSION, result)
        st.toast("Đã lưu bài học vào mục Progress.", icon="💾")
    except Exception as exc:
        st.warning(f"Không lưu được bài học: {exc}")


def render_analysis(analysis: TutorAnalysis) -> None:
    st.divider()

    st.header("1. Summary")
    st.subheader("English")
    st.write(analysis.summary.english)
    st.subheader("Vietnamese")
    st.write(analysis.summary.vietnamese)

    st.divider()
    st.header("2. Vocabulary")
    for index, item in enumerate(analysis.vocabulary, start=1):
        with st.expander(f"{index}. {item.word} — {item.meaning_vi}", expanded=True):
            st.write(f"**IPA:** {item.ipa or 'Not provided'}")
            st.write(f"**Meaning:** {item.meaning_vi}")
            st.write(f"**Example:** {item.example}")
            st.write(f"**Example translation:** {item.example_vi}")

    st.divider()
    st.header("3. Key Sentences")
    for index, item in enumerate(analysis.key_sentences, start=1):
        with st.expander(f"{index}. {item.english}", expanded=True):
            st.write(f"**Vietnamese:** {item.vietnamese}")
            st.write(f"**How to use:** {item.usage_vi}")

    st.divider()
    st.header("4. Quiz")
    render_quiz(analysis.quiz)


def render_quiz(quiz: list[QuizQuestion]) -> None:
    st.write("Chọn một đáp án cho mỗi câu hỏi. Phần giải thích sẽ hiện sau khi bạn kiểm tra.")

    answers: list[int | None] = []
    for number, question in enumerate(quiz, start=1):
        st.markdown(f"**Question {number}. {question.question}**")
        answers.append(
            st.radio(
                "Choose one answer:",
                options=range(len(question.options)),
                format_func=option_label(question.options),
                index=None,
                key=f"quiz_{st.session_state.lesson_key}_{number}",
                label_visibility="collapsed",
            )
        )

    if not st.button("Check my answers", type="primary"):
        return

    unanswered = sum(selected is None for selected in answers)
    if unanswered:
        st.warning(f"Bạn còn {unanswered} câu chưa trả lời.")
        return

    correct_count = 0
    for number, (question, selected) in enumerate(zip(quiz, answers), start=1):
        is_correct = selected == question.correct_index
        correct_count += is_correct
        st.markdown(f"**Question {number}: {'✅ Correct' if is_correct else '❌ Incorrect'}**")
        st.write(f"Your answer: {question.options[selected]}")
        st.write(f"Correct answer: {question.options[question.correct_index]}")
        st.info(question.explanation_vi)

    st.success(f"Your score: {correct_count}/{len(quiz)}")


def render_timings(render_seconds: float) -> None:
    timings = st.session_state.get("timings")
    if not timings:
        return

    with st.expander("⏱ Chi tiết thời gian xử lý"):
        if timings["info"].get("from_cache"):
            st.success("Kết quả lấy từ cache, không gọi lại YouTube và Gemini.")

        rows = [{"Stage": name, "Seconds": sec} for name, sec in timings["stages"].items()]
        rows.append({"Stage": "UI Rendering (lần hiển thị này)", "Seconds": round(render_seconds, 3)})
        st.table(rows)

        info = {key: value for key, value in timings["info"].items() if key != "from_cache"}
        if info:
            st.caption("Thông tin thêm: " + ", ".join(f"{k} = {v}" for k, v in info.items()))


st.session_state.setdefault("analysis", None)

page_header("▶️ YouTube Learning", "Biến video YouTube thành bài học tiếng Anh theo trình độ của bạn.")

user_id = current_user_id()
learner_level = current_level()

if learner_level and user_id:
    st.success(f"🎯 Bài học sẽ được tạo cho trình độ **{learner_level}** (theo kết quả Placement Test).")
elif learner_level:
    st.success(f"🎯 Bài học sẽ được tạo cho trình độ **{learner_level}** (theo bài test bạn vừa làm).")
    st.caption("Kết quả test chưa được lưu. Đăng nhập để lần sau không phải làm lại.")
    login_link()
else:
    st.warning(
        f"Bạn chưa làm Placement Test, nên bài học sẽ được tạo cho trình độ mặc định "
        f"**{DEFAULT_LEVEL}**. Làm bài test để bài học phù hợp hơn."
    )
    col1, col2 = st.columns(2)
    col1.page_link(Page.PLACEMENT_TEST, label="Làm Placement Test", icon="📝")
    if not user_id:
        login_link("Đã có tài khoản? Đăng nhập", container=col2)

url = st.text_input("YouTube video URL", placeholder="https://www.youtube.com/watch?v=...")
force_refresh = st.checkbox(
    "Phân tích lại từ đầu (bỏ qua cache)",
    help="Dùng khi bạn muốn Gemini tạo một bài học mới cho cùng video.",
)

if st.button("Analyze Video", type="primary", use_container_width=True):
    clear_lesson()
    if is_configured():
        run_analysis(url, force_refresh, learner_level or DEFAULT_LEVEL)
    else:
        st.error(MISSING_API_KEY_MESSAGE)

analysis: TutorAnalysis | None = st.session_state.analysis

render_start = time.perf_counter()
if analysis:
    st.caption(f"Bài học bên dưới được tạo cho trình độ: {st.session_state.get('lesson_level', DEFAULT_LEVEL)}")
    render_analysis(analysis)
render_timings(time.perf_counter() - render_start)
