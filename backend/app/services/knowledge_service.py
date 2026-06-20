from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument
from app.rag.document_loader import DocumentLoader
from app.rag.vector_store import VectorStore


class KnowledgeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.document_loader = DocumentLoader()
        self.vector_store = VectorStore(db)

    def ingest_knowledge_base(self) -> dict[str, int]:
        self.db.query(KnowledgeDocument).delete()

        documents = self.document_loader.load_documents()
        chunks_created = 0

        for document in documents:
            chunks = self.document_loader.chunk_document(document["content"])

            for index, chunk in enumerate(chunks, start=1):
                title = document["title"]
                if len(chunks) > 1:
                    title = f"{document['title']} (Part {index})"

                self.vector_store.save_document(
                    title=title,
                    content=chunk,
                    category=document["category"],
                )
                chunks_created += 1

        self.db.commit()

        return {
            "documents_processed": len(documents),
            "chunks_created": chunks_created,
        }
