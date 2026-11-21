import tempfile
import unittest
from pathlib import Path
from unittest import mock

from services import auth_service, database


class TempDatabaseTestCase(unittest.TestCase):
    """Mỗi test dùng một file database tạm, không đụng vào data/app.db thật."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "test.db"
        self.patches = [
            mock.patch.object(database, "DB_PATH", self.db_path),
            # Giảm số vòng băm mật khẩu để test chạy nhanh (app thật vẫn dùng 600.000).
            mock.patch.object(auth_service, "HASH_ITERATIONS", 1000),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in self.patches:
            patch.stop()
        self.tmp.cleanup()

    def count_rows(self, table: str) -> int:
        with database.get_connection() as conn:
            return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
