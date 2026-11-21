import json
import unittest

from pydantic import ValidationError

from models.schemas import TutorAnalysis


def make_analysis(vocab_count=5, sentence_count=5, quiz_count=5) -> dict:
    return {
        "summary": {"english": "A short summary.", "vietnamese": "Tóm tắt ngắn."},
        "vocabulary": [
            {"word": f"word{i}", "ipa": "", "meaning_vi": "nghĩa", "example": "Ex.", "example_vi": "Vd."}
            for i in range(vocab_count)
        ],
        "key_sentences": [
            {"english": "Sentence.", "vietnamese": "Câu.", "usage_vi": "Cách dùng."}
            for _ in range(sentence_count)
        ],
        "quiz": [
            {"question": "Q?", "options": ["a", "b", "c", "d"], "correct_index": 0, "explanation_vi": "Vì..."}
            for _ in range(quiz_count)
        ],
    }


class TestTutorAnalysisSchema(unittest.TestCase):  # TC026
    def test_valid_json(self):
        result = TutorAnalysis.model_validate_json(json.dumps(make_analysis()))
        self.assertEqual(len(result.quiz), 5)

    def test_too_many_vocabulary_items(self):
        with self.assertRaises(ValidationError):
            TutorAnalysis.model_validate(make_analysis(vocab_count=11))

    def test_wrong_quiz_count(self):
        with self.assertRaises(ValidationError):
            TutorAnalysis.model_validate(make_analysis(quiz_count=4))

    def test_quiz_needs_four_options(self):
        data = make_analysis()
        data["quiz"][0]["options"] = ["a", "b", "c"]
        with self.assertRaises(ValidationError):
            TutorAnalysis.model_validate(data)

    def test_missing_field(self):
        data = make_analysis()
        del data["summary"]
        with self.assertRaises(ValidationError):
            TutorAnalysis.model_validate(data)


if __name__ == "__main__":
    unittest.main()
