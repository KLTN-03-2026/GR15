from fastapi import APIRouter

from app.schemas.common import BaseAiResponse
from app.schemas.search import SemanticSearchRequest
from app.services.semantic_search import semantic_search_jobs


router = APIRouter()


@router.post("/search/semantic/jobs", response_model=BaseAiResponse)
def semantic_search_jobs_endpoint(payload: SemanticSearchRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **semantic_search_jobs(
            payload.query,
            [document.model_dump() for document in payload.documents],
            payload.top_k,
        )
    )
