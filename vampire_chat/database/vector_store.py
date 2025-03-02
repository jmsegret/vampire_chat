from typing import List, Dict, Optional
import numpy as np
from datetime import datetime
import faiss
from sentence_transformers import SentenceTransformer
import json
import os

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.messages = []
        self.index_path = "vampire_chat/database/vector_index"
        self.messages_path = "vampire_chat/database/vector_messages.json"
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create a new one."""
        if os.path.exists(self.index_path) and os.path.exists(self.messages_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.messages_path, 'r') as f:
                self.messages = json.load(f)
        else:
            # Initialize a new index
            embedding_dim = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(embedding_dim)
            self.messages = []

    def _save_index(self):
        """Save the current index and messages to disk."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.messages_path, 'w') as f:
            json.dump(self.messages, f)

    def add_message(self, message: Dict):
        """Add a new message to the vector store."""
        # Create embedding for the message content
        embedding = self.model.encode([message["content"]])[0]
        
        # Add to FAISS index
        self.index.add(np.array([embedding]).astype('float32'))
        
        # Store message with metadata
        self.messages.append({
            "id": message.get("message_id"),
            "conversation_id": message.get("conversation_id"),
            "role": message.get("role"),
            "content": message.get("content"),
            "timestamp": message.get("timestamp", str(datetime.now()))
        })
        
        # Save to disk
        self._save_index()

    def search_similar_messages(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar messages using the query."""
        if self.index.ntotal == 0:
            return []

        # Create query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Search in FAISS index
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'), 
            min(k, self.index.ntotal)
        )
        
        # Return relevant messages
        results = []
        for idx in indices[0]:
            if idx != -1:  # Valid index
                results.append(self.messages[idx])
        
        return results

    def get_relevant_context(self, query: str, max_messages: int = 5) -> str:
        """Get relevant context from previous messages for a query."""
        similar_messages = self.search_similar_messages(query, k=max_messages)
        
        if not similar_messages:
            return ""
        
        # Format context
        context = "Related previous messages:\n\n"
        for msg in similar_messages:
            context += f"{msg['role']}: {msg['content']}\n"
        
        return context
