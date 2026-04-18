from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.schemas.expense import Expense
from uuid import uuid4


class ValidationError(BaseModel):
    type: str
    message: str


class AgentState(BaseModel):
    user_input: Optional[str] = None
    transcribed_text: Optional[str] = None
    intent: Optional[str] = None
    expense: Optional[Expense] = None
    notion_result: Optional[Dict[str, Any]] = None
    summary_result: Optional[Dict[str, Any]] = None
    response: Optional[str] = None
    execution_path: list[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    validated: bool = False
    validation_error: Optional[ValidationError] = None
    request_id: str = Field(default_factory=lambda: str(uuid4()))

