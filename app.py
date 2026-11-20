
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import os
import json
import uuid
import hashlib

load_dotenv()

app = Flask(__name__)

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DATABASE_NAME", "flask_todo_db")]
todo_collection = db["todo_items"]


@app.route("/")
def home():
    todos = list(todo_collection.find())

    for todo in todos:
        todo["_id"] = str(todo["_id"])

    return render_template("index.html", todos=todos)


@app.route("/api")
def api():
    with open("data/items.json", "r") as file:
        data = json.load(file)

    return jsonify(data)


@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    item_name = request.form.get("itemName") or (
        request.json.get("itemName") if request.is_json else None
    )

    item_description = request.form.get("itemDescription") or (
        request.json.get("itemDescription") if request.is_json else None
    )

    if not item_name or not item_description:
        return jsonify({
            "success": False,
            "message": "Item name and description are required"
        }), 400

    todo = {
        "itemName": item_name,
        "itemDescription": item_description,
        "itemId": str(uuid.uuid4())[:8],
        "itemUUID": str(uuid.uuid4()),
        "itemHash": hashlib.sha256(
            f"{item_name}{item_description}".encode()
        ).hexdigest()
    }

    result = todo_collection.insert_one(todo)

    return jsonify({
        "success": True,
        "message": "To-Do item saved successfully",
        "id": str(result.inserted_id)
    }), 201


if __name__ == "__main__":
    app.run(debug=True)
