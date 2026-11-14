import json
from models.schemas import TutorAnalysis


def parse_analysis_json(raw_json: str) -> TutorAnalysis:
    """Tiện ích parse JSON nếu cần xử lý phản hồi dạng chuỗi ở nơi khác."""
    try:
        data = json.loads(raw_json)
        return TutorAnalysis.model_validate(data)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"JSON từ AI không đúng cấu trúc: {exc}") from exc
