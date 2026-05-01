from fastapi import APIRouter

from app.schemas.common import BaseAiResponse
from app.schemas.interview import (
    InterviewCopilotEvaluateRequest,
    InterviewCopilotGenerateRequest,
    MockInterviewAnswerRequest,
    MockInterviewQuestionRequest,
    MockInterviewReportRequest,
)
from app.services.interview_copilot import (
    evaluate_interview_copilot,
    generate_interview_copilot,
)
from app.services.mock_interview import (
    evaluate_mock_interview_answer,
    generate_mock_interview_question,
    generate_mock_interview_report,
)


router = APIRouter()


@router.post("/interview/mock/question", response_model=BaseAiResponse)
def generate_mock_interview_question_endpoint(payload: MockInterviewQuestionRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **generate_mock_interview_question(
            payload.session_id,
            interview_context=payload.interview_context,
            transcript=payload.transcript,
            question_index=payload.question_index,
            max_questions=payload.max_questions,
        )
    )


@router.post("/interview/mock/evaluate", response_model=BaseAiResponse)
def evaluate_mock_interview_answer_endpoint(payload: MockInterviewAnswerRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **evaluate_mock_interview_answer(
            payload.session_id,
            question_payload=payload.question_payload,
            answer=payload.answer,
            interview_context=payload.interview_context,
            transcript=payload.transcript,
            max_questions=payload.max_questions,
        )
    )


@router.post("/interview/mock/report", response_model=BaseAiResponse)
def generate_mock_interview_report_endpoint(payload: MockInterviewReportRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **generate_mock_interview_report(
            payload.session_id,
            interview_context=payload.interview_context,
            transcript=payload.transcript,
        )
    )


@router.post("/interview/copilot/generate", response_model=BaseAiResponse)
def generate_interview_copilot_endpoint(payload: InterviewCopilotGenerateRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **generate_interview_copilot(
            payload.ung_tuyen_id,
            application_context=payload.application_context,
        )
    )


@router.post("/interview/copilot/evaluate", response_model=BaseAiResponse)
def evaluate_interview_copilot_endpoint(payload: InterviewCopilotEvaluateRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **evaluate_interview_copilot(
            payload.ung_tuyen_id,
            application_context=payload.application_context,
            interview_notes=payload.interview_notes,
        )
    )
