from db.database import get_collection
schedules = get_collection("scheduled_habits")
print("Total entries:", schedules.count_documents({}))
for doc in schedules.find():
    print(doc)
