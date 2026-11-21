from datetime import datetime


def now() -> datetime:
    """Giờ hiện tại, làm tròn đến giây để mọi timestamp lưu trong DB có cùng định dạng."""
    return datetime.now().replace(microsecond=0)
