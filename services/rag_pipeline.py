import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.pinecone_service import PineconeService
from services.groq_extractor import chat_completion


SYSTEM_PROMPT = """You are BlinkBot, an enterprise AI assistant for Blinkit's Supply Chain Intelligence Platform.
You answer questions about employees, vendors, logistics partners, and contracts using the context provided.
Be concise, professional, and data-driven. If the context doesn't contain the answer, say so clearly.
Format numbers with proper units (₹ for currency, % for rates, etc.)."""


class RAGPipeline:
    def __init__(self, pinecone_service: PineconeService):
        self.pinecone = pinecone_service
        self.chat_history = []

    def query(self, user_question: str, use_history: bool = True) -> str:
        # Step 1: Retrieve relevant context from Pinecone
        context_chunks = []
        if self.pinecone.is_connected():
            matches = self.pinecone.query(user_question, top_k=5)
            for match in matches:
                if match.get("score", 0) > 0.3:
                    meta = match.get("metadata", {})
                    context_chunks.append(
                        f"[{meta.get('type', 'info').upper()}] Score: {match['score']:.2f} | {match['id']}"
                    )
        else:
            context_chunks.append("[Note: Vector DB not connected. Using LLM knowledge only.]")

        context = "\n".join(context_chunks) if context_chunks else "No specific context found."

        # Step 2: Build messages
        messages = []
        if use_history:
            messages.extend(self.chat_history[-6:])  # last 3 turns

        messages.append({
            "role": "user",
            "content": f"Context from knowledge base:\n{context}\n\nQuestion: {user_question}",
        })

        # Step 3: Generate response
        response = chat_completion(messages, system=SYSTEM_PROMPT)

        # Step 4: Update history
        self.chat_history.append({"role": "user", "content": user_question})
        self.chat_history.append({"role": "assistant", "content": response})

        return response

    def reset_history(self):
        self.chat_history = []

    def query_with_dataframe_context(self, user_question: str, df_context: str) -> str:
        """RAG with injected dataframe summaries as context."""
        messages = [
            {
                "role": "user",
                "content": f"Supply chain data context:\n{df_context}\n\nQuestion: {user_question}",
            }
        ]
        return chat_completion(messages, system=SYSTEM_PROMPT)
