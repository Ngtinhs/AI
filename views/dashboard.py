import streamlit as st

from config.settings import APP_NAME, APP_TAGLINE
from services.lesson_service import count_lessons
from services.session_service import current_level, current_user_id
from utils.ui import LOGIN_TO_SAVE_LABEL, Page, level_text, login_link, page_header

page_header("🏠 Dashboard", f"Chào mừng bạn đến với {APP_NAME} – {APP_TAGLINE}.")

user_id = current_user_id()
level = current_level()

if level is None:
    with st.container(border=True):
        st.markdown("### 👋 Bắt đầu từ đây")
        st.write("Hãy làm **Placement Test** ngắn để hệ thống biết trình độ hiện tại của bạn.")
        st.page_link(Page.PLACEMENT_TEST, label="Làm Placement Test ngay", icon="📝")
elif not user_id:
    st.warning("Bạn đã làm Placement Test nhưng chưa đăng nhập, nên kết quả chưa được lưu.")
    login_link(LOGIN_TO_SAVE_LABEL)

# "—": chức năng chưa có dữ liệu, không phải số 0.
col1, col2, col3, col4 = st.columns(4)
with col1.container(border=True):
    st.metric("Trình độ hiện tại", level_text(level))
with col2.container(border=True):
    if user_id:
        st.metric("Bài học đã lưu", count_lessons(user_id))
        st.page_link(Page.PROGRESS, label="Xem danh sách")
    else:
        st.metric("Bài học đã lưu", "—")
        st.caption("Đăng nhập để lưu bài học")
with col3.container(border=True):
    st.metric("Từ vựng đã lưu", "—")
    st.caption("Có từ Week 4")
with col4.container(border=True):
    st.metric("Kết quả Quiz", "—")
    st.caption("Có từ Week 5")

st.subheader("Truy cập nhanh")
QUICK_LINKS = [
    ("**📝 Placement Test**", "Đánh giá trình độ A1–B2.", Page.PLACEMENT_TEST),
    ("**▶️ YouTube Learning**", "Tạo bài học từ video YouTube.", Page.YOUTUBE_LEARNING),
    ("**👤 Learner Profile**", "Xem hồ sơ học tập của bạn.", Page.LEARNER_PROFILE),
]
for col, (title, caption, page) in zip(st.columns(len(QUICK_LINKS)), QUICK_LINKS):
    with col.container(border=True):
        st.markdown(title)
        st.caption(caption)
        st.page_link(page, label="Mở")
