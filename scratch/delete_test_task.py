from db.database import get_collection
schedules = get_collection("scheduled_habits")
result = schedules.delete_one({"_id": "108a86ac-39cd-4d3f-990b-730ebeb9f95b"})
print("Deleted test document. Deleted count:", result.deleted_count)
