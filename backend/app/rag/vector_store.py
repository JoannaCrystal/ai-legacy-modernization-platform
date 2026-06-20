from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument
from app.rag.embedding_service import EmbeddingService


class VectorStore:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.embedding_service = EmbeddingService()

    def save_document(
        self,
        title: str,
        content: str,
        category: str,
    ) -> KnowledgeDocument:
        embedding = self.embedding_service.create_embedding(content)

        document = KnowledgeDocument(
            title=title,
            content=content,
            category=category,
            embedding=embedding,
        )
        self.db.add(document)
        self.db.flush()
        return document
