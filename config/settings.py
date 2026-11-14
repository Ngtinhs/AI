import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Đọc biến môi trường từ file .env ở thư mục gốc project.
load_dotenv()


@dataclass
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


settings = Settings()
