from config.settings import (
    DEFAULT_LEVEL,
    KEY_SENTENCE_COUNT,
    QUIZ_COUNT,
    QUIZ_OPTION_COUNT,
    VOCABULARY_MAX,
    VOCABULARY_MIN,
)

# Đổi mỗi khi sửa prompt để cache không trả về bài học tạo từ prompt cũ.
PROMPT_VERSION = "w2-level-v1"

LEARNER_CONTEXT = {
    "native_language": "Vietnamese",
    "english_level": DEFAULT_LEVEL,
    "learning_goal": "Improve daily English communication",
    "learning_preference": "Simple explanations",
    "explanation_language": "Vietnamese",
}


def build_learner_context(level: str | None) -> dict:
    return {**LEARNER_CONTEXT, "english_level": level or DEFAULT_LEVEL}


def build_tutor_prompt(context: dict, transcript: str) -> str:
    level = context["english_level"]
    return f"""
You are a friendly English teacher who creates lessons from video transcripts.

LEARNER CONTEXT:
- Native language: {context["native_language"]}
- English level: {level}
- Learning goal: {context["learning_goal"]}
- Learning preference: {context["learning_preference"]}
- Explanation language: {context["explanation_language"]}

TASK:
Analyze the transcript and create these four learning sections:
1. Summary: a short summary in English suitable for a {level} learner,
   and a Vietnamese translation.
2. Vocabulary: choose {VOCABULARY_MIN} to {VOCABULARY_MAX} useful words or phrases that appear in the transcript.
   Include IPA when you can provide it reliably, Vietnamese meaning in this context,
   a simple English example, and its Vietnamese translation.
3. Key sentences: choose {KEY_SENTENCE_COUNT} useful sentences that appear in the transcript.
   Include Vietnamese translation and a simple Vietnamese explanation of how to use each.
4. Quiz: create {QUIZ_COUNT} multiple-choice questions about information explicitly stated in the transcript.
   Each question must have exactly {QUIZ_OPTION_COUNT} options and exactly 1 correct answer.
   Give the correct option index (0 to {QUIZ_OPTION_COUNT - 1}) and explain the answer in Vietnamese.

STRICT RULES:
- Use only information supported by the transcript for video-specific facts.
- Do not invent events, people, facts, or claims about the video.
- Keep all English (summary, examples, quiz) suitable for a {level} learner.
- Choose vocabulary and key sentences that are useful for a {level} learner.
- Explain in Vietnamese.
- Vocabulary meanings must match the context.
- Examples should be short, practical, and easy to understand.
- Select key sentences from the transcript; do not pretend invented sentences were spoken in the video.
- If the transcript does not contain enough information for a section, say so clearly in that section.
- Return data matching the requested JSON schema. Do not add Markdown fences.

TRANSCRIPT:
<<<TRANSCRIPT_START>>>
{transcript}
<<<TRANSCRIPT_END>>>
""".strip()
