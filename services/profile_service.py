from models.assessment import AssessmentResult
from models.learner import LearnerProfile
from services.database import fetch_one, get_connection, upsert
from utils.clock import now


def profile_row(profile: LearnerProfile) -> dict:
    return {
        "user_id": profile.user_id,
        "current_level": profile.current_level,
        "profile_json": profile.model_dump_json(),
        "updated_at": profile.updated_at.isoformat(),
    }


def get_profile(user_id: str) -> LearnerProfile | None:
    row = fetch_one("SELECT profile_json FROM profiles WHERE user_id = ?", (user_id,))
    return LearnerProfile.model_validate_json(row["profile_json"]) if row else None


def get_or_create_profile(user_id: str) -> LearnerProfile:
    with get_connection():
        profile = get_profile(user_id)
        if profile is None:
            created_at = now()
            profile = LearnerProfile(user_id=user_id, created_at=created_at, updated_at=created_at)
            save_profile(profile)
        return profile


def save_profile(profile: LearnerProfile) -> None:
    upsert("profiles", profile_row(profile), keys=("user_id",))


def apply_assessment(result: AssessmentResult) -> LearnerProfile:
    """Chỉ cập nhật trình độ tổng: số câu mỗi kỹ năng còn ít, chưa đủ để xác định level từng kỹ năng."""
    with get_connection():
        profile = get_or_create_profile(result.user_id)
        profile.current_level = result.overall_level
        profile.latest_assessment_id = result.assessment_id
        profile.updated_at = now()
        save_profile(profile)
        return profile
