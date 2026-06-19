from fastapi import APIRouter

from app.agents.orchestrator import orchestrator
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    result = orchestrator.handle_chat(
        message=payload.message,
        session_id=payload.session_id,
        use_tools=payload.use_tools,
    )
    return ChatResponse(**result)
