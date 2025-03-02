from typing import List, Dict, Optional
import uuid
from datetime import datetime

from ..database.db_manager import DatabaseManager
from ..database.vector_store import VectorStore

class ChatHistoryManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.vector_store = VectorStore()
        self.current_conversation_id = None

    def start_new_conversation(self) -> str:
        """Start a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        self.current_conversation_id = conversation_id
        self.db_manager.create_conversation(conversation_id)
        return conversation_id

    def add_message(self, role: str, content: str) -> None:
        """Add a message to both SQLite and vector storage."""
        if not self.current_conversation_id:
            self.start_new_conversation()

        message_id = str(uuid.uuid4())
        message = {
            "message_id": message_id,
            "conversation_id": self.current_conversation_id,
            "role": role,
            "content": content,
            "timestamp": str(datetime.now())
        }

        # Add to SQLite database
        self.db_manager.add_message(
            conversation_id=self.current_conversation_id,
            role=role,
            content=content,
            message_id=message_id
        )

        # Add to vector store
        self.vector_store.add_message(message)

    def get_conversation_history(self, limit: Optional[int] = None) -> List[List[str]]:
        """Get the current conversation history formatted for Gradio chatbot."""
        if not self.current_conversation_id:
            return []
        
        messages = self.db_manager.get_conversation_history(
            self.current_conversation_id,
            limit=limit
        )
        
        # Format messages for Gradio chatbot [[user_msg, bot_msg], ...]
        chat_history = []
        current_pair = []
        
        for msg in messages:
            if msg["role"] == "user":
                if current_pair:  # If we have an incomplete pair, add it
                    chat_history.append([current_pair[0], ""])
                current_pair = [msg["content"]]
            elif msg["role"] == "assistant":
                if current_pair:  # Complete the pair
                    current_pair.append(msg["content"])
                    chat_history.append(current_pair)
                    current_pair = []
                else:  # Assistant message without a user message
                    chat_history.append(["", msg["content"]])
        
        # Add any remaining incomplete pair
        if current_pair:
            chat_history.append([current_pair[0], ""])
        
        return chat_history

    def get_relevant_context(self, query: str, max_messages: int = 5) -> str:
        """Get relevant context from previous conversations."""
        return self.vector_store.get_relevant_context(query, max_messages)

    def load_conversation(self, conversation_id: str) -> None:
        """Load an existing conversation."""
        self.current_conversation_id = conversation_id

    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get list of recent conversations."""
        return self.db_manager.get_recent_conversations(limit)

    def format_conversation_for_openai(self, include_context: bool = True) -> List[Dict]:
        """Format conversation history for OpenAI API."""
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": "You are a vampire named Lilly, a friendly teenage vampire who loves chatting with children."
        })
        
        # Get conversation history from database
        history = self.db_manager.get_conversation_history(self.current_conversation_id)
        
        # Add messages from history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return messages
