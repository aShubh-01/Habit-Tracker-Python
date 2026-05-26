"""
utils/seed_data.py — Create demo users with 2 weeks of routine history.
Run: python utils/seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, timedelta, datetime
import uuid
import random

from db.database import get_collection
from services.auth_service import signup
from services.xp_service import calculate_consistency_streak
from config import get_streak_multiplier, get_level_from_xp


def seed():
    print("🌱 Seeding demo data for Routine Tracker v2...")

    # ── User 1: demo ──────────────────────────────────────────────────────────
    users_col = get_collection("users")

    # Remove existing demo user
    existing = users_col.find_one({"username": "demo"})
    if existing:
        uid = str(existing["_id"])
        # Clear all related collections
        for col in ["habits", "scheduled_habits", "rewards", "redemptions", "completions", "quests", "kingdom", "moods", "achievements"]:
            get_collection(col).delete_many({"user_id": uid})
        users_col.delete_one({"_id": existing["_id"]})
        print("  Removed existing user: demo")

    # Create demo user
    demo_user, _ = signup("demo", "demo123", "demo@routines.app")
    if not demo_user:
        print("  Could not create demo user. Skipping.")
        return

    demo_id = demo_user["id"]
    print(f"  Created user: demo (id: {demo_id})")

    # Create demo habits
    habits_data = [
        ("Morning Jog", "Go for a quick run to boost energy.", "Health & Fitness", "bolt", 15, "#10B981"),
        ("Read Python Book", "Learn deep details of language.", "Learning", "book-open", 10, "#6366F1"),
        ("LeetCode Problem", "Practice algorithms and data structures.", "Work & Coding", "code-bracket", 20, "#F59E0B"),
        ("Mindful Meditation", "10 minutes of breathing and focus.", "Mind & Sleep", "sparkles", 10, "#8B5CF6"),
        ("Sleep Prep", "Wind down, no screens 30m before bed.", "Mind & Sleep", "moon", 10, "#8B5CF6"),
        ("Journal Reflections", "Write down thoughts on daily wins.", "Personal Development", "pencil", 10, "#3B82F6"),
    ]

    habits_col = get_collection("habits")
    created_habits = []

    for name, desc, cat, symbol, pts, color in habits_data:
        habit = {
            "_id": str(uuid.uuid4()),
            "user_id": demo_id,
            "name": name,
            "description": desc,
            "category": cat,
            "symbol": symbol,
            "points": pts,
            "color": color,
            "created_at": (date.today() - timedelta(days=15)).isoformat() + "T08:00:00",
            "is_active": True,
        }
        habits_col.insert_one(habit)
        created_habits.append(habit)

    print(f"  Created {len(created_habits)} habits in library")

    # Map habits for scheduling
    habits_by_name = {h["name"]: h for h in created_habits}

    # Seed 14 days of scheduled habits and completions
    # We want a high completion rate with some perfect days for realism
    schedules_col = get_collection("scheduled_habits")
    total_xp = 0
    total_points = 0

    daily_schedule_plan = [
        ("Morning Jog", "07:00", "07:45", 45.0),       # 4.5 base XP
        ("Read Python Book", "09:00", "10:00", 60.0),   # 6.0 base XP
        ("LeetCode Problem", "14:00", "15:00", 60.0),   # 6.0 base XP
        ("Mindful Meditation", "18:00", "18:15", 15.0), # 1.5 base XP
        ("Sleep Prep", "22:30", "23:00", 30.0),         # 3.0 base XP
    ]

    # Pre-populate multiplier values day-by-day for seeding
    # For simplicity, we assume multiplier starts at 1.0 and increases
    current_streak = 0
    
    for days_ago in range(14, 0, -1):
        day_date = date.today() - timedelta(days=days_ago)
        day_str = day_date.isoformat()
        
        # Calculate streak multiplier for this day
        mult = get_streak_multiplier(current_streak)
        
        # Determine if this day will be a perfect day (100% completion)
        # Days: 14, 13, 12, 11 (perfect), 10 (missed one), 9, 8, 7 (perfect), etc.
        is_perfect_day = random.choice([True, True, False, True]) 
        
        all_completed = True
        for name, start, end, duration in daily_schedule_plan:
            habit = habits_by_name[name]
            
            # Determine completion
            completed = True
            if not is_perfect_day:
                if name == "Morning Jog" and random.random() < 0.5:
                    completed = False
                    all_completed = False
            
            comp_at = None
            if completed:
                comp_at = f"{day_str}T{start}:00"
                xp_earned = max(1, int(duration * 0.1 * mult))
                total_xp += xp_earned
                total_points += habit["points"]
                
            entry = {
                "_id": str(uuid.uuid4()),
                "user_id": demo_id,
                "habit_id": habit["_id"],
                "date": day_str,
                "start_time": start,
                "end_time": end,
                "auto_lock_enabled": True,
                "auto_lock_hours": 2,
                "completed": completed,
                "completed_at": comp_at,
                "locked": not completed,  # old ones are locked if incomplete
            }
            schedules_col.insert_one(entry)
            
        if all_completed:
            current_streak += 1
        else:
            current_streak = 0

    print(f"  Seeded 14 days of schedule history")
    print(f"  Earned {total_xp} XP and {total_points} total points from habits")

    # Seed rewards
    rewards_data = [
        ("Pizza Cheat Meal", "Indulge in a large stuffed crust pepperoni pizza.", 150, "gift"),
        ("1 Hour of Netflix", "Binge watch your favorite series guilt-free.", 50, "sparkles"),
        ("Buy Kindle Book", "Treat yourself to a new fiction or non-fiction ebook.", 200, "star"),
        ("Relaxing Spa Day", "Go get a premium 60-minute massage session.", 600, "heart"),
    ]
    
    rewards_col = get_collection("rewards")
    created_rewards = []
    for name, desc, cost, symbol in rewards_data:
        reward = {
            "_id": str(uuid.uuid4()),
            "user_id": demo_id,
            "name": name,
            "description": desc,
            "cost": cost,
            "symbol": symbol,
            "created_at": (date.today() - timedelta(days=10)).isoformat(),
        }
        rewards_col.insert_one(reward)
        created_rewards.append(reward)
        
    print(f"  Created {len(created_rewards)} reward choices in shop")

    # Seed some redemptions
    redemptions_col = get_collection("redemptions")
    # Redeem 3 Netflix hours and 1 Pizza meal
    netflix_reward = next(r for r in created_rewards if r["name"] == "1 Hour of Netflix")
    pizza_reward = next(r for r in created_rewards if r["name"] == "Pizza Cheat Meal")
    
    spent_points = 0
    redemptions_to_seed = [
        (netflix_reward, 8),
        (netflix_reward, 5),
        (pizza_reward, 3),
    ]
    
    for reward, days_ago in redemptions_to_seed:
        red_date = (date.today() - timedelta(days=days_ago)).isoformat()
        record = {
            "_id": str(uuid.uuid4()),
            "user_id": demo_id,
            "reward_id": reward["_id"],
            "reward_name": reward["name"],
            "reward_symbol": reward["symbol"],
            "points_spent": reward["cost"],
            "redeemed_at": f"{red_date}T19:30:00",
        }
        redemptions_col.insert_one(record)
        spent_points += reward["cost"]

    # Calculate remaining points
    remaining_points = max(0, total_points - spent_points)
    
    # Calculate current consistency stats dynamically
    final_streak = calculate_consistency_streak(demo_id)
    final_mult = get_streak_multiplier(final_streak)
    final_level, _, _ = get_level_from_xp(total_xp)

    # Save final user details
    users_col.update_one(
        {"_id": demo_id},
        {"$set": {
            "xp": total_xp,
            "points": remaining_points,
            "level": final_level,
            "consistency_streak": final_streak,
            "multiplier": final_mult
        }}
    )

    print(f"  Final stats calculated for user 'demo':")
    print(f"    Level: {final_level}")
    print(f"    XP: {total_xp}")
    print(f"    Points balance: {remaining_points} pts")
    print(f"    Active streak: {final_streak} days")
    print(f"    Multiplier: {final_mult}x")
    print("\n✅ Seed complete!")
    print("   Login with: demo / demo123")


if __name__ == "__main__":
    seed()
