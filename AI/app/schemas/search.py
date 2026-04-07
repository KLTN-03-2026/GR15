from pydantic import BaseModel, Field


class SemanticDocument(BaseModel):
    entity_id: int
    title: str
    text_content: str
    company_name: str | None = None
    location: str | None = None
    level: str | None = None
    metadata: dict | None = None


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=2)
    top_k: int = Field(default=10, ge=1, le=20)
    documents: list[SemanticDocument] = Field(default_factory=list)
