"""
services/schedule_service.py — Service for scheduling habits, checking locks, and completion.
"""
from __future__ import annotations

import uuid
from datetime import datetime, date, timedelta
from typing import Optional, List
from db.database import get_collection
from services.habit_service import get_habit
from utils.helpers import now_iso


def create_schedule_entry(user_id: str, habit_id: str, date_str: str,
                          start_time: str, end_time: str,
                          auto_lock_enabled: bool = False,
                          auto_lock_hours: int = 1) -> dict:
    schedules = get_collection("scheduled_habits")
    entry = {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "habit_id": habit_id,
        "date": date_str,  # YYYY-MM-DD
        "start_time": start_time,  # HH:MM
        "end_time": end_time,  # HH:MM
        "auto_lock_enabled": auto_lock_enabled,
        "auto_lock_hours": auto_lock_hours,
        "completed": False,
        "completed_at": None,
        "locked": False,
    }
    schedules.insert_one(entry)
    return _clean(entry)


def get_schedule(user_id: str, date_str: str) -> List[dict]:
    """Retrieve schedule entries for a specific day and populate habit details."""
    schedules = get_collection("scheduled_habits")
    query = {"user_id": user_id, "date": date_str}
    entries = list(schedules.find(query))

    results = []
    for entry in entries:
        # Check auto-lock first
        entry = check_and_update_lock(entry)

        # Hydrate habit info
        habit = get_habit(entry["habit_id"])
        if not habit:
            # Habit was deleted, skip or show as deleted
            continue
        
        cleaned = _clean(entry)
        cleaned["habit_name"] = habit.get("name", "Unnamed Habit")
        cleaned["habit_description"] = habit.get("description", "")
        cleaned["habit_category"] = habit.get("category", "Learning")
        cleaned["habit_symbol"] = habit.get("symbol", "star")
        cleaned["habit_points"] = habit.get("points", 10)
        cleaned["habit_color"] = habit.get("color") or "#6366F1"
        results.append(cleaned)

    # Sort chronologically by start_time
    results.sort(key=lambda x: x["start_time"])
    return results


def get_schedule_range(user_id: str, start_date: str, end_date: str) -> List[dict]:
    """Retrieve hydrated schedule entries within a date range."""
    schedules = get_collection("scheduled_habits")
    query = {
        "user_id": user_id,
        "date": {"$gte": start_date, "$lte": end_date}
    }
    entries = list(schedules.find(query))

    results = []
    for entry in entries:
        entry = check_and_update_lock(entry)
        habit = get_habit(entry["habit_id"])
        if not habit:
            continue
        cleaned = _clean(entry)
        cleaned["habit_name"] = habit["name"]
        cleaned["habit_category"] = habit["category"]
        cleaned["habit_points"] = habit["points"]
        cleaned["habit_symbol"] = habit["symbol"]
        cleaned["habit_color"] = habit.get("color") or "#6366F1"
        results.append(cleaned)

    return results


def check_and_update_lock(entry: dict) -> dict:
    """Disable auto-lock completely."""
    entry["locked"] = False
    return entry


def delete_schedule_entry(entry_id: str) -> None:
    get_collection("scheduled_habits").delete_one({"_id": entry_id})


def copy_day_schedule(user_id: str, source_date: str, target_date: str) -> int:
    """Copy all schedule items from source_date to target_date. Returns count copied."""
    schedules = get_collection("scheduled_habits")
    
    # Clear target date first to prevent duplication
    schedules.delete_many({"user_id": user_id, "date": target_date})

    source_items = list(schedules.find({"user_id": user_id, "date": source_date}))
    copied_count = 0

    for item in source_items:
        new_entry = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "habit_id": item["habit_id"],
            "date": target_date,
            "start_time": item["start_time"],
            "end_time": item["end_time"],
            "auto_lock_enabled": item.get("auto_lock_enabled", False),
            "auto_lock_hours": item.get("auto_lock_hours", 1),
            "completed": False,
            "completed_at": None,
            "locked": False,
        }
        schedules.insert_one(new_entry)
        copied_count += 1

    return copied_count


def toggle_completion(entry_id: str, user_id: str) -> Optional[dict]:
    """Toggle completion status of a schedule entry. Triggers points & XP calculations."""
    schedules = get_collection("scheduled_habits")
    entry = schedules.find_one({"_id": entry_id, "user_id": user_id})
    if not entry:
        return None

    entry = check_and_update_lock(entry)
    if entry.get("locked"):
        return None  # Cannot toggle locked items

    is_completing = not entry.get("completed")
    
    # Fetch habit for rewards/XP calc
    habit = get_habit(entry["habit_id"])
    if not habit:
        return None

    # Calculate points and duration
    points_val = habit["points"]
    from services.xp_service import award_completion, revert_completion

    if is_completing:
        try:
            start_dt = datetime.strptime(f"{entry['date']} {entry['start_time']}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{entry['date']} {entry['end_time']}", "%Y-%m-%d %H:%M")
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
            
            now_dt = datetime.now()
            # If completed during the scheduled window, calculate elapsed time
            if start_dt <= now_dt < end_dt:
                duration_minutes = (now_dt - start_dt).total_seconds() / 60.0
            else:
                duration_minutes = (end_dt - start_dt).total_seconds() / 60.0
        except Exception:
            duration_minutes = 30.0  # fallback

        schedules.update_one(
            {"_id": entry_id},
            {"$set": {
                "completed": True,
                "completed_at": now_iso(),
                "completed_duration_minutes": duration_minutes
            }}
        )
        # Award points & XP
        award_completion(user_id, points_val, duration_minutes)
    else:
        # Fetch stored duration, fallback to scheduled duration
        completed_duration_minutes = entry.get("completed_duration_minutes")
        if completed_duration_minutes is None:
            try:
                start_dt = datetime.strptime(entry["start_time"], "%H:%M")
                end_dt = datetime.strptime(entry["end_time"], "%H:%M")
                completed_duration_minutes = (end_dt - start_dt).total_seconds() / 60.0
                if completed_duration_minutes < 0:
                    completed_duration_minutes += 24 * 60
            except Exception:
                completed_duration_minutes = 30.0

        schedules.update_one(
            {"_id": entry_id},
            {"$set": {
                "completed": False,
                "completed_at": None,
                "completed_duration_minutes": None
            }}
        )
        # Revert points & XP
        revert_completion(user_id, points_val, completed_duration_minutes)


    # Return refreshed and hydrated entry
    entry = schedules.find_one({"_id": entry_id})
    cleaned = _clean(entry)
    cleaned["habit_name"] = habit["name"]
    cleaned["habit_category"] = habit["category"]
    cleaned["habit_points"] = habit["points"]
    cleaned["habit_symbol"] = habit["symbol"]
    cleaned["habit_color"] = habit.get("color") or "#6366F1"
    return cleaned


def _clean(doc: dict) -> dict:
    if not doc:
        return None
    d = dict(doc)
    d["id"] = str(d.get("_id", ""))
    return d
