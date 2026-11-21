import json
import unittest
from types import SimpleNamespace
from unittest import mock

from services import gemini_service
from tests.test_schemas import make_analysis


def fake_client(text: str | None):
    response = SimpleNamespace(text=text, usage_metadata=None)
    return SimpleNamespace(models=SimpleNamespace(generate_content=mock.Mock(return_value=response)))


class TestAnalyzeTranscript(unittest.TestCase):
    def setUp(self):
        patches = [mock.patch.object(gemini_service, "is_configured", return_value=True)]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def analyze_with_response(self, text):
        with mock.patch.object(gemini_service, "_get_client", return_value=fake_client(text)):
            return gemini_service.analyze_transcript("Hello world.")

    def test_valid_response(self):
        analysis = self.analyze_with_response(json.dumps(make_analysis()))
        self.assertEqual(len(analysis.quiz), 5)

    def test_empty_response_message_is_not_wrapped_twice(self):
        with self.assertRaises(RuntimeError) as ctx:
            self.analyze_with_response("")
        self.assertEqual(str(ctx.exception), "Gemini không trả về nội dung.")

    def test_invalid_json_shape(self):
        with self.assertRaises(RuntimeError) as ctx:
            self.analyze_with_response(json.dumps({"summary": {}}))
        self.assertIn("không đúng định dạng", str(ctx.exception))

    def test_api_error(self):
        client = fake_client(None)
        client.models.generate_content.side_effect = TimeoutError("timeout")
        with mock.patch.object(gemini_service, "_get_client", return_value=client):
            with self.assertRaises(RuntimeError) as ctx:
                gemini_service.analyze_transcript("Hello world.")
        self.assertIn("Không gọi được Gemini", str(ctx.exception))

    def test_missing_api_key(self):
        with mock.patch.object(gemini_service, "is_configured", return_value=False):
            with self.assertRaises(RuntimeError) as ctx:
                gemini_service.analyze_transcript("Hello world.")
        self.assertEqual(str(ctx.exception), gemini_service.MISSING_API_KEY_MESSAGE)


if __name__ == "__main__":
    unittest.main()
