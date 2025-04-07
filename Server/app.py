# app.py
from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from database import SessionLocal
from initialize_db import init_db
from models import User, Memory, History
import uuid
from sqlalchemy import text
import logging
import re

def calculate_rank(content, query):
    # Extract words from the query
    query_words = re.findall(r'\w+', query.lower())
    # Extract words from the content
    content_words = re.findall(r'\w+', content.lower())
    # Count the number of query words present in the content
    match_count = sum(content_words.count(word) for word in query_words)
    return match_count

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the database
init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper Functions
def get_or_create_user(db: Session, user_id: str, meta=None):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        user = User(user_id=user_id, meta=meta)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# API Endpoints

# --- Memory Endpoints ---

@app.route("/memories/add", methods=["POST"])
def add_memory():
    data = request.get_json()
    content = data.get("content")
    user_id = data.get("user_id")
    metadata = data.get("metadata")

    if not content:
        return jsonify({"error": "Content is required."}), 400

    memory_id = f"mem_{uuid.uuid4().hex[:8]}"

    db_gen = get_db()
    db = next(db_gen)

    user = get_or_create_user(db, user_id) if user_id else None

    memory = Memory(
        memory_id=memory_id,
        user_id=user.id if user else None,
        content=content,
        meta=metadata
    )
    db.add(memory)

    # Add entry to FTS5 virtual table
    try:
        db.execute(text("""
            INSERT INTO memories_fts (content, memory_id) VALUES (:content, :memory_id)
        """), {"content": content, "memory_id": memory_id})
    except Exception as e:
        logger.error(f"Failed to insert into FTS5 table: {e}")
        return jsonify({"error": "Failed to add memory to search index."}), 500

    db.commit()
    db.refresh(memory)

    logger.info(f"Memory '{memory_id}' added successfully.")

    return jsonify({"memory_id": memory_id, "status": "success"}), 201

@app.route("/memories/update", methods=["PUT"])
def update_memory():
    data = request.get_json()
    memory_id = data.get("memory_id")
    new_content = data.get("new_content")

    if not memory_id or not new_content:
        return jsonify({"error": "memory_id and new_content are required."}), 400

    db_gen = get_db()
    db = next(db_gen)

    memory = db.query(Memory).filter(Memory.memory_id == memory_id).first()
    if not memory:
        return jsonify({"error": "Memory not found."}), 404

    # Save history
    history = History(
        memory_id=memory.id,
        prev_value=memory.content,
        new_value=new_content
    )
    db.add(history)

    # Update memory content
    memory.content = new_content

    # Update FTS5 virtual table
    try:
        db.execute(text("""
            UPDATE memories_fts SET content = :new_content WHERE memory_id = :memory_id
        """), {"new_content": new_content, "memory_id": memory_id})
    except Exception as e:
        logger.error(f"Failed to update FTS5 table: {e}")
        return jsonify({"error": "Failed to update memory in search index."}), 500

    db.commit()
    db.refresh(memory)

    logger.info(f"Memory '{memory_id}' updated successfully.")

    return jsonify({"memory_id": memory_id, "status": "updated"}), 200

