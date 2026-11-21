import unittest

from models.assessment import TEST_LEVELS
from services.assessment_service import get_latest_assessment, load_question_bank, save_assessment, score_answers
from services.auth_service import register
from tests.helpers import TempDatabaseTestCase


def answers_for(bank, correct_ids: set[str]) -> dict[str, int]:
    """Tạo bộ đáp án: câu nằm trong correct_ids thì trả lời đúng, còn lại trả lời sai."""
    return {
        q.id: q.correct_index if q.id in correct_ids else (q.correct_index + 1) % 4
        for q in bank.questions
    }


class TestQuestionBank(unittest.TestCase):
    def test_bank_has_12_questions(self):
        bank = load_question_bank()
        self.assertEqual(len(bank.questions), 12)

    def test_each_level_has_one_question_per_skill(self):
        bank = load_question_bank()
        for level in TEST_LEVELS:
            skills = sorted(q.skill for q in bank.questions if q.level == level)
            self.assertEqual(skills, ["grammar", "reading", "vocabulary"], level)

    def test_reading_questions_have_passage(self):
        bank = load_question_bank()
        for q in bank.questions:
            if q.skill == "reading":
                self.assertTrue(q.passage, q.id)


class TestScoring(unittest.TestCase):
    def setUp(self):
        self.bank = load_question_bank()
        self.ids_by_level = {
            level: [q.id for q in self.bank.questions if q.level == level] for level in TEST_LEVELS
        }

    def score(self, correct_ids):
        return score_answers(self.bank, answers_for(self.bank, set(correct_ids)), "test_user")

    def test_all_correct_is_b2(self):
        result = self.score(q.id for q in self.bank.questions)
        self.assertEqual(result.overall_level, "B2")
        self.assertFalse(result.inconsistent)

    def test_all_wrong_is_below_a1(self):
        result = self.score([])
        self.assertEqual(result.overall_level, "Below A1")

    def test_one_of_three_at_a1_is_below_a1(self):
        result = self.score(self.ids_by_level["A1"][:1])
        self.assertEqual(result.overall_level, "Below A1")

    def test_two_of_three_at_a1_is_a1(self):
        result = self.score(self.ids_by_level["A1"][:2])
        self.assertEqual(result.overall_level, "A1")

    def test_pass_a1_a2_fail_b1_is_a2(self):
        result = self.score(self.ids_by_level["A1"] + self.ids_by_level["A2"])
        self.assertEqual(result.overall_level, "A2")
        self.assertFalse(result.inconsistent)

    def test_skip_level_is_flagged_inconsistent(self):
        # Đạt A1, trượt A2, đạt B1 -> vẫn là A1 nhưng bị đánh dấu không đồng đều.
        result = self.score(self.ids_by_level["A1"] + self.ids_by_level["B1"])
        self.assertEqual(result.overall_level, "A1")
        self.assertTrue(result.inconsistent)

    def test_fail_a1_but_pass_b2_is_flagged(self):
        result = self.score(self.ids_by_level["B2"])
        self.assertEqual(result.overall_level, "Below A1")
        self.assertTrue(result.inconsistent)

    def test_skill_counts(self):
        grammar_ids = [q.id for q in self.bank.questions if q.skill == "grammar"]
        result = self.score(grammar_ids)
        self.assertEqual(result.skill_correct, {"grammar": 4, "vocabulary": 0, "reading": 0})
        self.assertEqual(result.skill_total, {"grammar": 4, "vocabulary": 4, "reading": 4})

    def test_missing_answer_is_rejected(self):
        answers = answers_for(self.bank, set())
        answers[self.bank.questions[0].id] = None
        with self.assertRaises(ValueError):
            score_answers(self.bank, answers, "test_user")


class TestSaveAssessment(TempDatabaseTestCase):
    def setUp(self):
        super().setUp()
        register("test_user", "matkhau123")
        register("other_user", "matkhau123")

    def test_no_result_before_taking_test(self):
        self.assertIsNone(get_latest_assessment("test_user"))

    def test_save_and_get_latest(self):
        bank = load_question_bank()
        first = score_answers(bank, answers_for(bank, set()), "test_user")
        second = score_answers(bank, answers_for(bank, {q.id for q in bank.questions}), "test_user")
        save_assessment(first)
        save_assessment(second)

        latest = get_latest_assessment("test_user")
        self.assertEqual(latest.assessment_id, second.assessment_id)
        self.assertEqual(latest.overall_level, "B2")
        self.assertIsNone(get_latest_assessment("other_user"))

    def test_old_results_are_kept(self):
        bank = load_question_bank()
        for _ in range(3):
            save_assessment(score_answers(bank, answers_for(bank, set()), "test_user"))
        self.assertEqual(self.count_rows("assessments"), 3)


if __name__ == "__main__":
    unittest.main()
