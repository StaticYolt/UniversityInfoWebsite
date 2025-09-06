import os
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
DB_NAME = "Feeddata"

client = MongoClient(mongo_uri, server_api=ServerApi("1"))
db = client[DB_NAME]

# collections: jobs, events, resources
collections = {
    "job": db["jobs"],
    "event": db["events"],
    "resource": db["resources"]
}

def normalize_item(doc, idx, dtype):
    return {
        "id": str(idx),  # assign string IDs for frontend
        "type": dtype,
        "title": doc.get("title", "Untitled"),
        "description": doc.get("description", ""),
        "date": doc.get("date"),
        "link": doc.get("link"),
        "show": doc.get("show", True)
    }

def export_all():
    # for collection in collections:
    #     print(collections.get(collection).find_one())
    items = []
    idx = 1
    for dtype, coll in collections.items():
        for doc in coll.find():
            items.append(normalize_item(doc, idx, dtype))
            idx += 1

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"✅ Exported {len(items)} items to data.json")

if __name__ == "__main__":
    export_all()
