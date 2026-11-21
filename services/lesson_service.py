from datetime import datetime

from models.schemas import LessonSummary, TutorAnalysis
from services.database import fetch_all, fetch_one, upsert
from utils.clock import now


def save_lesson(
    user_id: str,
    video_id: str,
    video_url: str,
    learner_level: str,
    prompt_version: str,
    analysis: TutorAnalysis,
) -> None:
    """Cùng người + video + level -> ghi đè bằng bài mới nhất."""
    row = {
        "user_id": user_id,
        "video_id": video_id,
        "video_url": video_url,
        "learner_level": learner_level,
        "prompt_version": prompt_version,
        "analysis_json": analysis.model_dump_json(),
        "created_at": now().isoformat(),
    }
    upsert("lessons", row, keys=("user_id", "video_id", "learner_level"))


def list_lessons(user_id: str) -> list[LessonSummary]:
    rows = fetch_all(
        "SELECT lesson_id, video_id, video_url, learner_level, created_at FROM lessons "
        "WHERE user_id = ? ORDER BY created_at DESC, lesson_id DESC",
        (user_id,),
    )
    return [
        LessonSummary(**{**dict(row), "created_at": datetime.fromisoformat(row["created_at"])})
        for row in rows
    ]


def count_lessons(user_id: str) -> int:
    return fetch_one("SELECT COUNT(*) FROM lessons WHERE user_id = ?", (user_id,))[0]


def get_lesson(user_id: str, lesson_id: int) -> TutorAnalysis | None:
    # Lọc theo user_id để không mở được bài học của người khác.
    row = fetch_one(
        "SELECT analysis_json FROM lessons WHERE user_id = ? AND lesson_id = ?",
        (user_id, lesson_id),
    )
    return TutorAnalysis.model_validate_json(row["analysis_json"]) if row else None
