import re
from urllib.parse import parse_qs, urlparse

YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
}
VIDEO_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{11}")


def extract_video_id(url: str) -> str | None:
    """Hỗ trợ youtube.com/watch, youtu.be, /shorts/ và /embed/."""
    try:
        parsed = urlparse(url.strip())
    except (AttributeError, ValueError):
        return None

    host = parsed.netloc.lower()
    if host not in YOUTUBE_HOSTS:
        return None

    parts = parsed.path.strip("/").split("/")
    if host.endswith("youtu.be"):
        video_id = parts[0]
    elif parsed.path == "/watch":
        video_id = parse_qs(parsed.query).get("v", [None])[0]
    elif parsed.path.startswith(("/shorts/", "/embed/")):
        video_id = parts[1] if len(parts) > 1 else None
    else:
        return None

    return video_id if video_id and VIDEO_ID_PATTERN.fullmatch(video_id) else None


def validate_youtube_url(url: str) -> bool:
    return extract_video_id(url) is not None
