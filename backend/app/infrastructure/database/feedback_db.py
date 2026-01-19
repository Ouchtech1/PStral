import sqlite3
import logging
from datetime import datetime

DB_FILE = "feedback.db"
logger = logging.getLogger("feedback_db")

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_question TEXT NOT NULL,
                agent_answer TEXT NOT NULL,
                rating TEXT NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        logger.info("Feedback database initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize feedback database: {e}")

def add_feedback(user_question: str, agent_answer: str, rating: str, reason: str = None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (user_question, agent_answer, rating, reason)
            VALUES (?, ?, ?, ?)
        """, (user_question, agent_answer, rating, reason))
        conn.commit()
        fs_id = cursor.lastrowid
        conn.close()
        logger.info(f"Feedback saved with ID: {fs_id}")
        return fs_id
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        raise e
