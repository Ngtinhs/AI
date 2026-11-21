import unittest

from services.auth_service import register
from services.lesson_service import count_lessons, get_lesson, list_lessons, save_lesson
from tests.helpers import TempDatabaseTestCase
from tests.test_schemas import make_analysis
from models.schemas import TutorAnalysis

VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def sample_analysis(summary: str = "A short summary.") -> TutorAnalysis:
    data = make_analysis()
    data["summary"]["english"] = summary
    return TutorAnalysis.model_validate(data)


class TestLessonService(TempDatabaseTestCase):
    def setUp(self):
        super().setUp()
        register("lan", "matkhau123")
        register("minh", "matkhau123")

    def save(self, user="lan", video="dQw4w9WgXcQ", level="A2", summary="A short summary."):
        save_lesson(user, video, VIDEO_URL, level, "test-v1", sample_analysis(summary))

    def test_no_lessons_at_start(self):
        self.assertEqual(list_lessons("lan"), [])
        self.assertEqual(count_lessons("lan"), 0)

    def test_save_and_read_back(self):
        self.save()
        lessons = list_lessons("lan")
        self.assertEqual(len(lessons), 1)
        analysis = get_lesson("lan", lessons[0].lesson_id)
        self.assertEqual(analysis.summary.english, "A short summary.")

    def test_same_video_same_level_is_updated_not_duplicated(self):
        self.save(summary="Old")
        self.save(summary="New")
        lessons = list_lessons("lan")
        self.assertEqual(len(lessons), 1)
        self.assertEqual(get_lesson("lan", lessons[0].lesson_id).summary.english, "New")

    def test_same_video_different_level_is_a_new_lesson(self):
        self.save(level="A2")
        self.save(level="B1")
        self.assertEqual(count_lessons("lan"), 2)

    def test_user_cannot_open_other_users_lesson(self):
        self.save(user="lan")
        lesson_id = list_lessons("lan")[0].lesson_id
        self.assertIsNone(get_lesson("minh", lesson_id))
        self.assertEqual(list_lessons("minh"), [])


if __name__ == "__main__":
    unittest.main()
