from functools import lru_cache

from google import genai
from google.genai import types
from pydantic import ValidationError

from config.settings import GEMINI_TEMPERATURE, settings
from models.schemas import TutorAnalysis
from prompts.tutor_prompt import build_learner_context, build_tutor_prompt
from utils.timing import StageTimer, measure

MISSING_API_KEY_MESSAGE = "Chưa tìm thấy GEMINI_API_KEY. Hãy thêm API Key vào file .env."


@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    return genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(timeout=settings.gemini_timeout_seconds * 1000),
    )


def _build_config() -> types.GenerateContentConfig:
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=TutorAnalysis,
        temperature=GEMINI_TEMPERATURE,
    )
    if settings.gemini_thinking_budget is not None:
        config.thinking_config = types.ThinkingConfig(thinking_budget=settings.gemini_thinking_budget)
    return config


def is_configured() -> bool:
    return bool(settings.gemini_api_key)


def analyze_transcript(
    transcript: str,
    timer: StageTimer | None = None,
    learner_level: str | None = None,
) -> TutorAnalysis:
    if not is_configured():
        raise RuntimeError(MISSING_API_KEY_MESSAGE)
    if not transcript or not transcript.strip():
        raise ValueError("Transcript đang trống.")

    prompt = build_tutor_prompt(build_learner_context(learner_level), transcript)

    try:
        with measure(timer, "Gemini API"):
            response = _get_client().models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=_build_config(),
            )
    except Exception as exc:  # Lỗi mạng, timeout, quota, API key sai...
        raise RuntimeError(f"Không gọi được Gemini: {exc}") from exc

    if timer and response.usage_metadata:
        usage = response.usage_metadata
        timer.info["prompt_tokens"] = usage.prompt_token_count
        timer.info["thinking_tokens"] = usage.thoughts_token_count
        timer.info["output_tokens"] = usage.candidates_token_count

    if not response.text:
        raise RuntimeError("Gemini không trả về nội dung.")

    try:
        with measure(timer, "Validation"):
            return TutorAnalysis.model_validate_json(response.text)
    except ValidationError as exc:
        raise RuntimeError(f"Phản hồi của Gemini không đúng định dạng bài học: {exc}") from exc
