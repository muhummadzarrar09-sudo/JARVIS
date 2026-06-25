from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.model_service import model_service

router = APIRouter(prefix="/models", tags=["models"])


class ModelConfigureRequest(BaseModel):
    provider: str = Field(..., max_length=40)
    fast_model: str | None = Field(default=None, max_length=255)
    main_model: str | None = Field(default=None, max_length=255)


class ModelVerifyRequest(BaseModel):
    slot: str = Field(default="fast", pattern="^(fast|main)$")
    prompt: str | None = Field(default=None, max_length=400)
    expected: str | None = Field(default=None, max_length=200)


@router.get("/status")
def model_status() -> dict:
    return model_service.status()


@router.post("/configure")
def configure_models(payload: ModelConfigureRequest) -> dict:
    return model_service.configure_provider(
        provider=payload.provider,
        fast_model=payload.fast_model,
        main_model=payload.main_model,
    )


@router.post("/use-local")
def use_local_models() -> dict:
    return model_service.configure_local_models()


@router.post("/use-mock")
def use_mock_models() -> dict:
    return model_service.configure_mock_mode()


@router.post("/preload")
def preload_model(slot: str = Query(default="fast", pattern="^(fast|main)$")) -> dict:
    return model_service.preload_selected_model(slot=slot)


@router.post("/verify")
def verify_model_runtime(payload: ModelVerifyRequest) -> dict:
    return model_service.verify_runtime(slot=payload.slot, prompt=payload.prompt, expected=payload.expected)


@router.post("/unload")
def unload_model_runtime() -> dict:
    return model_service.unload_runtime_cache()
