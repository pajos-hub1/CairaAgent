from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import AIRequest, FollowUpRequest, AIResponse, ConversationHistory, HealthStatus
from .engine import CairaAI_Engine
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Caira Unified AI Engine",
    description="A unified conversational AI assistant for Gmail operations with hybrid workflow support",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the AI engine
try:
    ai_engine = CairaAI_Engine()
except ValueError as e:
    print(f"Failed to initialize AI engine: {e}")
    ai_engine = None


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Caira Unified AI Engine with Hybrid Workflow",
        "version": "2.0.0",
        "workflows": {
            "single_call": "Direct actions like drafting emails, blocking senders",
            "two_call": "Data fetching actions like summarizing emails, answering questions"
        },
        "endpoints": {
            "command": "POST /command - Process initial user command",
            "follow-up": "POST /follow-up - Process follow-up with email data",
            "history": "GET /history/{session_id} - Get conversation history",
            "clear": "DELETE /history/{session_id} - Clear conversation history",
            "health": "GET /health - System health check",
            "sessions": "GET /sessions - List all active conversation sessions"
        }
    }


@app.post("/command", response_model=AIResponse)
def process_initial_command_endpoint(request: AIRequest):
    """
    Endpoint for the user's initial command. This is the first call.
    Determines whether to use single-call or two-call workflow.
    """
    if ai_engine is None:
        raise HTTPException(
            status_code=500,
            detail="AI engine not initialized. Please check your TOGETHER_API_KEY environment variable."
        )

    try:
        response_data = ai_engine.process_initial_command(
            session_id=request.session_id,
            command_text=request.command_text,
            email_context=request.email_context
        )

        if "error" in response_data:
            raise HTTPException(status_code=500, detail=response_data["error"])

        return AIResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/follow-up", response_model=AIResponse)
def process_follow_up_endpoint(request: FollowUpRequest):
    """
    Endpoint for the second call in a two-call workflow.
    Processes email data and provides final response.
    """
    if ai_engine is None:
        raise HTTPException(status_code=500, detail="AI engine not initialized")

    try:
        response_data = ai_engine.process_follow_up(
            session_id=request.session_id,
            follow_up_action=request.follow_up_action,
            email_data=request.email_data,
            original_command=request.original_command
        )

        if "error" in response_data:
            raise HTTPException(status_code=500, detail=response_data["error"])

        return AIResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/history/{session_id}", response_model=ConversationHistory)
def get_conversation_history(session_id: str):
    """
    Get the conversation history for a specific session.
    """
    if ai_engine is None:
        raise HTTPException(status_code=500, detail="AI engine not initialized")

    history = ai_engine.get_conversation_history(session_id)
    return ConversationHistory(
        session_id=session_id,
        history=history,
        total_turns=len(history)
    )


@app.delete("/history/{session_id}")
def clear_conversation_history(session_id: str):
    """
    Clear the conversation history for a specific session.
    """
    if ai_engine is None:
        raise HTTPException(status_code=500, detail="AI engine not initialized")

    cleared = ai_engine.clear_conversation(session_id)
    return {
        "session_id": session_id,
        "cleared": cleared,
        "message": "Conversation history cleared" if cleared else "No history found for this session"
    }


@app.get("/health", response_model=HealthStatus)
def health_check():
    """Health check endpoint with detailed system information."""
    model_info = {}
    if ai_engine:
        model_info = ai_engine.get_model_info()

    return HealthStatus(
        status="healthy" if ai_engine is not None else "unhealthy",
        ai_engine_initialized=ai_engine is not None,
        model_info=model_info
    )


@app.get("/sessions")
def list_active_sessions():
    """List all active conversation sessions."""
    if ai_engine is None:
        raise HTTPException(status_code=500, detail="AI engine not initialized")

    sessions = list(ai_engine.conversations.keys())
    return {
        "active_sessions": sessions,
        "total_sessions": len(sessions)
    }
