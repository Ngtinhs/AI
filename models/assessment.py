from datetime import datetime
from typing import Literal, get_args

from pydantic import BaseModel, Field

from config.settings import QUIZ_OPTION_COUNT

TestLevel = Literal["A1", "A2", "B1", "B2"]
ResultLevel = Literal["Below A1", "A1", "A2", "B1", "B2"]
Skill = Literal["grammar", "vocabulary", "reading"]

TEST_LEVELS: list[str] = list(get_args(TestLevel))
SKILLS: list[str] = list(get_args(Skill))
BELOW_A1 = "Below A1"


class PlacementQuestion(BaseModel):
    id: str
    level: TestLevel
    skill: Skill
    passage: str | None = None
    question: str
    options: list[str] = Field(min_length=QUIZ_OPTION_COUNT, max_length=QUIZ_OPTION_COUNT)
    correct_index: int = Field(ge=0, le=QUIZ_OPTION_COUNT - 1)
    explanation_vi: str


class QuestionBank(BaseModel):
    bank_version: str
    questions: list[PlacementQuestion]


class LevelScore(BaseModel):
    level: TestLevel
    correct: int
    total: int
    passed: bool


class AssessmentResult(BaseModel):
    assessment_id: str
    user_id: str
    bank_version: str
    answers: dict[str, int]
    level_scores: list[LevelScore]
    skill_correct: dict[str, int]
    skill_total: dict[str, int]
    overall_level: ResultLevel
    # Đạt một level cao hơn nhưng trượt level thấp hơn.
    inconsistent: bool
    completed_at: datetime
