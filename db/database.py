"""
db/database.py — MongoDB connection and collection helpers
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure

load_dotenv()

_client: Optional[MongoClient] = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/habit_tracker")
        db_name = os.getenv("DB_NAME", "habit_tracker")
        _client = MongoClient(url, serverSelectionTimeoutMS=5000)
        _db = _client[db_name]
        _ensure_indexes()
    return _db


def get_collection(name: str):
    return get_db()[name]


def _ensure_indexes():
    db = _db
    # Users: unique username
    db["users"].create_index([("username", ASCENDING)], unique=True)
    # Habits: by user
    db["habits"].create_index([("user_id", ASCENDING)])
    # Scheduled Habits: by user, date, habit
    db["scheduled_habits"].create_index([("user_id", ASCENDING), ("date", ASCENDING)])
    db["scheduled_habits"].create_index([("habit_id", ASCENDING)])
    # Rewards: by user
    db["rewards"].create_index([("user_id", ASCENDING)])
    # Redemptions: by user
    db["redemptions"].create_index([("user_id", ASCENDING)])
    # Completions, Quests, Moods, Achievements, Kingdom: keep old ones for migration stability
    db["completions"].create_index([("user_id", ASCENDING), ("date", ASCENDING)])
    db["quests"].create_index([("user_id", ASCENDING), ("date", ASCENDING)])
    db["moods"].create_index([("user_id", ASCENDING), ("date", ASCENDING)], unique=True)
    db["achievements"].create_index([("user_id", ASCENDING)])
    db["kingdom"].create_index([("user_id", ASCENDING)], unique=True)


def ping():
    """Test if DB is reachable. Returns (True, None) or (False, error_msg)."""
    try:
        get_db().command("ping")
        return True, None
    except ConnectionFailure as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)
