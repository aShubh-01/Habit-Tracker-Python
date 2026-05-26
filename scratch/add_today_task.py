from db.database import get_collection
import uuid

schedules = get_collection("scheduled_habits")
entry = {
    "_id": str(uuid.uuid4()),
    "user_id": "cbdeb107-46bf-43bc-af60-0482e1da00a0",
    "habit_id": "697bfaeb-3cc6-4f69-a832-4d1d6b492a8c",
    "date": "2026-05-26",
    "start_time": "18:00",
    "end_time": "19:00",
    "auto_lock_enabled": False,
    "auto_lock_hours": 1,
    "completed": False,
    "completed_at": None,
    "locked": False
}
schedules.insert_one(entry)
print("Inserted task for today (2026-05-26)")
