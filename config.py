"""
config.py — App-wide constants and definitions for Routine Tracker v2
"""

# ─── Level System ───────────────────────────────────────────────────────────
# We calculate level and XP requirements dynamically.
# Level 1 cap is 100 XP. Each subsequent level increases the cap by 1.6x.

def get_level_max_xp(level: int) -> int:
    """Return the XP required to clear the given level (from level to level+1)."""
    if level < 1:
        return 100
    # Level 1 -> 100
    # Level 2 -> 160
    # Level 3 -> 256
    # Level 4 -> 410
    # Level 5 -> 655
    return int(100 * (1.6 ** (level - 1)))

def get_level_from_xp(total_xp: int) -> tuple[int, int, int]:
    """
    Given total cumulative XP, return a tuple of:
    (current_level, xp_progress_in_current_level, xp_required_for_next_level)
    """
    level = 1
    remaining_xp = total_xp
    while True:
        max_xp_for_level = get_level_max_xp(level)
        if remaining_xp >= max_xp_for_level:
            remaining_xp -= max_xp_for_level
            level += 1
        else:
            break
    return level, remaining_xp, get_level_max_xp(level)

def get_level_title(level: int) -> str:
    if level <= 1:
        return "Novice Planner"
    elif level <= 4:
        return "Rhythm Builder"
    elif level <= 7:
        return "Routine Architect"
    elif level <= 10:
        return "Habit Master"
    else:
        return "Productivity Legend"

# ─── Consistency Multiplier ──────────────────────────────────────────────────
# Streak of consecutive perfect days
def get_streak_multiplier(streak: int) -> float:
    if streak >= 14:
        return 3.0
    elif streak >= 7:
        return 2.0
    elif streak >= 3:
        return 1.5
    return 1.0

# ─── Habit Categories ────────────────────────────────────────────────────────
CATEGORIES = [
    "Learning",
    "Health & Fitness",
    "Work & Coding",
    "Mind & Sleep",
    "Daily Routine",
    "Personal Development"
]

CATEGORY_COLORS = {
    "Learning": "#6366F1",             # Indigo
    "Health & Fitness": "#10B981",     # Emerald
    "Work & Coding": "#F59E0B",        # Amber
    "Mind & Sleep": "#8B5CF6",         # Purple
    "Daily Routine": "#EC4899",        # Pink
    "Personal Development": "#3B82F6"  # Blue
}

def normalize_category(cat: str) -> str:
    if not cat:
        return CATEGORIES[0]
    
    mapping = {
        "study": "Learning",
        "fitness": "Health & Fitness",
        "coding": "Work & Coding",
        "sleep": "Mind & Sleep",
        "meditation": "Mind & Sleep",
        "reading": "Learning",
        "personal": "Personal Development"
    }
    
    normalized = cat.strip().lower()
    if normalized in mapping:
        return mapping[normalized]
        
    for c in CATEGORIES:
        if c.lower() == normalized:
            return c
            
    return CATEGORIES[0]

# ─── JWT Cookie Configuration ────────────────────────────────────────────────
JWT_COOKIE_NAME = "rt_token"
JWT_EXPIRY_DAYS = 7
