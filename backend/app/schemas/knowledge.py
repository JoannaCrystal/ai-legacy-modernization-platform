from pydantic import BaseModel


class KnowledgeIngestResponse(BaseModel):
    documents_processed: int
    chunks_created: int


class KnowledgeSearchResult(BaseModel):
    title: str
    content: str
