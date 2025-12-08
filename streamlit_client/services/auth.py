"""
Authentication and user helpers for the Streamlit client.

Passwords are stored as salted PBKDF2 hashes in `user_info.password_hash`.
"""

from hashlib import pbkdf2_hmac
import re
import secrets
from typing import Any, Dict, Optional, Tuple

from ..db import execute, fetch_one

ITERATIONS = 200_000
PASSWORD_MIN_LENGTH = 8


def _hash_password(raw_password: str, salt: Optional[str] = None) -> str:
    """Hash a password with PBKDF2-SHA256 and return salt$hash."""
    salt = salt or secrets.token_hex(16)
    dk = pbkdf2_hmac("sha256", raw_password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS)
    return f"{salt}${dk.hex()}"


def _verify_password(raw_password: str, stored_hash: str) -> bool:
    """Check a raw password against a stored salt$hash string."""
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, hashed = stored_hash.split("$", 1)
    candidate = _hash_password(raw_password, salt=salt)
    return candidate.split("$", 1)[1] == hashed


def get_user(identifier: str) -> Optional[Dict[str, Any]]:
    """Fetch a user by username or email."""
    return fetch_one(
        """
        SELECT
            user_id,
            username,
            email,
            password_hash,
            user_type,
            fitness_goal,
            date_registered
        FROM user_info
        WHERE username = %s OR email = %s
        LIMIT 1
        """,
        [identifier, identifier],
    )


def authenticate(username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Validate credentials and return (ok, user_dict, error_message)."""
    user = get_user(username)
    if not user:
        return False, None, "Account not found."
    if not _verify_password(password, user["password_hash"]):
        return False, None, "Invalid password."

    return True, {
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "user_type": user.get("user_type") or "member",
        "fitness_goal": user.get("fitness_goal"),
    }, ""


def _password_errors(password: str, username: str, email: str) -> Optional[str]:
    """Return an error string if password does not meet requirements."""
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Password must be at least {PASSWORD_MIN_LENGTH} characters."
    if password.isdigit():
        return "Password cannot be entirely numeric."
    if username and username.lower() in password.lower():
        return "Password is too similar to the username."
    local_part = email.split("@")[0] if email else ""
    if local_part and local_part.lower() in password.lower():
        return "Password is too similar to the email."
    common = re.compile(r"(password|123456|qwerty)", re.IGNORECASE)
    if common.search(password):
        return "Password is too common."
    return None


def create_user(username: str, email: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Create a new user record if credentials are valid.

    Returns (ok, user_dict, error_message).
    """
    if not username or not email:
        return False, None, "Username and email are required."

    err = _password_errors(password, username, email)
    if err:
        return False, None, err

    existing = get_user(username) or get_user(email)
    if existing:
        return False, None, "Username or email already in use."

    password_hash = _hash_password(password)
    # user_info requires first_name/last_name; reuse username as first_name and blank last_name
    user_id = execute(
        """
        INSERT INTO user_info (
            username, first_name, last_name, email, password_hash, date_registered, registered, user_type
        )
        VALUES (%s, %s, %s, %s, %s, CURDATE(), 1, %s)
        """,
        [username, username, "", email, password_hash, "member"],
    )

    return True, {
        "user_id": user_id,
        "username": username,
        "email": email,
        "user_type": "member",
    }, ""
