from pydantic import BaseModel
from typing import Dict, Any, Literal, List, Union

# --- Model for Incoming Requests ---
# A single, unified request model
class AIRequest(BaseModel):
    session_id: str
    command_text: str
    email_context: Dict[str, Any] | None = None

# This model is for the second call in a two-call workflow
class FollowUpRequest(BaseModel):
    session_id: str
    follow_up_action: Literal["SUMMARIZE_CONTENT", "ANSWER_QUESTION"]
    email_data: List[Dict[str, Any]]
    original_command: str

# --- Models for Outgoing Responses ---
class AIResponse(BaseModel):
    status: str = "success"
    action_type: str  # We keep this general to allow for all possibilities
    payload: Dict[str, Any]

# --- Additional helper models ---
class ConversationHistory(BaseModel):
    session_id: str
    history: List[Dict[str, Any]]
    total_turns: int

class HealthStatus(BaseModel):
    status: str
    ai_engine_initialized: bool
    model_info: Dict[str, str]
