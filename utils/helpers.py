"""
utils/helpers.py — Shared utility functions for Routine Tracker v2
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional


# ─── Date Helpers ─────────────────────────────────────────────────────────────

def today_str() -> str:
    return date.today().isoformat()

def now_iso() -> str:
    return datetime.now().isoformat()

def date_range(days: int) -> list[str]:
    """Return list of date strings for the past N days (inclusive today)."""
    today = date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]

def parse_date(d: str) -> date:
    return date.fromisoformat(d)

def days_since(iso_date: str) -> int:
    return (date.today() - parse_date(iso_date)).days


# ─── XP / Level Helpers ───────────────────────────────────────────────────────

def get_level_info(total_xp: int) -> dict:
    """
    Returns dict with: level, title, xp_in_level, xp_for_level, pct, total_xp
    """
    from config import get_level_from_xp, get_level_title

    level, xp_in_level, xp_for_level = get_level_from_xp(total_xp)
    title = get_level_title(level)
    pct = min(100, int((xp_in_level / xp_for_level) * 100)) if xp_for_level > 0 else 100

    return {
        "level": level,
        "title": title,
        "xp_in_level": xp_in_level,
        "xp_for_level": xp_for_level,
        "pct": pct,
        "total_xp": total_xp,
    }


# ─── Streak Calculator ────────────────────────────────────────────────────────

def calc_streak(sorted_dates: list[str]) -> int:
    """
    Given a list of ISO date strings (sorted ascending), return the current streak.
    A streak is a consecutive sequence ending today or yesterday.
    """
    if not sorted_dates:
        return 0

    unique_dates = sorted(set(date.fromisoformat(d) for d in sorted_dates), reverse=True)
    today = date.today()

    # Streak must include today or yesterday to be "active"
    if unique_dates[0] < today - timedelta(days=1):
        return 0

    streak = 1
    for i in range(1, len(unique_dates)):
        if (unique_dates[i - 1] - unique_dates[i]).days == 1:
            streak += 1
        else:
            break
    return streak


def calc_longest_streak(sorted_dates: list[str]) -> int:
    if not sorted_dates:
        return 0
    unique_dates = sorted(set(date.fromisoformat(d) for d in sorted_dates))
    max_s = cur = 1
    for i in range(1, len(unique_dates)):
        if (unique_dates[i] - unique_dates[i - 1]).days == 1:
            cur += 1
            max_s = max(max_s, cur)
        else:
            cur = 1
    return max_s


# ─── Misc ─────────────────────────────────────────────────────────────────────

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def plural(n: int, word: str) -> str:
    return f"{n} {word}{'s' if n != 1 else ''}"

def format_xp(xp: int) -> str:
    if xp >= 1000:
        return f"{xp/1000:.1f}k"
    return str(xp)

def format_ampm(time_str: str) -> str:
    """Format 'HH:MM' 24h time to 12h AM/PM time."""
    try:
        dt = datetime.strptime(time_str, "%H:%M")
        return dt.strftime("%I:%M %p").lstrip('0')
    except Exception:
        return time_str

