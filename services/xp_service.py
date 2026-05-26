"""
services/xp_service.py — XP, level, and consistency multiplier tracking
"""
from __future__ import annotations

from datetime import date, timedelta
from db.database import get_collection
from config import get_level_from_xp, get_streak_multiplier


def calculate_consistency_streak(user_id: str) -> int:
    """
    Calculate consecutive perfect days (where all scheduled habits were completed).
    A perfect day has at least one scheduled habit, and 100% of them are completed.
    Returns the current active streak.
    """
    schedules_col = get_collection("scheduled_habits")
    
    # Group scheduled habits by date
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$date",
            "all_completed": {"$min": "$completed"},
            "total_count": {"$sum": 1}
        }}
    ]
    days = list(schedules_col.aggregate(pipeline))
    if not days:
        return 0

    # Build map of date_str -> is_perfect
    perfect_days = {
        d["_id"]: (d["all_completed"] is True and d["total_count"] > 0)
        for d in days
    }

    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Choose start date for counting streak back
    start_date = today
    if not perfect_days.get(today.isoformat()):
        # Today is not perfect (or has no tasks). Let's check yesterday.
        if perfect_days.get(yesterday.isoformat()):
            start_date = yesterday
        else:
            return 0  # Neither today nor yesterday is perfect

    streak = 0
    current_check = start_date
    while True:
        date_str = current_check.isoformat()
        if perfect_days.get(date_str):
            streak += 1
            current_check -= timedelta(days=1)
        else:
            break

    return streak


def update_consistency_stats(user_id: str) -> tuple[int, float]:
    """Calculate and save consistency streak & multiplier for a user."""
    users_col = get_collection("users")
    streak = calculate_consistency_streak(user_id)
    multiplier = get_streak_multiplier(streak)
    
    users_col.update_one(
        {"_id": user_id},
        {"$set": {
            "consistency_streak": streak,
            "multiplier": multiplier
        }}
    )
    return streak, multiplier


def award_completion(user_id: str, points: int, duration_minutes: float) -> dict:
    """Award points and XP to the user on habit completion."""
    users_col = get_collection("users")
    user = users_col.find_one({"_id": user_id})
    if not user:
        return {}

    multiplier = user.get("multiplier", 1.0)
    # XP earned = duration_minutes * 0.1 * multiplier
    xp_gained = max(1, int(duration_minutes * 0.1 * multiplier))

    # Update cumulative XP and points
    new_xp = user.get("xp", 0) + xp_gained
    new_points = user.get("points", 0) + points

    # Calculate new level
    new_level, _, _ = get_level_from_xp(new_xp)

    users_col.update_one(
        {"_id": user_id},
        {"$set": {
            "xp": new_xp,
            "points": new_points,
            "level": new_level
        }}
    )

    # Recalculate consistency streak & multiplier
    update_consistency_stats(user_id)

    return {"xp_gained": xp_gained, "points_gained": points}


def revert_completion(user_id: str, points: int, duration_minutes: float) -> dict:
    """Deduct points and XP when a habit completion is unchecked."""
    users_col = get_collection("users")
    user = users_col.find_one({"_id": user_id})
    if not user:
        return {}

    multiplier = user.get("multiplier", 1.0)
    xp_lost = max(1, int(duration_minutes * 0.1 * multiplier))

    new_xp = max(0, user.get("xp", 0) - xp_lost)
    new_points = max(0, user.get("points", 0) - points)
    
    new_level, _, _ = get_level_from_xp(new_xp)

    users_col.update_one(
        {"_id": user_id},
        {"$set": {
            "xp": new_xp,
            "points": new_points,
            "level": new_level
        }}
    )

    update_consistency_stats(user_id)

    return {"xp_lost": xp_lost, "points_lost": points}
