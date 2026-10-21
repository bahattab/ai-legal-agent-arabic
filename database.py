import os
import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH

def get_connection():
    folder = os.path.dirname(DATABASE_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            role TEXT,
            content TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)
    
    conn.commit()
    conn.close()

def create_conversation(title=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (title) VALUES (?)", (title,))
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conversation_id

def save_message(conversation_id, role, content, metadata=None):
    conn = get_connection()
    cursor = conn.cursor()
    metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content, metadata) VALUES (?, ?, ?, ?)",
        (conversation_id, role, content, metadata_json)
    )
    conn.commit()
    conn.close()

def get_conversations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.title, c.created_at, 
               (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY id LIMIT 1) as first_message
        FROM conversations c 
        ORDER BY c.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_conversation_messages(conversation_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY id",
        (conversation_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
