from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    request_id: str
    intent: Optional[str] = None
    response: str
    execution_path: list[str] = Field(default_factory=list)
    data: Optional[Dict[str, Any]] = None
    errors: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str