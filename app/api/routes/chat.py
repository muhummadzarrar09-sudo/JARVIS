from fastapi import APIRouter

from app.agents.orchestrator import orchestrator
from app.models.chat import ChatRequest, ChatResponse
from app.services.model_service import model_service

router = APIRouter(tags=["chat"])


@router.get("/chat/ping")
def chat_ping() -> dict:
    model_status = model_service.status()
    provider = model_status.get("provider", {})
    return {
        "ok": True,
        "chat_ready": True,
        "effective_provider": provider.get("effective_provider"),
        "selected_model": (provider.get("selected_model") or {}).get("name"),
        "loaded_model_count": (model_status.get("loaded_models") or {}).get("count", 0),
        "consistency": model_status.get("consistency"),
        "plain_english": "The chat route is available and ready for shell sends.",
    }


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    result = orchestrator.handle_chat(
        message=payload.message,
        session_id=payload.session_id,
        use_tools=payload.use_tools,
        confirmed=payload.confirmed,
    )
    return ChatResponse(**result)
