import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "vampire_chat/database/chat_history.db"):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
                )
            """)
            
            conn.commit()

    def create_conversation(self, conversation_id: str) -> None:
        """Create a new conversation."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (conversation_id) VALUES (?)",
                (conversation_id,)
            )
            conn.commit()

    def add_message(self, conversation_id: str, role: str, content: str, message_id: str) -> None:
        """Add a new message to a conversation."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO messages (message_id, conversation_id, role, content)
                   VALUES (?, ?, ?, ?)""",
                (message_id, conversation_id, role, content)
            )
            
            # Update conversation last_updated timestamp
            cursor.execute(
                """UPDATE conversations 
                   SET last_updated = CURRENT_TIMESTAMP 
                   WHERE conversation_id = ?""",
                (conversation_id,)
            )
            conn.commit()

    def get_conversation_history(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve conversation history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT role, content, timestamp 
                FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp ASC
            """
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (conversation_id,))
            messages = cursor.fetchall()
            
            return [
                {
                    "role": msg[0],
                    "content": msg[1],
                    "timestamp": msg[2]
                }
                for msg in messages
            ]

    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversations."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT conversation_id, created_at, last_updated 
                   FROM conversations 
                   ORDER BY last_updated DESC 
                   LIMIT ?""",
                (limit,)
            )
            conversations = cursor.fetchall()
            
            return [
                {
                    "conversation_id": conv[0],
                    "created_at": conv[1],
                    "last_updated": conv[2]
                }
                for conv in conversations
            ]
