import unittest

from services import database
from services.auth_service import authenticate, register
from tests.helpers import TempDatabaseTestCase


class TestAuthService(TempDatabaseTestCase):
    def test_register_then_login(self):
        user_id = register("Lan_01", "matkhau123")
        self.assertEqual(user_id, "lan_01")  # đổi về chữ thường
        self.assertEqual(authenticate(" LAN_01 ", "matkhau123"), "lan_01")

    def test_wrong_password(self):
        register("lan", "matkhau123")
        self.assertIsNone(authenticate("lan", "saimatkhau"))

    def test_unknown_user(self):
        self.assertIsNone(authenticate("nobody", "matkhau123"))

    def test_duplicate_username(self):
        register("lan", "matkhau123")
        with self.assertRaises(ValueError):
            register("LAN", "khac12345")

    def test_invalid_username(self):
        for bad in ["ab", "có dấu", "a" * 21, "lan!"]:
            with self.assertRaises(ValueError, msg=bad):
                register(bad, "matkhau123")

    def test_short_password(self):
        with self.assertRaises(ValueError):
            register("lan", "1234567")

    def test_password_is_not_stored_in_plain_text(self):
        register("lan", "matkhau123")
        self.assertNotIn(b"matkhau123", self.db_path.read_bytes())
        with database.get_connection() as conn:
            row = conn.execute("SELECT password_hash, salt FROM accounts WHERE username = 'lan'").fetchone()
        self.assertTrue(row["password_hash"])
        self.assertTrue(row["salt"])

    def test_same_password_gives_different_hashes(self):
        register("lan", "matkhau123")
        register("minh", "matkhau123")
        with database.get_connection() as conn:
            hashes = [row[0] for row in conn.execute("SELECT password_hash FROM accounts")]
        self.assertNotEqual(hashes[0], hashes[1])


if __name__ == "__main__":
    unittest.main()
