"""
services/habit_service.py — CRUD for the habit library.
"""
from __future__ import annotations

import uuid
from typing import Optional, List
from db.database import get_collection
from utils.helpers import now_iso


def create_habit(user_id: str, name: str, description: str, category: str,
                 symbol: str, points: int = 10, color: Optional[str] = None) -> dict:
    habits = get_collection("habits")
    habit = {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": name.strip(),
        "description": description.strip(),
        "category": category,
        "symbol": symbol,
        "points": points,
        "color": color,
        "created_at": now_iso(),
        "is_active": True,
    }
    habits.insert_one(habit)
    return _clean(habit)


def get_habits(user_id: str, active_only: bool = True) -> List[dict]:
    query = {"user_id": user_id}
    if active_only:
        query["is_active"] = True
    return [_clean(h) for h in get_collection("habits").find(query)]


def get_habit(habit_id: str) -> Optional[dict]:
    h = get_collection("habits").find_one({"_id": habit_id})
    return _clean(h) if h else None


def update_habit(habit_id: str, updates: dict) -> None:
    # Remove _id or id keys to prevent illegal key modification in mongo
    updates = {k: v for k, v in updates.items() if k not in ["_id", "id"]}
    get_collection("habits").update_one({"_id": habit_id}, {"$set": updates})


def delete_habit(habit_id: str) -> None:
    """Archiving or deleting a habit completely, plus its schedule entries."""
    get_collection("habits").delete_one({"_id": habit_id})
    get_collection("scheduled_habits").delete_many({"habit_id": habit_id})


def _clean(doc: dict) -> dict:
    if not doc:
        return None
    d = dict(doc)
    d["id"] = str(d.get("_id", ""))
    
    from config import normalize_category
    d["category"] = normalize_category(d.get("category", ""))
    d["description"] = d.get("description") or ""
    d["points"] = d.get("points") or 10
    d["symbol"] = d.get("symbol") or "star"
    return d
