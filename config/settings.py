import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _optional_int(name: str) -> int | None:
    value = os.getenv(name, "").strip()
    return int(value) if value else None


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    gemini_timeout_seconds: int = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "180"))
    # Để trống = dùng mặc định của model.
    gemini_thinking_budget: int | None = _optional_int("GEMINI_THINKING_BUDGET")


settings = Settings()

# App
APP_NAME = "AI English Learning Assistant"
APP_TAGLINE = "Your Personal English Tutor"
APP_ICON = "🎓"

# Storage
DB_PATH = PROJECT_ROOT / "data" / "app.db"
DB_TIMEOUT_SECONDS = 10
QUESTION_BANK_PATH = PROJECT_ROOT / "content" / "placement_questions.json"

# Auth
HASH_ITERATIONS = 600_000
SALT_BYTES = 16
MIN_PASSWORD_LENGTH = 8
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20

# Placement Test
MIN_CORRECT_TO_PASS = 2
GUEST_ID = "guest"

# Lesson generation
DEFAULT_LEVEL = "A2"
GEMINI_TEMPERATURE = 0.2
# Chỉ lấy phụ đề tiếng Anh: prompt yêu cầu trích câu tiếng Anh có thật trong transcript.
TRANSCRIPT_LANGUAGES = ["en", "en-US", "en-GB"]
QUIZ_COUNT = 5
KEY_SENTENCE_COUNT = 5
VOCABULARY_MIN = 5
VOCABULARY_MAX = 10
QUIZ_OPTION_COUNT = 4

# YouTube Learning page
CACHE_TTL_SECONDS = 6 * 60 * 60
ANALYSIS_CACHE_MAX_ENTRIES = 100
LONG_TRANSCRIPT_CHARS = 60_000
