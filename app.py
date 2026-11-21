import streamlit as st

from config.settings import APP_ICON, APP_NAME, APP_TAGLINE
from services.session_service import current_level, current_user_id, logout
from utils.ui import LOGIN_LABEL, Page, level_text

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="wide")

user_id = current_user_id()
if user_id:
    account_page = st.Page(Page.LOGIN, title=f"Tài khoản ({user_id})", icon="👤")
else:
    account_page = st.Page(Page.LOGIN, title=LOGIN_LABEL, icon="🔐")

navigation = st.navigation(
    {
        "Overview": [
            st.Page(Page.DASHBOARD, title="Dashboard", icon="🏠", default=True),
        ],
        "Assessment": [
            st.Page(Page.PLACEMENT_TEST, title="Placement Test", icon="📝"),
            st.Page(Page.LEARNER_PROFILE, title="Learner Profile", icon="👤"),
        ],
        "Learn": [
            st.Page(Page.YOUTUBE_LEARNING, title="YouTube Learning", icon="▶️"),
            st.Page(Page.AI_TUTOR, title="AI Tutor", icon="🤖"),
            st.Page(Page.VOCABULARY, title="Vocabulary", icon="📚"),
            st.Page(Page.PROGRESS, title="Progress", icon="📈"),
        ],
        "Account": [account_page],
    }
)

with st.sidebar:
    st.markdown(f"### {APP_ICON} {APP_NAME}")
    st.caption(APP_TAGLINE)
    st.write(f"👤 **{user_id}**" if user_id else "👤 Khách (chưa đăng nhập)")
    st.metric("Your level", level_text(current_level()))
    if user_id and st.button("Đăng xuất", use_container_width=True):
        logout()
        st.rerun()

navigation.run()
