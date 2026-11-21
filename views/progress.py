import streamlit as st

from services.lesson_service import get_lesson, list_lessons
from services.session_service import current_user_id, show_lesson
from utils.ui import DATETIME_FORMAT, Page, coming_soon, login_link, page_header

page_header("📈 Progress", "Theo dõi tiến bộ học tập.")

st.subheader("📚 Bài học của tôi")
user_id = current_user_id()

if not user_id:
    st.info("🔐 Đăng nhập để lưu và xem lại các bài học YouTube của bạn.")
    login_link()
else:
    lessons = list_lessons(user_id)
    if not lessons:
        st.write("Bạn chưa có bài học nào. Hãy phân tích một video để bắt đầu.")
        st.page_link(Page.YOUTUBE_LEARNING, label="Mở YouTube Learning", icon="▶️")

    for lesson in lessons:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"**{lesson.video_url}**")
            col1.caption(f"Trình độ: {lesson.learner_level} · Tạo lúc: {lesson.created_at:{DATETIME_FORMAT}}")
            if col2.button("Mở lại", key=f"open_lesson_{lesson.lesson_id}"):
                analysis = get_lesson(user_id, lesson.lesson_id)
                if analysis:
                    show_lesson(analysis, lesson.video_url, lesson.learner_level)
                    st.switch_page(Page.YOUTUBE_LEARNING)

coming_soon(
    "Thống kê tiến bộ",
    "Week 5",
    [
        "Thống kê kết quả Quiz và từ vựng.",
        "Phân loại bài học theo chủ đề (category).",
        "Phân tích kỹ năng còn yếu.",
        "Gợi ý nội dung học tiếp theo.",
        "Đánh giá lại trình độ.",
    ],
)
