# Caira AI Engine v2.0

An intelligent email assistant AI engine with hybrid workflow architecture, built with FastAPI and Together AI (Llama models).

## 🏗️ Architecture

The Caira AI Engine implements a **hybrid workflow model**:

- **One-Call Workflow**: Direct actions like email searches or simple commands
- **Two-Call Workflow**: Complex operations requiring data fetching and processing (summarization, Q&A)

## 🚀 Quick Start

### Prerequisites

1. Python 3.10+
2. Together AI API key (free tier available)

### Installation

1. **Clone and setup**:
   \`\`\`bash
   git clone <repository>
   cd caira-ai-engine
   pip install -r requirements.txt
   \`\`\`

2. **Get Together AI API Key**:
   - Visit [together.ai](https://together.ai)
   - Sign up for free account
   - Get your API key from the dashboard

3. **Configure environment**:
   \`\`\`bash
   cp .env.example .env
   # Edit .env and add your TOGETHER_API_KEY
   \`\`\`

4. **Start the server**:
   \`\`\`bash
   python scripts/start_server.py
   \`\`\`

5. **Test the engine**:
   \`\`\`bash
   python scripts/test_engine.py
   \`\`\`

## 📡 API Endpoints

### Main Processing Endpoint
\`\`\`
POST /api/v1/ai-engine/process
\`\`\`

**Request Body** (Initial):
\`\`\`json
{
  "command_text": "Show me emails from john@example.com",
  "user_profile": {
    "user_id": "user123",
    "email": "user@example.com",
    "timezone": "UTC"
  },
  "email_context": {
    "subject": "Optional current email subject",
    "sender": "Optional current email sender"
  }
}
\`\`\`

**Response** (One-Call):
\`\`\`json
{
  "status": "success",
  "action_type": "GMAIL_QUERY_GENERATED",
  "payload": {
    "gmail_search_string": "from:john@example.com"
  }
}
\`\`\`

**Response** (Two-Call Trigger):
\`\`\`json
{
  "status": "success", 
  "action_type": "FETCH_AND_SUMMARIZE",
  "payload": {
    "gmail_search_string": "from:hr after:2025/06/21"
  }
}
\`\`\`

### Follow-up Request (Two-Call Completion):
\`\`\`json
{
  "follow_up_action": "SUMMARIZE_CONTENT",
  "email_data": [
    {
      "subject": "Email subject",
      "sender": "sender@example.com", 
      "body": "Email content..."
    }
  ],
  "original_command": "Summarize my emails from HR",
  "user_profile": { /* same as above */ }
}
\`\`\`

## 🧠 Action Types

| Action Type | Workflow | Description |
|-------------|----------|-------------|
| `GMAIL_QUERY_GENERATED` | One-Call | Generate Gmail search query |
| `ACTION_REQUIRED` | One-Call | Direct actions (block, delete, etc.) |
| `FETCH_AND_SUMMARIZE` | Two-Call | Fetch emails then summarize |
| `FETCH_AND_ANSWER` | Two-Call | Fetch emails then answer questions |
| `FINAL_RESPONSE` | Response | Final processed response |

## 🔧 Development

### Project Structure
\`\`\`
caira-ai-engine/
├── app/
│   ├── main.py          # FastAPI server
│   ├── engine.py        # Core AI logic
│   ├── schemas.py       # Data models
│   └── prompts.py       # Prompt templates
├── scripts/
│   ├── test_engine.py   # Test script
│   └── start_server.py  # Dev server
└── .env                 # Environment config
\`\`\`

### Testing
\`\`\`bash
# Run the test script
python scripts/test_engine.py

# Or use pytest for unit tests
pytest tests/
\`\`\`

### API Documentation
Visit `http://localhost:8000/docs` when the server is running for interactive API documentation.

## 🌟 Features

- **Intelligent Intent Classification**: Uses advanced prompting to determine optimal workflow
- **Hybrid Processing**: Optimizes for speed (one-call) vs intelligence (two-call)
- **Gmail Integration Ready**: Generates proper Gmail search queries
- **Extensible Architecture**: Easy to add new action types and workflows
- **Comprehensive Logging**: Full request/response logging for debugging
- **Type Safety**: Full Pydantic validation for all data structures

## 🤖 AI Model

- **Provider**: Together AI
- **Model**: Mistral 7B Instruct v0.1
- **Benefits**: 
  - Fast inference (~1-2 seconds)
  - Excellent instruction following
  - Cost-effective on free tier
  - Great for structured outputs
- **Cost**: Free tier available with generous limits

## 🔐 Environment Variables

\`\`\`bash
TOGETHER_API_KEY=your_together_api_key_here    # Required
TOGETHER_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo  # Optional
LOG_LEVEL=INFO                                 # Optional
DEBUG=True                                     # Optional
\`\`\`

## 📈 Performance

- **One-Call Latency**: ~1-2 seconds (Mistral is very fast!)
- **Two-Call Latency**: ~3-5 seconds total
- **Free Tier**: Generous limits for development and testing
- **Accuracy**: >90% intent classification with optimized prompts
- **Efficiency**: 7B parameters = faster responses, lower costs

## 💰 Cost Benefits

- **Free Tier**: Together AI offers generous free usage
- **Fast Model**: Mistral 7B is one of the fastest models available
- **High Efficiency**: Smaller model size = lower costs per request
- **No Rate Limits**: More flexible than other free tiers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.
