"""
services/stats_service.py — Aggregations and insights based on scheduled habits (v2)
"""
from __future__ import annotations

from datetime import date, timedelta
from collections import defaultdict
from db.database import get_collection
from services.habit_service import get_habit


def get_routine_stats(user_id: str, days: int = 30) -> dict:
    """Retrieve aggregations for the past N days from scheduled_habits."""
    schedules = get_collection("scheduled_habits")
    
    # Calculate cutoff date
    cutoff_date = (date.today() - timedelta(days=days)).isoformat()
    
    query = {
        "user_id": user_id,
        "date": {"$gte": cutoff_date}
    }
    
    entries = list(schedules.find(query))
    
    total_scheduled = len(entries)
    total_completed = sum(1 for e in entries if e.get("completed"))
    completion_rate = int((total_completed / total_scheduled) * 100) if total_scheduled > 0 else 0
    
    # Group by date to find perfect days
    date_groups = defaultdict(list)
    for e in entries:
        date_groups[e["date"]].append(e)
        
    perfect_days = 0
    for day_str, items in date_groups.items():
        if items and all(x.get("completed") for x in items):
            perfect_days += 1
            
    # Fetch user for current streak & level details
    user = get_collection("users").find_one({"_id": user_id})
    streak = user.get("consistency_streak", 0) if user else 0
    points = user.get("points", 0) if user else 0
    xp = user.get("xp", 0) if user else 0
    level = user.get("level", 1) if user else 1
            
    return {
        "total_scheduled": total_scheduled,
        "total_completed": total_completed,
        "completion_rate": completion_rate,
        "perfect_days": perfect_days,
        "unique_days_scheduled": len(date_groups),
        "streak": streak,
        "points": points,
        "xp": xp,
        "level": level
    }


def get_category_stats(user_id: str, days: int = 30) -> list[dict]:
    """Retrieve completion count grouped by habit categories."""
    schedules = get_collection("scheduled_habits")
    cutoff_date = (date.today() - timedelta(days=days)).isoformat()
    
    # Query completed schedules
    query = {
        "user_id": user_id,
        "completed": True,
        "date": {"$gte": cutoff_date}
    }
    
    completed_entries = list(schedules.find(query))
    
    # Count per category
    category_counts = defaultdict(int)
    for entry in completed_entries:
        habit = get_habit(entry["habit_id"])
        if habit:
            category_counts[habit["category"]] += 1
            
    from config import CATEGORIES, CATEGORY_COLORS
    result = []
    for cat in CATEGORIES:
        result.append({
            "category": cat,
            "count": category_counts.get(cat, 0),
            "color": CATEGORY_COLORS.get(cat, "#6366F1")
        })
        
    # Sort by count descending
    result.sort(key=lambda x: x["count"], reverse=True)
    return result


def get_smart_suggestions(user_id: str) -> list[str]:
    """Provide minimal recommendations based on routine history."""
    stats = get_routine_stats(user_id, days=14)
    suggestions = []
    
    if stats["total_scheduled"] == 0:
        suggestions.append("🌱 Your routine schedule is empty. Head to the **Schedule** tab to plan some habits!")
        return suggestions
        
    rate = stats["completion_rate"]
    if rate < 50:
        suggestions.append("💡 Your completion rate is under 50%. Try reducing the length of your scheduled slots or scheduling fewer habits to build momentum.")
    elif rate >= 85:
        suggestions.append("🔥 Outstanding consistency! With an 85%+ completion rate, you are doing great. Consider increasing habit durations or scheduling a new challenging habit.")
        
    streak = stats["streak"]
    if streak >= 3:
        suggestions.append(f"⚡ Double XP Multiplier is Active! Keep checking off all scheduled habits daily to maintain your {streak}-day perfect streak.")
    else:
        suggestions.append("🎯 Build a 3-day perfect streak (completing everything scheduled) to unlock a 1.5x XP multiplier!")
        
    return suggestions
