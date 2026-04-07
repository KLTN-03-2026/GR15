from pydantic import BaseModel, Field


class CareerChatRequest(BaseModel):
    session_id: int
    message: str = Field(min_length=2)
    history: list[dict] = Field(default_factory=list)
    context: dict | None = None
    force_model: bool = False
