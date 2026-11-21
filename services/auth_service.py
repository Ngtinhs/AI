"""Tài khoản: chỉ lưu mã băm PBKDF2-SHA256 với salt ngẫu nhiên riêng cho từng người."""

import hashlib
import hmac
import os
import re
import sqlite3

from config.settings import (
    HASH_ITERATIONS,
    MIN_PASSWORD_LENGTH,
    SALT_BYTES,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)
from services.database import fetch_one, insert
from utils.clock import now

USERNAME_PATTERN = re.compile(rf"[a-z0-9_]{{{USERNAME_MIN_LENGTH},{USERNAME_MAX_LENGTH}}}")


def normalize_username(username: str) -> str:
    return username.strip().lower()


def hash_password(password: str, salt: bytes, iterations: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations).hex()


def register(username: str, password: str) -> str:
    username = normalize_username(username)

    if not USERNAME_PATTERN.fullmatch(username):
        raise ValueError(
            f"Tên đăng nhập phải dài {USERNAME_MIN_LENGTH}–{USERNAME_MAX_LENGTH} ký tự, "
            "chỉ gồm chữ thường, số và dấu _."
        )
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Mật khẩu phải có ít nhất {MIN_PASSWORD_LENGTH} ký tự.")

    salt = os.urandom(SALT_BYTES)
    row = {
        "username": username,
        "password_hash": hash_password(password, salt, HASH_ITERATIONS),
        "salt": salt.hex(),
        "iterations": HASH_ITERATIONS,
        "created_at": now().isoformat(),
    }
    try:
        insert("accounts", row)
    except sqlite3.IntegrityError as exc:
        raise ValueError("Tên đăng nhập đã tồn tại.") from exc

    return username


def authenticate(username: str, password: str) -> str | None:
    username = normalize_username(username)
    account = fetch_one(
        "SELECT password_hash, salt, iterations FROM accounts WHERE username = ?", (username,)
    )
    if account is None:
        return None

    computed = hash_password(password, bytes.fromhex(account["salt"]), account["iterations"])
    return username if hmac.compare_digest(computed, account["password_hash"]) else None
