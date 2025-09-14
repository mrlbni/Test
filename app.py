# app.py
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

app = Flask(__name__)
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "MongoDB API is running 🚀"})
    
@app.route("/files", methods=["GET"])
def get_files():
    q = request.args.get("q", "")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))

    query = {"$or":[
        {"name": {"$regex": q, "$options": "i"}},
        {"title": {"$regex": q, "$options": "i"}},
        {"filename": {"$regex": q, "$options": "i"}}
    ]} if q else {}

    skip = (page - 1) * limit
    cursor = collection.find(query).skip(skip).limit(limit)

    results = []
    for r in cursor:
        r["_id"] = str(r["_id"])
        results.append(r)

    total_count = collection.count_documents(query)
    total_pages = (total_count + limit - 1) // limit

    return jsonify({
        "count": len(results),
        "page": page,
        "total_pages": total_pages,
        "total_count": total_count,
        "results": results
    })
    
