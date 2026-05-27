import os
import sys
from dotenv import load_dotenv

# Add workspace path to sys.path
sys.path.append(os.getcwd())

from services.schedule_service import toggle_completion
from db.database import get_collection

def test_toggle(task_id, user_id):
    schedules = get_collection("scheduled_habits")
    entry_before = schedules.find_one({"_id": task_id})
    print("Before toggle:", entry_before)
    
    try:
        res = toggle_completion(task_id, user_id)
        print("Result of toggle_completion:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()
        
    entry_after = schedules.find_one({"_id": task_id})
    print("After toggle:", entry_after)

if __name__ == "__main__":
    test_toggle("eedc3a9a-a017-4144-83f5-40c1ebe01c33", "68353234-3a1c-4850-a49c-f2459eee5aa2")
