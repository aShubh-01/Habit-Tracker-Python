"""
services/auth_service.py — Signup, login, JWT generation and validation
"""
from __future__ import annotations

import os
import uuid
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from dotenv import load_dotenv
from db.database import get_collection

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-to-a-long-random-secret-string")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 7


# ─── Password Helpers ─────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ─── JWT Helpers ──────────────────────────────────────────────────────────────

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def validate_token(token: str) -> Optional[dict]:
    """Decode JWT and return user dict, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            return None
        return get_user_by_id(user_id)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ─── User CRUD ────────────────────────────────────────────────────────────────

def signup(username: str, password: str, email: str = "") -> tuple:
    """
    Create a new user. Returns (user_dict, token) on success, (None, error_msg) on failure.
    """
    users = get_collection("users")
    username = username.strip().lower()

    if not username or len(username) < 3:
        return None, "Username must be at least 3 characters."
    if not password or len(password) < 6:
        return None, "Password must be at least 6 characters."
    if users.find_one({"username": username}):
        return None, "Username already taken."

    user_id = str(uuid.uuid4())
    user = {
        "_id": user_id,
        "username": username,
        "email": email.strip().lower(),
        "password_hash": hash_password(password),
        "points": 0,
        "xp": 0,
        "level": 1,
        "consistency_streak": 0,
        "multiplier": 1.0,
        "created_at": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat(),
        "display_name": username.capitalize(),
    }
    users.insert_one(user)
    token = create_token(user_id)
    return _clean_user(user), token

def login(username: str, password: str) -> tuple:
    """Returns (user_dict, token) or (None, error_msg)."""
    users = get_collection("users")
    username = username.strip().lower()

    user = users.find_one({"username": username})
    if not user:
        return None, "Invalid username or password."
    if not verify_password(password, user["password_hash"]):
        return None, "Invalid username or password."

    users.update_one({"_id": user["_id"]}, {"$set": {"last_active": datetime.now().isoformat()}})
    token = create_token(str(user["_id"]))
    return _clean_user(user), token

def get_user_by_id(user_id: str) -> Optional[dict]:
    users = get_collection("users")
    user = users.find_one({"_id": user_id})
    return _clean_user(user) if user else None

def update_user(user_id: str, updates: dict) -> None:
    users = get_collection("users")
    users.update_one({"_id": user_id}, {"$set": updates})

def add_points(user_id: str, amount: int) -> None:
    get_collection("users").update_one({"_id": user_id}, {"$inc": {"points": amount}})

def get_all_users() -> List[dict]:
    return [_clean_user(u) for u in get_collection("users").find({})]

def delete_account(user_id: str) -> None:
    for col in ["users", "habits", "scheduled_habits", "rewards", "redemptions"]:
        get_collection(col).delete_many({"_id" if col == "users" else "user_id": user_id})


# ─── Internal ─────────────────────────────────────────────────────────────────

def _clean_user(user: dict) -> dict:
    """Remove sensitive fields from user doc."""
    if not user:
        return None
    u = dict(user)
    u.pop("password_hash", None)
    # Normalise _id to string
    u["id"] = str(u.get("_id", ""))
    return u
