import streamlit as st

from config.settings import MIN_PASSWORD_LENGTH, USERNAME_MAX_LENGTH, USERNAME_MIN_LENGTH
from services.auth_service import authenticate, register
from services.session_service import current_user_id, login, logout
from utils.ui import LOGIN_LABEL, Page, page_header


def finish_login(user_id: str) -> None:
    message = f"Xin chào **{user_id}**! Bạn đã đăng nhập."
    if login(user_id):
        message += " Kết quả Placement Test vừa làm đã được lưu vào tài khoản."
    st.session_state.flash = message
    st.rerun()


user_id = current_user_id()

if user_id:
    page_header("👤 Tài khoản", "Thông tin tài khoản của bạn.")
else:
    page_header(f"🔐 {LOGIN_LABEL}", "Đăng nhập để lưu kết quả Placement Test và hồ sơ học tập.")

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

if user_id:
    st.write(f"Bạn đang đăng nhập với tên **{user_id}**.")
    col1, col2 = st.columns(2)
    col1.page_link(Page.LEARNER_PROFILE, label="Xem Learner Profile", icon="👤")
    if col2.button("Đăng xuất"):
        logout()
        st.rerun()
    st.stop()

if st.session_state.get("guest_result"):
    st.info("Bạn đã làm Placement Test. Đăng nhập hoặc đăng ký để **lưu kết quả** này.")

login_tab, register_tab = st.tabs(["Đăng nhập", "Đăng ký"])

with login_tab:
    with st.form("login_form"):
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập", type="primary")

    if submitted:
        found_user = authenticate(username, password)
        if found_user:
            finish_login(found_user)
        else:
            # Không tiết lộ sai tên hay sai mật khẩu.
            st.error("Sai tên đăng nhập hoặc mật khẩu.")

with register_tab:
    with st.form("register_form"):
        new_username = st.text_input(
            "Tên đăng nhập",
            help=f"{USERNAME_MIN_LENGTH}–{USERNAME_MAX_LENGTH} ký tự: chữ thường, số, dấu _",
        )
        new_password = st.text_input("Mật khẩu", type="password", help=f"Ít nhất {MIN_PASSWORD_LENGTH} ký tự")
        confirm_password = st.text_input("Nhập lại mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng ký", type="primary")

    if submitted:
        if new_password != confirm_password:
            st.error("Mật khẩu nhập lại không khớp.")
        else:
            try:
                finish_login(register(new_username, new_password))
            except ValueError as exc:
                st.error(str(exc))
