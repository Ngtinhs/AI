from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from models.assessment import SKILLS, ResultLevel

# Kỹ năng chưa có trong Placement Test.
UNTESTED_SKILLS = ["listening"]
# Phải khớp với các field SkillAssessment của LearnerProfile bên dưới.
SKILL_FIELDS = [*SKILLS, *UNTESTED_SKILLS]


class SkillAssessment(BaseModel):
    # level = None: chưa đánh giá, không tự gán khi chưa có dữ liệu.
    level: ResultLevel | None = None
    source: Literal["placement_test"] | None = None
    assessed_at: datetime | None = None


class LearnerProfile(BaseModel):
    user_id: str
    native_language: str = "Vietnamese"
    current_level: ResultLevel | None = None
    grammar: SkillAssessment = Field(default_factory=SkillAssessment)
    vocabulary: SkillAssessment = Field(default_factory=SkillAssessment)
    reading: SkillAssessment = Field(default_factory=SkillAssessment)
    listening: SkillAssessment = Field(default_factory=SkillAssessment)
    learning_goal: str | None = None
    learning_preferences: dict[str, str] = Field(
        default_factory=lambda: {"explanation_language": "Vietnamese"}
    )
    latest_assessment_id: str | None = None
    created_at: datetime
    updated_at: datetime
