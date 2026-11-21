import streamlit as st

NOT_ASSESSED = "Not assessed yet"
LOGIN_LABEL = "Đăng nhập / Đăng ký"
LOGIN_TO_SAVE_LABEL = f"{LOGIN_LABEL} để lưu kết quả"
DATETIME_FORMAT = "%d/%m/%Y %H:%M"


class Page:
    DASHBOARD = "views/dashboard.py"
    PLACEMENT_TEST = "views/placement_test.py"
    LEARNER_PROFILE = "views/learner_profile.py"
    YOUTUBE_LEARNING = "views/youtube_learning.py"
    AI_TUTOR = "views/ai_tutor.py"
    VOCABULARY = "views/vocabulary.py"
    PROGRESS = "views/progress.py"
    LOGIN = "views/login.py"


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def level_text(level: str | None) -> str:
    return level or NOT_ASSESSED


def option_label(options: list[str]):
    """format_func cho st.radio: 0 -> "A. <đáp án>"."""
    return lambda i: f"{chr(65 + i)}. {options[i]}"


def login_link(label: str = LOGIN_LABEL, container=st) -> None:
    container.page_link(Page.LOGIN, label=label, icon="🔐")


def coming_soon(feature_name: str, week: str, planned_features: list[str]) -> None:
    with st.container(border=True):
        st.info(f"🚧 **{feature_name}** chưa khả dụng. Dự kiến triển khai ở **{week}**.")
        st.markdown("**Chức năng sẽ có:**")
        for item in planned_features:
            st.markdown(f"- {item}")
