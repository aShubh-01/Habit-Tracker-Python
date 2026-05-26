from db.database import get_collection
schedules = get_collection("scheduled_habits")
result = schedules.update_one(
    {"_id": "e3cafcb8-3031-4898-a3f2-dfa47719dfa3"},
    {"$set": {"date": "2026-05-26"}}
)
print("Updated document date to 2026-05-26. Matched count:", result.matched_count)
