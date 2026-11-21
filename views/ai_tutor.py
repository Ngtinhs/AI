import streamlit as st

from utils.ui import Page, coming_soon, page_header

page_header("🤖 AI Tutor", "Gia sư AI giải thích bài học theo trình độ của bạn.")

st.write("Hiện tại, Summary, Vocabulary, Key Sentences và Quiz đã có trong trang **YouTube Learning**.")
st.page_link(Page.YOUTUBE_LEARNING, label="Mở YouTube Learning", icon="▶️")

coming_soon(
    "AI Tutor cá nhân hóa",
    "Week 4",
    [
        "Giải thích từ vựng và đáp án chi tiết hơn theo trình độ của bạn.",
        "Dùng thêm mục tiêu học tập và sở thích trong Learner Profile.",
        "Phân loại từ vựng: Review, Target, Challenge.",
    ],
)
