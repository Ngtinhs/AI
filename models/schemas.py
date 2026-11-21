from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from config.settings import (
    KEY_SENTENCE_COUNT,
    QUIZ_COUNT,
    QUIZ_OPTION_COUNT,
    VOCABULARY_MAX,
    VOCABULARY_MIN,
)


class Summary(BaseModel):
    english: str = Field(description="Short summary in English suitable for the learner's level")
    vietnamese: str = Field(description="Vietnamese translation")


class VocabularyItem(BaseModel):
    word: str
    ipa: str = ""
    meaning_vi: str
    example: str
    example_vi: str


class KeySentence(BaseModel):
    english: str
    vietnamese: str
    usage_vi: str


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=QUIZ_OPTION_COUNT, max_length=QUIZ_OPTION_COUNT)
    correct_index: int = Field(ge=0, le=QUIZ_OPTION_COUNT - 1)
    explanation_vi: str


class TutorAnalysis(BaseModel):
    summary: Summary
    vocabulary: list[VocabularyItem]
    key_sentences: list[KeySentence]
    quiz: list[QuizQuestion]

    @field_validator("quiz")
    @classmethod
    def validate_quiz_count(cls, value):
        if value and len(value) != QUIZ_COUNT:
            raise ValueError(f"Quiz phải có đúng {QUIZ_COUNT} câu hỏi.")
        return value

    @field_validator("vocabulary")
    @classmethod
    def validate_vocabulary_count(cls, value):
        if value and not VOCABULARY_MIN <= len(value) <= VOCABULARY_MAX:
            raise ValueError(f"Vocabulary phải có từ {VOCABULARY_MIN} đến {VOCABULARY_MAX} mục.")
        return value

    @field_validator("key_sentences")
    @classmethod
    def validate_key_sentence_count(cls, value):
        if value and len(value) != KEY_SENTENCE_COUNT:
            raise ValueError(f"Key Sentences phải có đúng {KEY_SENTENCE_COUNT} câu.")
        return value


@dataclass
class LessonSummary:
    lesson_id: int
    video_id: str
    video_url: str
    learner_level: str
    created_at: datetime
