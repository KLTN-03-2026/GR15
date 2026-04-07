from pydantic import BaseModel


class BaseAiResponse(BaseModel):
    success: bool
    parser_version: str | None = None
    confidence_score: float | None = None
    model_version: str | None = None
    data: dict
    error: str | None = None
