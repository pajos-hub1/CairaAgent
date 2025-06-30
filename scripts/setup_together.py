#!/usr/bin/env python3
"""
Setup script for Together AI integration
Helps users get started with Together AI API
"""

import os
import sys


def main():
    print("🚀 Caira AI Engine - Together AI Setup (Mistral 7B)")
    print("=" * 55)

    print("\n📋 Setup Steps:")
    print("1. Visit https://together.ai")
    print("2. Sign up for a free account")
    print("3. Go to your dashboard and create an API key")
    print("4. Copy your API key")

    print("\n🔑 Enter your Together AI API key:")
    api_key = input("API Key: ").strip()

    if not api_key:
        print("❌ No API key provided. Exiting.")
        return

    # Create or update .env file
    env_content = f"""# Caira AI Engine Environment Variables
# Together AI Configuration - Mistral 7B
TOGETHER_API_KEY={api_key}
TOGETHER_MODEL=mistralai/Mistral-7B-Instruct-v0.1

# Optional: Logging Configuration
LOG_LEVEL=INFO

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8000

# Optional: Development Settings
DEBUG=True
RELOAD=True
"""

    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")

        print("\n🧪 Testing Mistral 7B connection...")

        # Test the connection
        os.environ['TOGETHER_API_KEY'] = api_key

        try:
            import together
            client = together.Together(api_key=api_key)

            response = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.1",
                messages=[{"role": "user", "content": "Say 'Mistral connection successful!'"}],
                max_tokens=10
            )

            if response.choices[0].message.content:
                print("✅ Mistral 7B connection successful!")
                print(f"Response: {response.choices[0].message.content}")
            else:
                print("❌ Connection test failed - no response")

        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            print("Please check your API key and try again.")
            return

        print("\n🎉 Setup complete! You can now run:")
        print("   python scripts/start_server.py")
        print("   python scripts/test_engine.py")

    except Exception as e:
        print(f"❌ Error creating .env file: {str(e)}")


if __name__ == "__main__":
    main()
