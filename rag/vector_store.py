import hashlib
import json
import math
from pathlib import Path

try:
    import chromadb
    from chromadb.api.types import EmbeddingFunction
except ModuleNotFoundError:
    chromadb = None

    class EmbeddingFunction:
        pass

from config import settings


class LocalEmbedding(EmbeddingFunction):
    def __call__(self, input):
        vectors = []
        for text in input:
            vector = [0.0] * 96
            for token in text.lower().split():
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                vector[digest[0] % 96] += 1.0
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors


class CareerVectorStore:
    def __init__(self):
        self.docs = json.loads(Path("data/knowledge.json").read_text(encoding="utf-8"))
        if chromadb is None:
            self.collection = None
            return
        self.client = chromadb.PersistentClient(path=settings().chroma_path)
        self.collection = self.client.get_or_create_collection(
            name="career_knowledge",
            embedding_function=LocalEmbedding(),
            metadata={"hnsw:space": "cosine"},
        )
        self.seed()

    def seed(self):
        if self.collection is None:
            return
        if self.collection.count() > 0:
            return
        self.collection.add(ids=[doc["id"] for doc in self.docs], documents=[doc["text"] for doc in self.docs])

    def search(self, query: str, limit: int = 4) -> list[dict]:
        if self.collection is None:
            words = {word.lower().strip(",.?") for word in query.split() if len(word) > 2}
            scored = []
            for doc in self.docs:
                score = sum(1 for word in words if word in doc["text"].lower())
                scored.append((score, doc))
            scored.sort(key=lambda item: item[0], reverse=True)
            return [doc for _, doc in scored[:limit]]
        result = self.collection.query(query_texts=[query], n_results=limit)
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        return [{"id": doc_id, "text": text} for doc_id, text in zip(ids, documents)]
