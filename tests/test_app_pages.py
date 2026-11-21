"""
Test giao diện bằng Streamlit AppTest (chạy app thật nhưng không cần mở trình duyệt).
Cần cài streamlit; nếu chưa cài thì các test này được bỏ qua.
Không gọi YouTube/Gemini.
"""

import unittest

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None

from config.settings import PROJECT_ROOT
from services import auth_service
from services.assessment_service import get_latest_assessment, load_question_bank
from services.lesson_service import save_lesson
from services.profile_service import get_profile
from tests.helpers import TempDatabaseTestCase
from tests.test_lesson_service import VIDEO_URL, sample_analysis

PAGES = [
    "views/dashboard.py",
    "views/placement_test.py",
    "views/learner_profile.py",
    "views/youtube_learning.py",
    "views/ai_tutor.py",
    "views/vocabulary.py",
    "views/progress.py",
    "views/login.py",
]


@unittest.skipIf(AppTest is None, "streamlit chưa được cài")
class TestAppPages(TempDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.app = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
        self.app.run()

    def open_page(self, page):
        self.app.switch_page(page)
        self.app.run()
        self.assertFalse(self.app.exception, f"{page}: {self.app.exception}")

    def answer_all_correct(self):
        for question in load_question_bank().questions:
            self.app.radio(key=f"pt_{question.id}").set_value(question.correct_index)
        self.app.button[0].click()  # nút "Nộp bài" (form_submit_button)
        self.app.run()

    def test_all_pages_open_as_guest(self):
        for page in PAGES:
            self.open_page(page)

    def test_profile_requires_login(self):
        self.open_page("views/learner_profile.py")
        self.assertIn("đăng nhập", self.app.info[0].value.lower())

    def test_guest_can_take_test_but_result_is_not_saved(self):
        self.open_page("views/placement_test.py")
        self.answer_all_correct()

        self.assertEqual(self.app.session_state["guest_result"].overall_level, "B2")
        self.assertIn("chưa được lưu", self.app.warning[0].value)
        self.assertEqual(self.count_rows("assessments"), 0)

    def test_guest_result_is_saved_after_register(self):
        self.open_page("views/placement_test.py")
        self.answer_all_correct()

        self.open_page("views/login.py")
        self.app.text_input[2].input("lan")  # tab Đăng ký: tên đăng nhập
        self.app.text_input[3].input("matkhau123")
        self.app.text_input[4].input("matkhau123")
        self.app.button[1].click()  # nút "Đăng ký"
        self.app.run()

        self.assertEqual(self.app.session_state["user_id"], "lan")
        self.assertEqual(get_profile("lan").current_level, "B2")
        self.assertEqual(get_latest_assessment("lan").user_id, "lan")

    def test_logged_in_user_result_is_saved(self):
        auth_service.register("minh", "matkhau123")
        self.app.session_state["user_id"] = "minh"
        self.open_page("views/placement_test.py")
        self.answer_all_correct()

        self.assertEqual(get_profile("minh").current_level, "B2")

    def test_progress_asks_guest_to_login(self):
        self.open_page("views/progress.py")
        self.assertIn("đăng nhập", self.app.info[0].value.lower())

    def test_progress_lists_saved_lessons(self):
        auth_service.register("minh", "matkhau123")
        save_lesson("minh", "dQw4w9WgXcQ", VIDEO_URL, "B1", "test-v1", sample_analysis())
        self.app.session_state["user_id"] = "minh"
        self.open_page("views/progress.py")

        page_text = " ".join(m.value for m in self.app.markdown)
        self.assertIn(VIDEO_URL, page_text)
        self.assertTrue(any(b.label == "Mở lại" for b in self.app.button))

    def open_quiz(self, lesson_key="lesson-1"):
        self.app.session_state["analysis"] = sample_analysis()
        self.app.session_state["video_url"] = VIDEO_URL
        self.app.session_state["lesson_level"] = "B1"
        self.app.session_state["lesson_key"] = lesson_key
        self.open_page("views/youtube_learning.py")

    def click(self, label):
        next(b for b in self.app.button if b.label == label).click()
        self.app.run()

    def test_quiz_has_no_preselected_answer(self):
        self.open_quiz()
        self.click("Check my answers")
        self.assertIn("chưa trả lời", self.app.warning[-1].value)

    def test_quiz_scores_when_all_answered(self):
        self.open_quiz()
        for question_radio in self.app.radio:
            question_radio.set_value(0)  # sample_analysis: đáp án đúng luôn là 0
        self.click("Check my answers")
        self.assertIn("5/5", self.app.success[-1].value)

    def test_logout_clears_session(self):
        self.app.session_state["user_id"] = "minh"
        self.open_page("views/login.py")
        self.app.button[-1].click()  # "Đăng xuất" trong trang tài khoản
        self.app.run()
        self.assertNotIn("user_id", self.app.session_state)


if __name__ == "__main__":
    unittest.main()
