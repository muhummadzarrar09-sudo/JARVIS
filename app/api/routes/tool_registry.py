from fastapi import APIRouter

from app.services.tool_registry import tool_registry

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/registry")
def registry() -> dict:
    items = tool_registry.list_tools()
    return {"items": items, "count": len(items)}
