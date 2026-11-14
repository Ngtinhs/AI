from pydantic import BaseModel, Field, field_validator


class Summary(BaseModel):
    english: str = Field(description="Short summary in simple A2 English")
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
    options: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    explanation_vi: str


class TutorAnalysis(BaseModel):
    summary: Summary
    vocabulary: list[VocabularyItem]
    key_sentences: list[KeySentence]
    quiz: list[QuizQuestion]

    @field_validator("quiz")
    @classmethod
    def validate_quiz_count(cls, value):
        if value and len(value) != 5:
            raise ValueError("Quiz phải có đúng 5 câu hỏi.")
        return value

    @field_validator("vocabulary")
    @classmethod
    def validate_vocabulary_count(cls, value):
        if value and not 5 <= len(value) <= 10:
            raise ValueError("Vocabulary phải có từ 5 đến 10 mục.")
        return value

    @field_validator("key_sentences")
    @classmethod
    def validate_key_sentence_count(cls, value):
        if value and len(value) != 5:
            raise ValueError("Key Sentences phải có đúng 5 câu.")
        return value
