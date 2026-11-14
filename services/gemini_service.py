from google import genai
from google.genai import types

from config.settings import settings
from models.schemas import TutorAnalysis
from prompts.tutor_prompt import LEARNER_CONTEXT, build_tutor_prompt


def analyze_transcript(transcript: str) -> TutorAnalysis:
    """Gửi Context + Prompt + Transcript đến Gemini và kiểm tra kết quả."""
    if not settings.gemini_api_key:
        raise RuntimeError("Thiếu GEMINI_API_KEY trong file .env.")

    if not transcript or not transcript.strip():
        raise ValueError("Transcript đang trống.")

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = build_tutor_prompt(LEARNER_CONTEXT, transcript)

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TutorAnalysis,
                temperature=0.2,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini không trả về nội dung.")

        # Parse JSON và xác thực kiểu dữ liệu bằng Pydantic.
        return TutorAnalysis.model_validate_json(response.text)

    except Exception as exc:
        raise RuntimeError(f"Lỗi khi gọi hoặc xử lý phản hồi Gemini: {exc}") from exc
