from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument
from app.rag.embedding_service import EmbeddingService


class KnowledgeRetriever:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.embedding_service = EmbeddingService()

    def retrieve(self, query: str, limit: int = 3) -> list[dict]:
        query_embedding = self.embedding_service.create_embedding(query)
        distance_expr = KnowledgeDocument.embedding.l2_distance(query_embedding)

        rows = (
            self.db.query(KnowledgeDocument, distance_expr.label("distance"))
            .order_by(distance_expr)
            .limit(limit)
            .all()
        )

        results: list[dict] = []
        for document, distance in rows:
            results.append(
                {
                    "title": document.title,
                    "content": document.content,
                    "score": 1 / (1 + float(distance)),
                }
            )

        return results
