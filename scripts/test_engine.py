#!/usr/bin/env python3
"""
Test script for the Caira AI Engine API using Together AI's Mistral model
Run this script to test the conversational flow
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test-conversation-123"


def test_api():
    print("🚀 Testing Caira AI Engine API with Together AI Mistral")
    print("=" * 60)

    # Test health check first
    print("\n🏥 Health Check")
    health_response = requests.get(f"{BASE_URL}/health")
    if health_response.status_code == 200:
        health_data = health_response.json()
        print(f"✅ Status: {health_data['status']}")
        print(f"🤖 AI Engine: {'Initialized' if health_data['ai_engine_initialized'] else 'Not Initialized'}")
    else:
        print(f"❌ Health check failed: {health_response.status_code}")
        return

    # Test 1: Initial draft request
    print("\n📝 Test 1: Initial Email Draft")
    response1 = requests.post(f"{BASE_URL}/process", json={
        "session_id": SESSION_ID,
        "command_text": "Write an email to Sarah about the project delay."
    })

    if response1.status_code == 200:
        result1 = response1.json()
        print(f"✅ Status: {result1['status']}")
        print(f"📧 Action: {result1['action_type']}")
        print(f"📄 Payload: {json.dumps(result1['payload'], indent=2)}")
    else:
        print(f"❌ Error: {response1.status_code} - {response1.text}")
        return

    time.sleep(1)

    # Test 2: Follow-up modification
    print("\n🔄 Test 2: Update the Draft")
    response2 = requests.post(f"{BASE_URL}/process", json={
        "session_id": SESSION_ID,
        "command_text": "Set the new timeline to March 6th."
    })

    if response2.status_code == 200:
        result2 = response2.json()
        print(f"✅ Status: {result2['status']}")
        print(f"📧 Action: {result2['action_type']}")
        print(f"📄 Payload: {json.dumps(result2['payload'], indent=2)}")
    else:
        print(f"❌ Error: {response2.status_code} - {response2.text}")
        return

    time.sleep(1)

    # Test 3: Get conversation history
    print("\n📚 Test 3: Conversation History")
    response3 = requests.get(f"{BASE_URL}/history/{SESSION_ID}")

    if response3.status_code == 200:
        history = response3.json()
        print(f"✅ Session: {history['session_id']}")
        print(f"📊 Total turns: {history['total_turns']}")
        print("📜 History:")
        for i, turn in enumerate(history['history']):
            print(f"  {i + 1}. {json.dumps(turn, indent=4)}")
    else:
        print(f"❌ Error: {response3.status_code} - {response3.text}")

    print("\n🎉 Testing completed!")


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://127.0.0.1:8000")
        print("   Run: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
