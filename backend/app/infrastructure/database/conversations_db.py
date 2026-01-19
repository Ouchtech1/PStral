"""
Conversations database for Pstral.
Centralizes chat history storage for multi-user access.
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "conversations.db")


class Message(BaseModel):
    role: str
    content: str
    images: Optional[List[str]] = None
    timestamp: Optional[str] = None


class Conversation(BaseModel):
    id: str
    user_id: int
    title: str
    mode: str
    messages: List[Message]
    created_at: str
    updated_at: str


class ConversationSummary(BaseModel):
    id: str
    title: str
    mode: str
    message_count: int
    created_at: str
    updated_at: str


def init_conversations_db():
    """Initialize the conversations database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT,
            mode TEXT,
            messages TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_updated ON conversations(updated_at)")
    
    conn.commit()
    conn.close()


def create_conversation(user_id: int, conversation_id: str, mode: str, title: str = "Nouvelle discussion") -> Conversation:
    """Create a new conversation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO conversations (id, user_id, title, mode, messages, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (conversation_id, user_id, title, mode, json.dumps([]), now, now))
    
    conn.commit()
    conn.close()
    
    return Conversation(
        id=conversation_id,
        user_id=user_id,
        title=title,
        mode=mode,
        messages=[],
        created_at=now,
        updated_at=now
    )


def get_conversation(conversation_id: str, user_id: int) -> Optional[Conversation]:
    """Get a conversation by ID, ensuring it belongs to the user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, user_id, title, mode, messages, created_at, updated_at
        FROM conversations
        WHERE id = ? AND user_id = ?
    """, (conversation_id, user_id))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        messages_raw = json.loads(row[4])
        messages = [Message(**m) for m in messages_raw]
        return Conversation(
            id=row[0],
            user_id=row[1],
            title=row[2],
            mode=row[3],
            messages=messages,
            created_at=row[5],
            updated_at=row[6]
        )
    return None


def get_user_conversations(user_id: int, limit: int = 50) -> List[ConversationSummary]:
    """Get all conversations for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, mode, messages, created_at, updated_at
        FROM conversations
        WHERE user_id = ?
        ORDER BY updated_at DESC
        LIMIT ?
    """, (user_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    summaries = []
    for row in rows:
        messages = json.loads(row[3])
        summaries.append(ConversationSummary(
            id=row[0],
            title=row[1],
            mode=row[2],
            message_count=len(messages),
            created_at=row[4],
            updated_at=row[5]
        ))
    
    return summaries


def update_conversation(conversation_id: str, user_id: int, messages: List[dict], title: Optional[str] = None) -> bool:
    """Update a conversation's messages and optionally its title."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    if title:
        cursor.execute("""
            UPDATE conversations
            SET messages = ?, title = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (json.dumps(messages), title, now, conversation_id, user_id))
    else:
        cursor.execute("""
            UPDATE conversations
            SET messages = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (json.dumps(messages), now, conversation_id, user_id))
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return updated


def delete_conversation(conversation_id: str, user_id: int) -> bool:
    """Delete a conversation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM conversations
        WHERE id = ? AND user_id = ?
    """, (conversation_id, user_id))
    
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return deleted


def search_conversations(user_id: int, query: str, limit: int = 20) -> List[ConversationSummary]:
    """Search conversations by title or content."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Search in title and messages content
    cursor.execute("""
        SELECT id, title, mode, messages, created_at, updated_at
        FROM conversations
        WHERE user_id = ? AND (title LIKE ? OR messages LIKE ?)
        ORDER BY updated_at DESC
        LIMIT ?
    """, (user_id, f"%{query}%", f"%{query}%", limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    summaries = []
    for row in rows:
        messages = json.loads(row[3])
        summaries.append(ConversationSummary(
            id=row[0],
            title=row[1],
            mode=row[2],
            message_count=len(messages),
            created_at=row[4],
            updated_at=row[5]
        ))
    
    return summaries

