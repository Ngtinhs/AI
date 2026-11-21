import streamlit as st

from config.settings import GUEST_ID, MIN_CORRECT_TO_PASS, QUIZ_OPTION_COUNT
from models.assessment import BELOW_A1, SKILLS, AssessmentResult, QuestionBank
from models.learner import UNTESTED_SKILLS
from services.assessment_service import (
    get_latest_assessment,
    load_question_bank,
    record_assessment,
    score_answers,
)
from services.session_service import current_user_id
from utils.ui import (
    DATETIME_FORMAT,
    LOGIN_TO_SAVE_LABEL,
    NOT_ASSESSED,
    Page,
    login_link,
    option_label,
    page_header,
)


def show_test(bank: QuestionBank) -> None:
    tested_skills = ", ".join(skill.title() for skill in SKILLS)
    st.markdown(
        f"""
**Hướng dẫn**
- Bài gồm **{len(bank.questions)} câu** trắc nghiệm, khoảng 5–10 phút.
- Kiểm tra {len(SKILLS)} kỹ năng: **{tested_skills}**, từ dễ (A1) đến khó (B2).
- Listening và Speaking **chưa được đánh giá** trong phiên bản này.
- Hãy tự làm, không đoán bừa – kết quả dùng để chọn bài học phù hợp với bạn.
"""
    )

    with st.form("placement_form"):
        answers: dict[str, int | None] = {}
        for number, question in enumerate(bank.questions, start=1):
            st.markdown(f"**Câu {number}** · {question.skill.title()}")
            if question.passage:
                st.info(question.passage)
            answers[question.id] = st.radio(
                question.question,
                options=range(QUIZ_OPTION_COUNT),
                format_func=option_label(question.options),
                index=None,
                key=f"pt_{question.id}",
            )
            st.write("")

        submitted = st.form_submit_button("Nộp bài", type="primary", use_container_width=True)

    if not submitted:
        return

    user_id = current_user_id()
    try:
        result = score_answers(bank, answers, user_id or GUEST_ID)
    except ValueError as exc:
        st.warning(f"{exc} Vui lòng trả lời tất cả các câu trước khi nộp bài.")
        return

    if user_id:
        record_assessment(result)
    else:
        # Khách: chỉ giữ trong phiên, được lưu khi đăng nhập.
        st.session_state.guest_result = result
    st.session_state.pt_retake = False
    st.rerun()


def show_result(result: AssessmentResult, bank: QuestionBank) -> None:
    if not current_user_id():
        st.warning(
            "⚠️ Kết quả này **chưa được lưu** và sẽ mất khi bạn đóng trình duyệt. "
            "Đăng nhập hoặc đăng ký để lưu lại."
        )
        login_link(LOGIN_TO_SAVE_LABEL)

    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        col1.metric("Trình độ ước tính", result.overall_level)
        col2.markdown(
            f"Hoàn thành lúc: {result.completed_at:{DATETIME_FORMAT}}  \n"
            f"Bộ câu hỏi: `{result.bank_version}`"
        )
        if result.overall_level == BELOW_A1:
            col2.write("Bạn chưa đạt A1. Hãy bắt đầu với các bài học nền tảng nhất.")

    st.subheader("Vì sao ra kết quả này?")
    st.write(
        f"Đạt một level khi đúng ít nhất **{MIN_CORRECT_TO_PASS}** câu của level đó. "
        "Trình độ của bạn là level cao nhất mà **tất cả** các level từ A1 đến đó đều đạt."
    )
    st.table(
        [
            {
                "Level": score.level,
                "Đúng": f"{score.correct}/{score.total}",
                "Kết quả": "✅ Đạt" if score.passed else "❌ Chưa đạt",
            }
            for score in result.level_scores
        ]
    )

    if result.inconsistent:
        st.warning(
            "Kết quả không đồng đều: bạn đạt một level cao hơn nhưng chưa đạt level thấp hơn. "
            f"Bài test hiện chỉ có {len(result.answers)} câu nên kết quả có thể chưa chính xác."
        )

    st.subheader("Số câu đúng theo kỹ năng")
    cols = iter(st.columns(len(SKILLS) + len(UNTESTED_SKILLS)))
    for skill in SKILLS:
        next(cols).metric(skill.title(), f"{result.skill_correct.get(skill, 0)}/{result.skill_total.get(skill, 0)}")
    for skill in UNTESTED_SKILLS:
        next(cols).metric(skill.title(), NOT_ASSESSED)
    st.caption(
        f"Mỗi kỹ năng chỉ có khoảng {min(result.skill_total.values())} câu nên chưa đủ để xác định "
        "level riêng cho từng kỹ năng. "
        "Bài test đầy đủ theo kỹ năng sẽ có ở Week 3."
    )

    # Chỉ xem lại đáp án khi kết quả được chấm bằng đúng bộ câu hỏi hiện tại.
    if result.bank_version == bank.bank_version:
        with st.expander("Xem lại đáp án"):
            for number, question in enumerate(bank.questions, start=1):
                chosen = result.answers.get(question.id)
                is_correct = chosen == question.correct_index
                st.markdown(f"**Câu {number}. {question.question}** {'✅' if is_correct else '❌'}")
                if chosen is not None:
                    st.write(f"Bạn chọn: {question.options[chosen]}")
                st.write(f"Đáp án đúng: {question.options[question.correct_index]}")
                st.caption(question.explanation_vi)

    col1, col2, col3 = st.columns(3)
    col1.page_link(Page.LEARNER_PROFILE, label="Xem Learner Profile", icon="👤")
    col2.page_link(Page.YOUTUBE_LEARNING, label="Học với YouTube", icon="▶️")
    if col3.button("Làm lại bài test"):
        st.session_state.pt_retake = True
        for question in bank.questions:
            st.session_state.pop(f"pt_{question.id}", None)
        st.rerun()


page_header("📝 Placement Test", "Đánh giá trình độ tiếng Anh ban đầu theo thang CEFR (A1–B2).")

st.session_state.setdefault("pt_retake", False)

try:
    question_bank = load_question_bank()
    user_id = current_user_id()
    latest_result = get_latest_assessment(user_id) if user_id else st.session_state.get("guest_result")
except Exception as exc:
    st.error(f"Không tải được Placement Test: {exc}")
    st.stop()

if latest_result and not st.session_state.pt_retake:
    show_result(latest_result, question_bank)
else:
    show_test(question_bank)
