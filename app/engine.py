import together
import os
import json
from .prompts import COMMAND_CLASSIFIER_PROMPT, MASTER_ROUTER_PROMPT, SUMMARIZER_PROMPT, QUESTION_ANSWERER_PROMPT


class CairaAI_Engine:
    def __init__(self):
        # Configure Together AI
        api_key = os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY environment variable is required")

        self.client = together.Together(api_key=api_key)
        self.model = os.environ.get("TOGETHER_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
        self.conversations = {}  # In-memory history storage
        print(f"Unified CairaAI Engine Initialized with {self.model}")

    def _update_history(self, session_id: str, user_text: str, ai_response: dict):
        """Appends the latest turn to the conversation history."""
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        self.conversations[session_id].append({"user": user_text})
        self.conversations[session_id].append({"ai": ai_response})

        # Limit history size to prevent it from growing too large
        if len(self.conversations[session_id]) > 12:
            self.conversations[session_id] = self.conversations[session_id][-12:]

    def get_conversation_history(self, session_id: str) -> list:
        """Returns the conversation history for a given session."""
        return self.conversations.get(session_id, [])

    def clear_conversation(self, session_id: str) -> bool:
        """Clears the conversation history for a given session."""
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False

    def _call_together_ai(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.1) -> str:
        """Helper method to call Together AI with consistent parameters."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that responds with valid JSON objects for Gmail operations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                stop=None
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"Together AI API call failed: {str(e)}")

    def process_initial_command(self, session_id: str, command_text: str, email_context: dict | None) -> dict:
        """Handles the FIRST call. It reads history and decides on a workflow."""
        print(f"Processing initial command for session: {session_id}")

        # Retrieve history for the current session
        history = self.conversations.get(session_id, [])

        # Format the history for the prompt
        if history:
            history_text = "\n".join([json.dumps(turn, indent=2) for turn in history])
        else:
            history_text = "No previous conversation history."

        # Add email context to the prompt if it exists
        context_info = ""
        if email_context:
            context_info = f"\n\n**Additional Context:**\n{json.dumps(email_context, indent=2)}"

        prompt = MASTER_ROUTER_PROMPT.format(
            conversation_history=history_text,
            user_command=command_text
        ) + context_info

        try:
            # Call Together AI to get the initial action_type
            response_text = self._call_together_ai(prompt)

            # Clean up the response (remove markdown code blocks if present)
            cleaned_text = response_text.replace("\`\`\`json", "").replace("\`\`\`", "").strip()

            # Parse the JSON response
            ai_payload = json.loads(cleaned_text)

            # Validate required fields
            if "action_type" not in ai_payload:
                raise ValueError("AI response missing 'action_type' field")

            if "payload" not in ai_payload:
                ai_payload["payload"] = {}

            # Update history with this turn
            self._update_history(session_id, command_text, ai_payload)

            return ai_payload

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response_text if 'response_text' in locals() else 'No response'}")
            return {
                "error": "Failed to parse AI response as JSON",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        except Exception as e:
            print(f"Error processing initial command: {e}")
            return {"error": f"Failed to process command: {str(e)}"}

    def process_follow_up(self, session_id: str, follow_up_action: str, email_data: list,
                          original_command: str) -> dict:
        """Handles the SECOND call in a two-call workflow."""
        print(f"Processing follow-up action: {follow_up_action} for session: {session_id}")

        try:
            # Convert email data to string format
            email_content_str = json.dumps(email_data, indent=2)

            if follow_up_action == "SUMMARIZE_CONTENT":
                prompt = SUMMARIZER_PROMPT.format(
                    original_command=original_command,
                    email_content=email_content_str
                )

                response_text = self._call_together_ai(prompt, max_tokens=1500, temperature=0.3)

                final_response = {
                    "status": "success",
                    "action_type": "FINAL_RESPONSE",
                    "payload": {
                        "text_response": response_text,
                        "response_type": "summary",
                        "processed_emails": len(email_data)
                    }
                }

            elif follow_up_action == "ANSWER_QUESTION":
                prompt = QUESTION_ANSWERER_PROMPT.format(
                    original_command=original_command,
                    email_content=email_content_str
                )

                response_text = self._call_together_ai(prompt, max_tokens=1000, temperature=0.2)

                final_response = {
                    "status": "success",
                    "action_type": "FINAL_RESPONSE",
                    "payload": {
                        "text_response": response_text,
                        "response_type": "answer",
                        "processed_emails": len(email_data)
                    }
                }

            else:
                return {"error": f"Unknown follow-up action: {follow_up_action}"}

            # Update history with the final outcome
            self._update_history(session_id, f"System: Processed {follow_up_action} for {len(email_data)} emails",
                                 final_response)

            return final_response

        except Exception as e:
            print(f"Error processing follow-up: {e}")
            return {"error": f"Failed to process follow-up: {str(e)}"}

    def get_model_info(self) -> dict:
        """Returns information about the current model configuration."""
        return {
            "model": self.model,
            "provider": "Together AI",
            "capabilities": ["text_generation", "json_output", "conversation_history"]
        }
