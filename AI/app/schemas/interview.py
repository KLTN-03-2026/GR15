from pydantic import BaseModel, Field


class MockInterviewQuestionRequest(BaseModel):
    session_id: int
    interview_context: dict | None = None
    transcript: list[dict] = Field(default_factory=list)
    question_index: int = Field(default=1, ge=1)
    max_questions: int = Field(default=5, ge=3, le=7)


class MockInterviewAnswerRequest(BaseModel):
    session_id: int
    question_payload: dict
    answer: str = Field(min_length=2)
    interview_context: dict | None = None
    transcript: list[dict] = Field(default_factory=list)
    max_questions: int = Field(default=5, ge=3, le=7)


class MockInterviewReportRequest(BaseModel):
    session_id: int
    interview_context: dict | None = None
    transcript: list[dict] = Field(default_factory=list)
