import sqlite3
import unittest
from unittest import mock

from services import assessment_service, database
from services.assessment_service import load_question_bank, score_answers
from services.auth_service import register
from services.profile_service import apply_assessment, get_or_create_profile, get_profile
from tests.helpers import TempDatabaseTestCase


class TestDatabase(TempDatabaseTestCase):
    def test_tables_are_created(self):
        with database.get_connection() as conn:
            tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"accounts", "profiles", "assessments", "lessons"} <= tables)

    def test_error_rolls_back_changes(self):
        register("lan", "matkhau123")
        with self.assertRaises(RuntimeError):
            with database.get_connection() as conn:
                conn.execute("DELETE FROM accounts")
                raise RuntimeError("lỗi giữa chừng")
        self.assertEqual(self.count_rows("accounts"), 1)  # lệnh DELETE đã bị hủy

    def test_nested_calls_share_one_transaction(self):
        # register() mở connection riêng, nhưng nằm trong khối ngoài nên bị rollback cùng.
        with self.assertRaises(RuntimeError):
            with database.get_connection():
                register("lan", "matkhau123")
                raise RuntimeError("lỗi giữa chừng")
        self.assertEqual(self.count_rows("accounts"), 0)

    def test_record_assessment_is_atomic(self):
        register("lan", "matkhau123")
        bank = load_question_bank()
        result = score_answers(bank, {q.id: q.correct_index for q in bank.questions}, "lan")
        with mock.patch.object(assessment_service, "apply_assessment", side_effect=RuntimeError("lỗi")):
            with self.assertRaises(RuntimeError):
                assessment_service.record_assessment(result)
        self.assertEqual(self.count_rows("assessments"), 0)

    def test_profile_must_belong_to_an_account(self):
        # Khóa ngoại: không tạo được profile cho tài khoản không tồn tại.
        with self.assertRaises(sqlite3.IntegrityError):
            get_or_create_profile("nobody")


class TestLearnerProfile(TempDatabaseTestCase):
    def setUp(self):
        super().setUp()
        register("lan", "matkhau123")

    def test_no_profile_before_start(self):
        self.assertIsNone(get_profile("lan"))

    def test_new_profile_is_not_assessed(self):
        profile = get_or_create_profile("lan")
        self.assertIsNone(profile.current_level)
        for skill in [profile.grammar, profile.vocabulary, profile.reading, profile.listening]:
            self.assertIsNone(skill.level)

    def test_profile_is_not_duplicated(self):
        get_or_create_profile("lan")
        get_or_create_profile("lan")
        self.assertEqual(self.count_rows("profiles"), 1)

    def test_apply_assessment_updates_only_overall_level(self):
        bank = load_question_bank()
        all_correct = {q.id: q.correct_index for q in bank.questions}
        result = score_answers(bank, all_correct, "lan")

        profile = apply_assessment(result)

        self.assertEqual(profile.current_level, "B2")
        self.assertEqual(profile.latest_assessment_id, result.assessment_id)
        # Không tự gán level cho từng kỹ năng.
        self.assertIsNone(profile.grammar.level)
        self.assertIsNone(profile.listening.level)
        self.assertEqual(get_profile("lan").current_level, "B2")


if __name__ == "__main__":
    unittest.main()
