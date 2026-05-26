"""
services/reward_service.py — Manage reward creations and redemptions.
"""
from __future__ import annotations

import uuid
from typing import Optional, List
from db.database import get_collection
from utils.helpers import now_iso


def create_reward(user_id: str, name: str, description: str, cost: int, symbol: str) -> dict:
    rewards = get_collection("rewards")
    reward = {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": name.strip(),
        "description": description.strip(),
        "cost": max(1, cost),
        "symbol": symbol,
        "created_at": now_iso(),
    }
    rewards.insert_one(reward)
    return _clean(reward)


def get_rewards(user_id: str) -> List[dict]:
    rewards = get_collection("rewards")
    return [_clean(r) for r in rewards.find({"user_id": user_id})]


def get_reward(reward_id: str) -> Optional[dict]:
    r = get_collection("rewards").find_one({"_id": reward_id})
    return _clean(r) if r else None


def delete_reward(reward_id: str) -> None:
    get_collection("rewards").delete_one({"_id": reward_id})


def redeem_reward(user_id: str, reward_id: str) -> tuple[Optional[dict], Optional[str]]:
    """
    Deducts points and saves redemption record.
    Returns (redemption_record, None) on success, or (None, error_msg) on failure.
    """
    reward = get_reward(reward_id)
    if not reward:
        return None, "Reward not found."

    users_col = get_collection("users")
    user = users_col.find_one({"_id": user_id})
    if not user:
        return None, "User not found."

    points_balance = user.get("points", 0)
    cost = reward["cost"]

    if points_balance < cost:
        return None, f"Insufficient points. Need {cost} points (have {points_balance})."

    # Deduct points
    users_col.update_one(
        {"_id": user_id},
        {"$inc": {"points": -cost}}
    )

    # Record redemption
    redemptions = get_collection("redemptions")
    record = {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "reward_id": reward_id,
        "reward_name": reward["name"],
        "reward_symbol": reward["symbol"],
        "points_spent": cost,
        "redeemed_at": now_iso(),
    }
    redemptions.insert_one(record)

    return _clean(record), None


def get_redemptions(user_id: str) -> List[dict]:
    redemptions = get_collection("redemptions")
    # Fetch and sort by redeemed_at descending
    records = list(redemptions.find({"user_id": user_id}).sort("redeemed_at", -1))
    return [_clean(r) for r in records]


def _clean(doc: dict) -> dict:
    if not doc:
        return None
    d = dict(doc)
    d["id"] = str(d.get("_id", ""))
    return d
