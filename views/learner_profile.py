import streamlit as st

from models.learner import SKILL_FIELDS
from services.profile_service import get_or_create_profile
from services.session_service import current_user_id
from utils.ui import DATETIME_FORMAT, NOT_ASSESSED, Page, level_text, login_link, page_header

page_header("👤 Learner Profile", "Hồ sơ học tập dùng để cá nhân hóa bài học.")

user_id = current_user_id()
if not user_id:
    st.info("🔐 Vui lòng đăng nhập để xem hồ sơ học tập của bạn.")
    login_link()
    st.stop()

profile = get_or_create_profile(user_id)

if profile.current_level is None:
    st.info(f"Bạn chưa làm Placement Test, nên trình độ đang là \"{NOT_ASSESSED}\".")
    st.page_link(Page.PLACEMENT_TEST, label="Làm Placement Test", icon="📝")

col1, col2 = st.columns(2)

with col1.container(border=True):
    st.markdown("### Thông tin chung")
    st.write(f"**User ID:** `{profile.user_id}`")
    st.write(f"**Native language:** {profile.native_language}")
    st.write(f"**Current English level:** {level_text(profile.current_level)}")
    st.write(f"**Learning goal:** {profile.learning_goal or 'Chưa thiết lập'}")
    preferences = ", ".join(f"{k}: {v}" for k, v in profile.learning_preferences.items())
    st.write(f"**Learning preferences:** {preferences or 'Chưa thiết lập'}")

with col2.container(border=True):
    st.markdown("### Trình độ theo kỹ năng")
    for skill in SKILL_FIELDS:
        st.write(f"**{skill.title()}:** {level_text(getattr(profile, skill).level)}")
    st.caption(
        f"\"{NOT_ASSESSED}\" nghĩa là kỹ năng chưa có bài đánh giá riêng. "
        "Hệ thống không tự gán level khi chưa có dữ liệu."
    )

st.caption(f"Cập nhật lần cuối: {profile.updated_at:{DATETIME_FORMAT}}")
st.info("🚧 Chỉnh sửa mục tiêu học tập và sở thích học sẽ có ở Week 3.")
