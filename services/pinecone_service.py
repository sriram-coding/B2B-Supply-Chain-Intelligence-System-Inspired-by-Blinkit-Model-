import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False


class PineconeService:
    def __init__(self):
        self.pc = None
        self.index = None
        self.model = None
        self._connected = False

        if ST_AVAILABLE:
            try:
                self.model = SentenceTransformer(config.EMBEDDING_MODEL)
            except Exception as e:
                print(f"[SentenceTransformer] Load failed: {e}")

        if PINECONE_AVAILABLE and config.PINECONE_API_KEY:
            try:
                self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
                existing = [i.name for i in self.pc.list_indexes()]
                if config.PINECONE_INDEX_NAME not in existing:
                    self.pc.create_index(
                        name=config.PINECONE_INDEX_NAME,
                        dimension=384,
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                    )
                self.index = self.pc.Index(config.PINECONE_INDEX_NAME)
                self._connected = True
            except Exception as e:
                print(f"[Pinecone] Connection failed: {e}")

    def is_connected(self):
        return self._connected

    def embed(self, text: str):
        if self.model:
            return self.model.encode(text).tolist()
        return [0.0] * 384

    def upsert_documents(self, documents: list):
        """documents: list of dicts with 'id', 'text', 'metadata'"""
        if not self._connected or not self.index:
            return False
        vectors = []
        for doc in documents:
            embedding = self.embed(doc["text"])
            vectors.append({
                "id": doc["id"],
                "values": embedding,
                "metadata": doc.get("metadata", {}),
            })
        if vectors:
            self.index.upsert(vectors=vectors)
        return True

    def query(self, text: str, top_k: int = 5):
        if not self._connected or not self.index:
            return []
        embedding = self.embed(text)
        results = self.index.query(
            vector=embedding, top_k=top_k, include_metadata=True
        )
        return results.get("matches", [])

    def build_context_from_dataframes(self, employees_df, vendors_df, logistics_df, contracts_df):
        """Convert dataframes to documents and upsert."""
        docs = []
        for _, row in employees_df.iterrows():
            text = (
                f"Employee {row['name']} works in {row['department']} department "
                f"as {row['role']} at warehouse {row['warehouse']}. "
                f"They handled {row['projects_handled']} projects, managed {row['clients_managed']} clients, "
                f"completed {row['tasks_completed']} tasks with {row['on_time_delivery_rate']*100:.0f}% on-time delivery rate."
            )
            docs.append({"id": row["employee_id"], "text": text, "metadata": {"type": "employee", "name": row["name"]}})

        for _, row in vendors_df.iterrows():
            text = (
                f"Vendor {row['vendor_name']} supplies {row['category']} category products. "
                f"Contract value is ₹{row['contract_value']:,}. Operates in {row['region']} region."
            )
            docs.append({"id": row["vendor_id"], "text": text, "metadata": {"type": "vendor", "name": row["vendor_name"]}})

        for _, row in logistics_df.iterrows():
            text = (
                f"Logistics partner {row['partner_name']} handles {row['shipments_handled']} shipments "
                f"in {row['region']} region with average delivery time of {row['avg_delivery_time']} minutes."
            )
            docs.append({"id": row["logistics_id"], "text": text, "metadata": {"type": "logistics", "name": row["partner_name"]}})

        for _, row in contracts_df.iterrows():
            text = (
                f"Contract {row['contract_id']} with {row['vendor_name']} worth ₹{row['value']:,}. "
                f"Valid from {row['start_date']} to {row['end_date']}. Status: {row['status']}."
            )
            docs.append({"id": row["contract_id"], "text": text, "metadata": {"type": "contract", "vendor": row["vendor_name"]}})

        return self.upsert_documents(docs)