@app.route("/memories/search", methods=["GET"])
def search_memories():
    query = request.args.get("query")
    user_id = request.args.get("user_id")

    if not query:
        logger.warning("Search attempt without query parameter.")
        return jsonify({"error": "Query parameter is required."}), 400

    db_gen = get_db()
    db = next(db_gen)

    # Sanitize the input by escaping single quotes to prevent SQL injection
    sanitized_query = query.replace("'", "''")
    sanitized_query = f'"{sanitized_query}"'

    # Stage 1: Perform FTS search to get memory_ids from content and meta
    fts_query = f"""
        SELECT memory_id
        FROM memories_fts
        WHERE content MATCH '{sanitized_query}'
        ORDER BY rowid ASC  -- Default ordering
    """

    try:
        logger.info(f"Executing FTS search query:\n{fts_query}")
        fts_result = db.execute(text(fts_query))
    except Exception as e:
        logger.error(f"Error during FTS search execution: {e}")
        return jsonify({"error": "An error occurred while searching memories."}), 500

    # Extract memory_ids from the result
    memory_ids = [row[0] for row in fts_result]

    if not memory_ids:
        logger.info("No memories found matching the query.")
        return jsonify({"memories": []}), 200

    # Stage 2: Fetch memory details for the found memory_ids
    memories_query = db.query(Memory).filter(Memory.memory_id.in_(memory_ids))
    if user_id:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            logger.info(f"No user found with user_id: {user_id}")
            return jsonify({"memories": []}), 200
        memories_query = memories_query.filter(Memory.user_id == user.id)

    memories = memories_query.all()

    # Calculate rank based on keyword matches
    response_memories = [
        {
            "memory_id": mem.memory_id,
            "user": mem.user.user_id if mem.user else None,
            "content": mem.content,
            "metadata": mem.meta,
            "score": calculate_rank(mem.content, query)  # Custom rank
        }
        for mem in memories
    ]

    # Sort the results by rank descending (more matches first)
    response_memories.sort(key=lambda x: x['score'], reverse=True)

    logger.info(f"Search completed. Found {len(response_memories)} memory/memories.")

    return jsonify({"memories": response_memories}), 200

@app.route("/memories/all", methods=["GET"])
def get_all_memories():
    user_id = request.args.get("user_id")

    db_gen = get_db()
    db = next(db_gen)

    memories_query = db.query(Memory)

    if user_id:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            memories_query = memories_query.filter(Memory.user_id == user.id)

    memories = memories_query.all()

    response_memories = [
        {
            "memory_id": mem.memory_id,
            "content": mem.content,
            "metadata": mem.meta,
            "created_at": mem.created_at.isoformat(),
            "updated_at": mem.updated_at.isoformat()
        }
        for mem in memories
    ]

    return jsonify({"memories": response_memories}), 200

@app.route("/memories/history/<memory_id>", methods=["GET"])
def get_memory_history(memory_id):
    db_gen = get_db()
    db = next(db_gen)

    memory = db.query(Memory).filter(Memory.memory_id == memory_id).first()
    if not memory:
        return jsonify({"error": "Memory not found."}), 404

    history_records = db.query(History).filter(History.memory_id == memory.id).order_by(History.updated_at.desc()).all()

    response_history = [
        {
            "prev_value": record.prev_value,
            "new_value": record.new_value,
            "updated_at": record.updated_at.isoformat()
        }
        for record in history_records
    ]

    return jsonify({"history": response_history}), 200

# --- User Endpoints ---

@app.route("/users/add", methods=["POST"])
def add_user():
    data = request.get_json()
    user_id = data.get("user_id")
    meta = data.get("metadata")

    if not user_id:
        return jsonify({"error": "user_id is required."}), 400

    db_gen = get_db()
    db = next(db_gen)

    existing_user = db.query(User).filter(User.user_id == user_id).first()
    if existing_user:
        return jsonify({"error": "User already exists."}), 400

    user = User(user_id=user_id, meta=meta)
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"User '{user.user_id}' added successfully.")

    return jsonify({"user_id": user.user_id, "status": "success"}), 201

@app.route("/users/search", methods=["GET"])
def search_users():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id parameter is required."}), 400

    db_gen = get_db()
    db = next(db_gen)

    users = db.query(User).filter(User.user_id.contains(user_id)).all()

    response_users = [
        {
            "user_id": user.user_id,
            "metadata": user.meta,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]

    return jsonify({"users": response_users}), 200

@app.route("/users/all", methods=["GET"])
def list_all_users():
    db_gen = get_db()
    db = next(db_gen)

    users = db.query(User).all()

    response_users = [
        {
            "user_id": user.user_id,
            "metadata": user.meta,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]

    return jsonify({"users": response_users}), 200

# --- Run the Flask app ---
if __name__ == "__main__":
    app.run(debug=True)
