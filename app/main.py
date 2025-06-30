"""
Caira AI Engine: FastAPI Server
Main entry point for the AI Engine service
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict, Any
import os
from dotenv import load_dotenv

from .engine import CairaAI_Engine
from .schemas import InitialRequest, FollowUpRequest, AIResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Caira AI Engine",
    description="Intelligent email assistant AI engine with hybrid workflow",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Engine
ai_engine = CairaAI_Engine()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Caira AI Engine",
        "version": "2.0.0",
        "status": "operational",
        "workflow_model": "hybrid"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test AI engine initialization
        test_response = ai_engine._test_connection()
        return {
            "status": "healthy",
            "ai_engine": "connected" if test_response else "disconnected",
            "model": "Together AI + Llama",
            "timestamp": "2025-06-30T14:21:47Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/api/v1/ai-engine/process", response_model=AIResponse)
async def process_request(request: InitialRequest | FollowUpRequest):
    """
    Main processing endpoint for both initial and follow-up requests
    Handles the hybrid workflow model
    """
    try:
        logger.info(f"Processing request type: {type(request).__name__}")

        # Convert request to dict for processing
        request_data = request.model_dump()

        # Process through AI engine
        response = ai_engine.process_request(request_data)

        logger.info(f"Generated response with action_type: {response.get('action_type')}")
        return response

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI Engine processing error: {str(e)}"
        )


@app.post("/api/v1/ai-engine/follow-up", response_model=AIResponse)
async def process_follow_up(request: FollowUpRequest):
    """
    Dedicated endpoint for follow-up requests (optional alternative)
    """
    try:
        logger.info("Processing follow-up request")

        request_data = request.model_dump()
        response = ai_engine._handle_follow_up_request(request_data)

        logger.info("Follow-up request processed successfully")
        return response

    except Exception as e:
        logger.error(f"Error processing follow-up request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Follow-up processing error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
