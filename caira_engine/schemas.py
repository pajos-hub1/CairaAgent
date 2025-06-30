"""
Caira AI Engine: Data Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class ActionType(str, Enum):
    """Enumeration of possible action types"""
    GMAIL_QUERY_GENERATED = "GMAIL_QUERY_GENERATED"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    FETCH_AND_SUMMARIZE = "FETCH_AND_SUMMARIZE"
    FETCH_AND_ANSWER = "FETCH_AND_ANSWER"
    EXPORT_TO_SHEETS = "EXPORT_TO_SHEETS"
    FINAL_RESPONSE = "FINAL_RESPONSE"

class UserProfile(BaseModel):
    """User profile information"""
    user_id: str
    email: str
    preferences: Optional[Dict[str, Any]] = {}
    timezone: Optional[str] = "UTC"
    language: Optional[str] = "en"

class EmailContext(BaseModel):
    """Context of currently viewed email"""
    subject: Optional[str] = None
    sender: Optional[str] = None
    body: Optional[str] = None
    timestamp: Optional[str] = None
    thread_id: Optional[str] = None

class EmailData(BaseModel):
    """Individual email data structure"""
    subject: str
    sender: str
    body: str
    timestamp: Optional[str] = None
    thread_id: Optional[str] = None
    labels: Optional[List[str]] = []

class InitialRequest(BaseModel):
    """Schema for initial AI Engine requests"""
    command_text: str = Field(..., description="User's natural language command")
    user_profile: UserProfile
    email_context: Optional[EmailContext] = None

class FollowUpRequest(BaseModel):
    """Schema for follow-up AI Engine requests"""
    follow_up_action: str = Field(..., description="Type of follow-up action")
    email_data: List[EmailData] = Field(..., description="Email content to process")
    original_command: str = Field(..., description="Original user command")
    user_profile: UserProfile

class GmailQueryPayload(BaseModel):
    """Payload for Gmail query generation"""
    gmail_search_string: str
    explanation: Optional[str] = None

class ActionRequiredPayload(BaseModel):
    """Payload for direct actions"""
    action: str
    parameters: Dict[str, Any] = {}
    confirmation_required: bool = False

class FetchPayload(BaseModel):
    """Payload for fetch operations"""
    gmail_search_string: str
    max_results: Optional[int] = 10
    include_body: bool = True

class FinalResponsePayload(BaseModel):
    """Payload for final responses"""
    text_response: str
    confidence: Optional[float] = None
    sources: Optional[List[str]] = []

class AIResponse(BaseModel):
    """Standard AI Engine response schema"""
    status: str = Field(default="success", description="Response status")
    action_type: ActionType
    payload: Union[
        GmailQueryPayload,
        ActionRequiredPayload,
        FetchPayload,
        FinalResponsePayload,
        Dict[str, Any]
    ]
    metadata: Optional[Dict[str, Any]] = {}

class ErrorResponse(BaseModel):
    """Error response schema"""
    status: str = "error"
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
