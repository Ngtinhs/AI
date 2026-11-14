import streamlit as st

from config.settings import settings
from models.schemas import TutorAnalysis
from services.youtube_service import get_transcript
from services.gemini_service import analyze_transcript
from utils.validators import extract_video_id, validate_youtube_url


st.set_page_config(
    page_title="YouTube English AI Tutor",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 YouTube English AI Tutor")
st.caption("Turn YouTube videos into simple English lessons for A2 learners.")

# Lưu kết quả trong session để người dùng có thể xem lại khi Streamlit rerun.
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "video_url" not in st.session_state:
    st.session_state.video_url = ""

with st.sidebar:
    st.header("Learner Context")
    st.write("**Native language:** Vietnamese")
    st.write("**English level:** A2")
    st.write("**Goal:** Daily English communication")
    st.write("**Preference:** Simple explanations")

url = st.text_input(
    "YouTube video URL",
    placeholder="https://www.youtube.com/watch?v=...",
)

if st.button("Analyze Video", type="primary", use_container_width=True):
    st.session_state.analysis = None

    if not settings.gemini_api_key:
        st.error("Chưa tìm thấy GEMINI_API_KEY. Hãy thêm API Key vào file .env.")
    elif not validate_youtube_url(url):
        st.error("URL YouTube không hợp lệ. Vui lòng kiểm tra lại đường dẫn.")
    else:
        video_id = extract_video_id(url)

        try:
            with st.spinner("Đang lấy phụ đề từ YouTube..."):
                transcript = get_transcript(video_id)

            with st.spinner("Gemini đang phân tích và tạo bài học..."):
                result = analyze_transcript(transcript)

            st.session_state.analysis = result
            st.session_state.video_url = url
            st.success("Phân tích video thành công!")
        except Exception as exc:
            st.error(str(exc))

analysis: TutorAnalysis | None = st.session_state.analysis

if analysis:
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
    st.write("Chọn một đáp án cho mỗi câu hỏi. Phần giải thích sẽ hiện sau khi bạn kiểm tra.")

    answers = {}
    for index, question in enumerate(analysis.quiz):
        st.markdown(f"**Question {index + 1}. {question.question}**")
        answers[index] = st.radio(
            "Choose one answer:",
            options=range(len(question.options)),
            format_func=lambda choice, options=question.options: (
                f"{chr(65 + choice)}. {options[choice]}"
            ),
            key=f"quiz_{index}_{hash(st.session_state.video_url)}",
            label_visibility="collapsed",
        )

    if st.button("Check my answers", type="primary"):
        correct_count = 0
        for index, question in enumerate(analysis.quiz):
            selected = answers[index]
            is_correct = selected == question.correct_index
            if is_correct:
                correct_count += 1

            st.markdown(f"**Question {index + 1}: {'✅ Correct' if is_correct else '❌ Incorrect'}**")
            st.write(f"Your answer: {question.options[selected]}")
            st.write(f"Correct answer: {question.options[question.correct_index]}")
            st.info(question.explanation_vi)

        st.success(f"Your score: {correct_count}/{len(analysis.quiz)}")
