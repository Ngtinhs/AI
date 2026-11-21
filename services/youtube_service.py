from youtube_transcript_api import YouTubeTranscriptApi

from config.settings import TRANSCRIPT_LANGUAGES
from utils.timing import StageTimer, measure


def get_transcript(
    video_id: str,
    languages: list[str] | None = None,
    timer: StageTimer | None = None,
) -> str:
    try:
        with measure(timer, "Transcript Retrieval"):
            transcript = YouTubeTranscriptApi().fetch(video_id, languages=languages or TRANSCRIPT_LANGUAGES)

        with measure(timer, "Transcript Processing"):
            full_text = " ".join(s.text.strip() for s in transcript if s.text.strip())

        if not full_text:
            raise ValueError("Video có phụ đề nhưng nội dung phụ đề đang trống.")

        if timer:
            timer.info["transcript_chars"] = len(full_text)
        return full_text

    except Exception as exc:
        raise RuntimeError(
            "Không lấy được transcript. Video có thể không có phụ đề tiếng Anh, "
            "bị giới hạn truy cập hoặc YouTube đang chặn yêu cầu. "
            f"Chi tiết: {exc}"
        ) from exc
