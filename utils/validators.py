import re
from urllib.parse import urlparse, parse_qs


YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


def extract_video_id(url: str) -> str | None:
    """Trích xuất video ID từ URL youtube.com/watch, youtu.be hoặc Shorts."""
    try:
        parsed = urlparse(url.strip())
        host = parsed.netloc.lower()

        if host not in YOUTUBE_HOSTS:
            return None

        if host.endswith("youtu.be"):
            video_id = parsed.path.strip("/").split("/")[0]
        elif parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith("/shorts/") or parsed.path.startswith("/embed/"):
            parts = parsed.path.strip("/").split("/")
            video_id = parts[1] if len(parts) > 1 else None
        else:
            return None

        if video_id and re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            return video_id

        return None
    except Exception:
        return None


def validate_youtube_url(url: str) -> bool:
    return extract_video_id(url) is not None
