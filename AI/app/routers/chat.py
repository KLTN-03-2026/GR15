from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import CareerChatRequest
from app.schemas.common import BaseAiResponse
from app.services.chatbot import generate_career_chat_reply, stream_career_chat_reply


router = APIRouter()


@router.post("/chat/career-consultant", response_model=BaseAiResponse)
def career_chat_endpoint(payload: CareerChatRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **generate_career_chat_reply(
            payload.session_id,
            payload.message,
            history=payload.history,
            context=payload.context,
            force_model=payload.force_model,
        )
    )


@router.post("/chat/career-consultant/stream")
def career_chat_stream_endpoint(payload: CareerChatRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_career_chat_reply(
            payload.session_id,
            payload.message,
            history=payload.history,
            context=payload.context,
            force_model=payload.force_model,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
