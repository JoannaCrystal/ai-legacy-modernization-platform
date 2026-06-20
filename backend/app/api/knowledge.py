from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.rag.retriever import KnowledgeRetriever
from app.schemas.knowledge import (
    KnowledgeIngestResponse,
    KnowledgeSearchResult,
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/ingest", response_model=KnowledgeIngestResponse)
def ingest_knowledge_base(
    db: Session = Depends(get_db),
) -> KnowledgeIngestResponse:
    service = KnowledgeService(db)
    result = service.ingest_knowledge_base()
    return KnowledgeIngestResponse(**result)


@router.get("/search", response_model=list[KnowledgeSearchResult])
def search_knowledge(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> list[KnowledgeSearchResult]:
    retriever = KnowledgeRetriever(db)
    results = retriever.retrieve(query)
    return [
        KnowledgeSearchResult(
            title=result["title"],
            content=result["content"],
        )
        for result in results
    ]
