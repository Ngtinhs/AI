from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id: str, languages: list[str] | None = None) -> str:
    """
    Lấy phụ đề video và ghép thành một đoạn văn bản.
    Mặc định ưu tiên phụ đề tiếng Anh, sau đó đến tiếng Việt.
    """
    if languages is None:
        languages = ["en", "vi"]

    try:
        # API phiên bản mới dùng instance và phương thức fetch().
        transcript = YouTubeTranscriptApi().fetch(
            video_id,
            languages=languages,
        )

        # Mỗi snippet chứa phần văn bản và mốc thời gian.
        lines = [snippet.text.strip() for snippet in transcript if snippet.text.strip()]
        full_text = " ".join(lines)

        if not full_text:
            raise ValueError("Video có phụ đề nhưng nội dung phụ đề đang trống.")

        return full_text

    except Exception as exc:
        raise RuntimeError(
            "Không lấy được transcript. Video có thể không có phụ đề, "
            "bị giới hạn truy cập hoặc YouTube đang chặn yêu cầu. "
            f"Chi tiết: {exc}"
        ) from exc
