"""
Placement Test, chấm điểm không dùng Gemini:
- Đạt một level khi đúng ít nhất MIN_CORRECT_TO_PASS câu của level đó.
- Trình độ = level cao nhất mà mọi level từ A1 đến đó đều đạt; không đạt A1 -> "Below A1".
- Đạt một level cao hơn kết quả -> đánh dấu `inconsistent`.
"""

import uuid
from pathlib import Path

from config.settings import MIN_CORRECT_TO_PASS, QUESTION_BANK_PATH
from models.assessment import BELOW_A1, TEST_LEVELS, AssessmentResult, LevelScore, QuestionBank
from models.learner import LearnerProfile
from services.database import fetch_one, get_connection, insert
from services.profile_service import apply_assessment
from utils.clock import now


def load_question_bank(path: Path = QUESTION_BANK_PATH) -> QuestionBank:
    bank = QuestionBank.model_validate_json(path.read_text(encoding="utf-8"))

    ids = [q.id for q in bank.questions]
    if len(ids) != len(set(ids)):
        raise ValueError("Question Bank có id câu hỏi bị trùng.")

    for level in TEST_LEVELS:
        if not any(q.level == level for q in bank.questions):
            raise ValueError(f"Question Bank chưa có câu hỏi cho level {level}.")

    return bank


def score_answers(bank: QuestionBank, answers: dict[str, int | None], user_id: str) -> AssessmentResult:
    missing = [q.id for q in bank.questions if answers.get(q.id) is None]
    if missing:
        raise ValueError(f"Bạn chưa trả lời {len(missing)} câu hỏi.")

    level_correct = dict.fromkeys(TEST_LEVELS, 0)
    level_total = dict.fromkeys(TEST_LEVELS, 0)
    skill_correct: dict[str, int] = {}
    skill_total: dict[str, int] = {}

    for question in bank.questions:
        is_correct = answers[question.id] == question.correct_index
        level_total[question.level] += 1
        level_correct[question.level] += is_correct
        skill_total[question.skill] = skill_total.get(question.skill, 0) + 1
        skill_correct[question.skill] = skill_correct.get(question.skill, 0) + is_correct

    level_scores = [
        LevelScore(
            level=level,
            correct=level_correct[level],
            total=level_total[level],
            passed=level_correct[level] >= MIN_CORRECT_TO_PASS,
        )
        for level in TEST_LEVELS
    ]

    passed_streak = 0
    for score in level_scores:
        if not score.passed:
            break
        passed_streak += 1

    overall_level = level_scores[passed_streak - 1].level if passed_streak else BELOW_A1
    inconsistent = any(score.passed for score in level_scores[passed_streak:])

    return AssessmentResult(
        assessment_id=uuid.uuid4().hex,
        user_id=user_id,
        bank_version=bank.bank_version,
        answers={q.id: answers[q.id] for q in bank.questions},
        level_scores=level_scores,
        skill_correct=skill_correct,
        skill_total=skill_total,
        overall_level=overall_level,
        inconsistent=inconsistent,
        completed_at=now(),
    )


def assessment_row(result: AssessmentResult) -> dict:
    return {
        "assessment_id": result.assessment_id,
        "user_id": result.user_id,
        "overall_level": result.overall_level,
        "completed_at": result.completed_at.isoformat(),
        "result_json": result.model_dump_json(),
    }


def save_assessment(result: AssessmentResult) -> None:
    insert("assessments", assessment_row(result))


def record_assessment(result: AssessmentResult) -> LearnerProfile:
    """Lưu kết quả và cập nhật Learner Profile trong cùng một transaction."""
    with get_connection():
        save_assessment(result)
        return apply_assessment(result)


def get_latest_assessment(user_id: str) -> AssessmentResult | None:
    row = fetch_one(
        "SELECT result_json FROM assessments WHERE user_id = ? "
        "ORDER BY completed_at DESC, rowid DESC LIMIT 1",
        (user_id,),
    )
    return AssessmentResult.model_validate_json(row["result_json"]) if row else None
