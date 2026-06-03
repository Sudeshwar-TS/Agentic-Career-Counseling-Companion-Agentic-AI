from rag.granite import GraniteLLM
from rag.vector_store import CareerVectorStore


class CareerCounselorRAG:
    def __init__(self):
        self.store = CareerVectorStore()
        self.llm = GraniteLLM()

    def answer(self, question: str, student_context: str) -> dict:
        sources = self.store.search(question)
        context = "\n".join(source["text"] for source in sources)
        prompt = (
            "You are CareerNav AI, an IBM Granite-powered agentic career counselor.\n"
            "Use the knowledge base and student context to give concise, actionable guidance.\n\n"
            f"Student context:\n{student_context}\n\nKnowledge base:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
        )
        return {"answer": self.llm.invoke(prompt), "sources": sources}
