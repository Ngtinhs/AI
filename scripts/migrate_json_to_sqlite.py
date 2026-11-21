"""
Chuyển dữ liệu JSON cũ (data/accounts.json, users.json, assessments.json) sang data/app.db.

    python scripts/migrate_json_to_sqlite.py

Chạy lại nhiều lần an toàn (INSERT OR IGNORE), không xóa file JSON.
Profile/kết quả không thuộc tài khoản nào sẽ bị bỏ qua.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from config.settings import DB_PATH, PROJECT_ROOT  # noqa: E402
from models.assessment import AssessmentResult  # noqa: E402
from models.learner import LearnerProfile  # noqa: E402
from services.assessment_service import assessment_row  # noqa: E402
from services.database import get_connection, insert  # noqa: E402
from services.profile_service import profile_row  # noqa: E402

DATA_DIR = PROJECT_ROOT / "data"
ACCOUNT_FIELDS = ("password_hash", "salt", "iterations", "created_at")


def load(filename: str, key: str, default):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"- Không có {filename}, bỏ qua.")
        return default
    return json.loads(path.read_text(encoding="utf-8"))[key]


def insert_owned(table: str, items: list, known: set[str]) -> None:
    """Thêm các model (có user_id) thuộc tài khoản đã biết; in số dòng thêm/bỏ qua."""
    to_row = profile_row if table == "profiles" else assessment_row
    added, skipped = 0, set()
    for item in items:
        if item.user_id not in known:
            skipped.add(item.user_id)
            continue
        added += insert(table, to_row(item), ignore=True)
    print(f"{table.title()}: thêm {added}/{len(items)}, bỏ qua (không có tài khoản): {sorted(skipped)}")


def main() -> None:
    accounts = load("accounts.json", "accounts", {})
    users = load("users.json", "users", {})
    assessments = load("assessments.json", "assessments", [])

    with get_connection() as conn:
        added = 0
        for username, acc in accounts.items():
            row = {"username": username, **{key: acc[key] for key in ACCOUNT_FIELDS}}
            added += insert("accounts", row, ignore=True)
        print(f"Accounts: thêm {added}/{len(accounts)}")

        known = {row["username"] for row in conn.execute("SELECT username FROM accounts")}
        insert_owned("profiles", [LearnerProfile.model_validate(raw) for raw in users.values()], known)
        insert_owned("assessments", [AssessmentResult.model_validate(raw) for raw in assessments], known)

    print(f"\nXong. Database: {DB_PATH}")


if __name__ == "__main__":
    main()
