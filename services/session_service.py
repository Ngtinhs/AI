"""
Trạng thái phiên Streamlit:
- `user_id` (None = khách) và `guest_result` (kết quả test chưa lưu của khách).
- `analysis`, `video_url`, `lesson_level`, `lesson_key`, `timings`: bài học đang hiển thị ở YouTube Learning.
Các trang đọc/ghi những key này qua module này thay vì tự đặt tên key.
"""

import uuid

import streamlit as st

from models.schemas import TutorAnalysis
from services.assessment_service import record_assessment
from services.profile_service import get_or_create_profile, get_profile


def current_user_id() -> str | None:
    return st.session_state.get("user_id")


def current_level() -> str | None:
    """Đã đăng nhập -> level trong Learner Profile; khách -> level của bài test trong phiên."""
    user_id = current_user_id()
    if user_id:
        profile = get_profile(user_id)
        return profile.current_level if profile else None

    guest_result = st.session_state.get("guest_result")
    return guest_result.overall_level if guest_result else None


def login(user_id: str) -> bool:
    """Trả về True nếu kết quả test của khách được lưu vào tài khoản."""
    st.session_state.user_id = user_id
    get_or_create_profile(user_id)

    guest_result = st.session_state.pop("guest_result", None)
    if guest_result is None:
        return False

    record_assessment(guest_result.model_copy(update={"user_id": user_id}))
    return True


def show_lesson(analysis: TutorAnalysis, video_url: str, level: str, timings: dict | None = None) -> None:
    """Chọn bài học hiển thị ở trang YouTube Learning. `lesson_key` mới giúp Quiz không giữ đáp án của bài cũ."""
    st.session_state.analysis = analysis
    st.session_state.video_url = video_url
    st.session_state.lesson_level = level
    st.session_state.lesson_key = uuid.uuid4().hex
    st.session_state.timings = timings


def clear_lesson() -> None:
    st.session_state.analysis = None
    st.session_state.timings = None


def logout() -> None:
    """Xóa toàn bộ trạng thái phiên (bài học, đáp án đang chọn...) để người sau không thấy dữ liệu cũ."""
    st.session_state.clear()
