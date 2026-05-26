from db.database import get_collection
habits = get_collection("habits")
print("Total habits:", habits.count_documents({}))
for h in habits.find():
    print(h)
