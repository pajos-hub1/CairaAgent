#!/usr/bin/env python3
"""
Test script for the Caira AI Engine
Run this to verify the engine is working correctly
"""

import sys
import os
import asyncio
import json

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.engine import CairaAI_Engine
from app.schemas import UserProfile, EmailData


async def test_ai_engine():
    """Test the AI Engine with sample requests"""

    print("🚀 Testing Caira AI Engine...")

    try:
        # Initialize engine
        engine = CairaAI_Engine()
        print("✅ AI Engine initialized successfully")

        # Test connection
        if engine._test_connection():
            print("✅ Together AI connection successful")
        else:
            print("❌ Together AI connection failed")
            return

        # Sample user profile
        user_profile = {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "timezone": "UTC",
            "language": "en"
        }

        # Test 1: One-Call Workflow (Gmail Query)
        print("\n📧 Test 1: Gmail Query Generation")
        request1 = {
            "command_text": "Show me emails from notifications@shopmaster.com",
            "user_profile": user_profile
        }

        response1 = engine.process_request(request1)
        print(f"Response: {json.dumps(response1, indent=2)}")

        # Test 2: Two-Call Workflow (Summarization)
        print("\n📝 Test 2: Email Summarization Workflow")

        # Initial request
        request2_initial = {
            "command_text": "Summarize my emails from HR this week",
            "user_profile": user_profile
        }

        response2_initial = engine.process_request(request2_initial)
        print(f"Initial Response: {json.dumps(response2_initial, indent=2)}")

        # Follow-up request (simulating backend fetching emails)
        if response2_initial.get("action_type") == "FETCH_AND_SUMMARIZE":
            sample_emails = [
                {
                    "subject": "New Work Policy Update",
                    "sender": "hr@company.com",
                    "body": "Dear team, we're implementing a new flexible work policy starting next month. Key changes include: 1) Remote work up to 3 days per week, 2) Flexible hours between 7 AM - 7 PM, 3) New collaboration tools will be provided. Please review the attached document and confirm your preferred schedule by Friday.",
                    "timestamp": "2025-06-28T10:00:00Z"
                },
                {
                    "subject": "Q&A Session - Friday 2 PM",
                    "sender": "hr@company.com",
                    "body": "Hi everyone, we're hosting a Q&A session this Friday at 2 PM in the main conference room to discuss the new work policy. Come with your questions! Light refreshments will be provided. RSVP by Thursday.",
                    "timestamp": "2025-06-29T14:30:00Z"
                }
            ]

            request2_followup = {
                "follow_up_action": "SUMMARIZE_CONTENT",
                "email_data": sample_emails,
                "original_command": "Summarize my emails from HR this week",
                "user_profile": user_profile
            }

            response2_final = engine.process_request(request2_followup)
            print(f"Final Response: {json.dumps(response2_final, indent=2)}")

        # Test 3: Question Answering
        print("\n❓ Test 3: Question Answering")
        request3_initial = {
            "command_text": "What time is the HR Q&A session?",
            "user_profile": user_profile
        }

        response3_initial = engine.process_request(request3_initial)
        print(f"Initial Response: {json.dumps(response3_initial, indent=2)}")

        if response3_initial.get("action_type") == "FETCH_AND_ANSWER":
            request3_followup = {
                "follow_up_action": "ANSWER_QUESTION",
                "email_data": sample_emails,
                "original_command": "What time is the HR Q&A session?",
                "user_profile": user_profile
            }

            response3_final = engine.process_request(request3_followup)
            print(f"Final Response: {json.dumps(response3_final, indent=2)}")

        print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ai_engine())
