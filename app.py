import os
from flask import Flask, request, jsonify
from pymongo import MongoClient

# MongoDB credentials
DATABASE_URI = os.environ.get(
    "DATABASE_URI",
    "mongodb+srv://mrnoobx:DAZCdTczVWyECi04@cluster0.sedgwxy.mongodb.net/?retryWrites=true&w=majority"
)
DATABASE_NAME = os.environ.get("DATABASE_NAME", "mrnoobx")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "Files")

# Flask app
app = Flask(__name__)

# MongoDB client
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "MongoDB API is running 🚀"})

@app.route("/files", methods=["GET"])
def get_files():
    # Query parameters
    query_param = request.args.get("q", "")  # search keyword
    page = int(request.args.get("page", 1))  # page number
    limit = int(request.args.get("limit", 50))  # items per page

    # Build query
    if query_param:
        query = {
            "$or": [
                {"name": {"$regex": query_param, "$options": "i"}},
                {"title": {"$regex": query_param, "$options": "i"}},
                {"filename": {"$regex": query_param, "$options": "i"}}
            ]
        }
    else:
        query = {}  # no filter, fetch all

    # Pagination
    skip = (page - 1) * limit
    cursor = collection.find(query).skip(skip).limit(limit)

    data = []
    for r in cursor:
        r["_id"] = str(r["_id"])
        data.append(r)

    total_count = collection.count_documents(query)
    total_pages = (total_count + limit - 1) // limit

    return jsonify({
        "count": len(data),
        "page": page,
        "total_pages": total_pages,
        "total_count": total_count,
        "results": data
    })
  
