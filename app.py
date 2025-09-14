# app.py
import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS

# ----------------------
# MongoDB Configuration
# ----------------------
DATABASE_URI = os.environ.get(
    "DATABASE_URI",
    "mongodb+srv://mrnoobx:DAZCdTczVWyECi04@cluster0.sedgwxy.mongodb.net/?retryWrites=true&w=majority"
)
DATABASE_NAME = os.environ.get("DATABASE_NAME", "mrnoobx")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "Files")

client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# ----------------------
# Flask App
# ----------------------
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for browser use

BASE_DOWNLOAD_URL = os.environ.get("BASE_DOWNLOAD_URL", "https://mango-dl.vercel.app/files")

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "MongoDB API is running 🚀"})

@app.route("/files", methods=["GET"])
def get_files():
    """
    Query Parameters:
    - q: search keyword (optional)
    - page: page number (default=1)
    - limit: number of files per page (default=50)
    """
    q = request.args.get("q", "")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))

    # Build search query
    query = {"$or": [
        {"name": {"$regex": q, "$options": "i"}},
        {"title": {"$regex": q, "$options": "i"}},
        {"filename": {"$regex": q, "$options": "i"}}
    ]} if q else {}

    skip = (page - 1) * limit
    cursor = collection.find(query).skip(skip).limit(limit)

    results = []
    for r in cursor:
        r["_id"] = str(r["_id"])
        # Construct direct download link
        r["direct_link"] = f"{BASE_DOWNLOAD_URL}/{r['_id']}/download"
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

# ----------------------
# Direct Download Endpoint
# ----------------------
@app.route("/files/<file_id>/download", methods=["GET"])
def download_file(file_id):
    """
    Optional: redirect to actual file_path or URL stored in MongoDB
    """
    file_doc = collection.find_one({"_id": file_id})
    if not file_doc:
        return jsonify({"error": "File not found"}), 404

    file_url = file_doc.get("file_path") or file_doc.get("url")
    if not file_url:
        return jsonify({"error": "File URL not found"}), 404

    # For Vercel, redirect to the actual file URL
    return jsonify({"direct_download": file_url})

# ----------------------
# Run locally (for testing)
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
        
