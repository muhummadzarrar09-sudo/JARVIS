from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=12000)
    session_id: str | None = Field(default=None, max_length=120)
    use_tools: bool = True
    confirmed: bool = False


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    steps: list[str]
    requires_confirmation: bool = False
    confirmation: dict[str, Any] | None = None
