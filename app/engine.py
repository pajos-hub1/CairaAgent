"""
Caira AI Engine: Core AI Logic (Together AI)
The intelligent brain of the email assistant
"""

import together
import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from .prompts import PromptTemplates
from .schemas import ActionType

logger = logging.getLogger(__name__)

class CairaAI_Engine:
    """
    Core AI Engine implementing hybrid workflow model
    Handles both one-call and two-call processing patterns
    Uses Together AI with Llama Guard 4 12B
    """

    def __init__(self):
        """Initialize the AI Engine with Together AI"""
        self.api_key = os.getenv("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY environment variable is required")

        # Configure Together AI
        together.api_key = self.api_key
        self.client = together.Together(api_key=self.api_key)

        # Model configuration
        self.model_name = os.getenv("TOGETHER_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")

        # Initialize prompt templates
        self.prompts = PromptTemplates()

        logger.info(f"Caira AI Engine initialized with Together AI model: {self.model_name}")

    def _test_connection(self) -> bool:
        """Test connection to Together AI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Test connection - respond with 'OK'"}],
                max_tokens=10,
                temperature=0.1
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    def _generate_completion(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
        """Generate completion using Together AI with Mistral 7B"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are Caira, an intelligent email assistant AI. You are precise, helpful, and always follow instructions exactly."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                repetition_penalty=1.0,  # Mistral works better with lower repetition penalty
                stop=["</s>"]  # Mistral's stop token
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise

    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for processing requests
        Determines if request is initial or follow-up
        """
        try:
            if "follow_up_action" in request_data:
                logger.info("Processing follow-up request")
                return self._handle_follow_up_request(request_data)
            else:
                logger.info("Processing initial command")
                return self._handle_initial_command(request_data)
        except Exception as e:
            logger.error(f"Error in process_request: {str(e)}")
            return {
                "status": "error",
                "action_type": "ERROR",
                "payload": {"error": str(e)}
            }

    def _handle_initial_command(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle initial user command using Master Router
        This is the core intelligence that determines workflow
        """
        try:
            command_text = request_data.get("command_text", "")
            user_profile = request_data.get("user_profile", {})
            email_context = request_data.get("email_context")

            # Generate master router prompt
            prompt = self.prompts.get_master_router_prompt(
                command_text, user_profile, email_context
            )

            # Get AI response with lower temperature for more consistent JSON
            response_text = self._generate_completion(prompt, max_tokens=500, temperature=0.1)

            logger.info(f"Master Router raw response: {response_text}")

            # Parse JSON response
            try:
                # Clean up response text - remove any markdown formatting
                clean_response = response_text.strip()
                if clean_response.startswith("\`\`\`json"):
                    clean_response = clean_response.replace("\`\`\`json", "").replace("\`\`\`", "").strip()
                elif clean_response.startswith("\`\`\`"):
                    clean_response = clean_response.replace("\`\`\`", "").strip()

                ai_decision = json.loads(clean_response)

                # Validate response structure
                if "action_type" not in ai_decision or "payload" not in ai_decision:
                    raise ValueError("Invalid AI response structure")

                # Add metadata
                ai_decision["status"] = "success"
                ai_decision["metadata"] = {
                    "timestamp": datetime.now().isoformat(),
                    "model": self.model_name,
                    "workflow_type": self._get_workflow_type(ai_decision["action_type"])
                }

                return ai_decision

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {response_text}")
                # Fallback: try to extract action from text
                return self._fallback_command_processing(command_text, user_profile)

        except Exception as e:
            logger.error(f"Error in _handle_initial_command: {str(e)}")
            return {
                "status": "error",
                "action_type": "ERROR",
                "payload": {"error": f"Initial command processing failed: {str(e)}"}
            }

    def _handle_follow_up_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle follow-up requests (second call in two-call workflow)
        """
        try:
            follow_up_action = request_data.get("follow_up_action", "")
            email_data = request_data.get("email_data", [])
            original_command = request_data.get("original_command", "")

            if follow_up_action == "SUMMARIZE_CONTENT":
                return self._summarize_email_content(email_data, original_command)
            elif follow_up_action == "ANSWER_QUESTION":
                return self._answer_email_question(email_data, original_command)
            else:
                raise ValueError(f"Unknown follow-up action: {follow_up_action}")

        except Exception as e:
            logger.error(f"Error in _handle_follow_up_request: {str(e)}")
            return {
                "status": "error",
                "action_type": "ERROR",
                "payload": {"error": f"Follow-up processing failed: {str(e)}"}
            }

    def _summarize_email_content(self, email_data: List[Dict], original_command: str) -> Dict[str, Any]:
        """Summarize email content using specialized prompt"""
        try:
            prompt = self.prompts.get_summarization_prompt(email_data, original_command)

            # Use higher max_tokens for summaries and slightly higher temperature for more natural language
            summary_text = self._generate_completion(prompt, max_tokens=1500, temperature=0.5)

            return {
                "status": "success",
                "action_type": ActionType.FINAL_RESPONSE,
                "payload": {
                    "text_response": summary_text
                },
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "emails_processed": len(email_data),
                    "model": self.model_name
                }
            }

        except Exception as e:
            logger.error(f"Error in _summarize_email_content: {str(e)}")
            raise

    def _answer_email_question(self, email_data: List[Dict], original_command: str) -> Dict[str, Any]:
        """Answer specific questions about email content"""
        try:
            prompt = self.prompts.get_question_answering_prompt(email_data, original_command)

            # Use moderate settings for Q&A
            answer_text = self._generate_completion(prompt, max_tokens=1000, temperature=0.4)

            return {
                "status": "success",
                "action_type": ActionType.FINAL_RESPONSE,
                "payload": {
                    "text_response": answer_text
                },
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "emails_analyzed": len(email_data),
                    "model": self.model_name
                }
            }

        except Exception as e:
            logger.error(f"Error in _answer_email_question: {str(e)}")
            raise

    def _fallback_command_processing(self, command_text: str, user_profile: Dict) -> Dict[str, Any]:
        """
        Fallback processing when JSON parsing fails
        Uses simpler heuristics to determine action
        """
        logger.info("Using fallback command processing")

        command_lower = command_text.lower()

        # Simple keyword-based classification
        if any(word in command_lower for word in ["show", "find", "search", "list", "get"]):
            # Likely a search query
            query_prompt = self.prompts.get_gmail_query_builder_prompt(command_text)
            try:
                search_string = self._generate_completion(query_prompt, max_tokens=200, temperature=0.1)

                return {
                    "status": "success",
                    "action_type": ActionType.GMAIL_QUERY_GENERATED,
                    "payload": {
                        "gmail_search_string": search_string,
                        "explanation": "Generated via fallback processing"
                    }
                }
            except:
                # Ultimate fallback
                return {
                    "status": "success",
                    "action_type": ActionType.GMAIL_QUERY_GENERATED,
                    "payload": {
                        "gmail_search_string": command_text,
                        "explanation": "Direct command passthrough"
                    }
                }

        elif any(word in command_lower for word in ["summarize", "summary", "overview"]):
            # Likely needs summarization
            return {
                "status": "success",
                "action_type": ActionType.FETCH_AND_SUMMARIZE,
                "payload": {
                    "gmail_search_string": command_text
                }
            }

        else:
            # Default to search
            return {
                "status": "success",
                "action_type": ActionType.GMAIL_QUERY_GENERATED,
                "payload": {
                    "gmail_search_string": command_text
                }
            }

    def _get_workflow_type(self, action_type: str) -> str:
        """Determine workflow type based on action_type"""
        one_call_actions = [
            ActionType.GMAIL_QUERY_GENERATED,
            ActionType.ACTION_REQUIRED
        ]

        two_call_actions = [
            ActionType.FETCH_AND_SUMMARIZE,
            ActionType.FETCH_AND_ANSWER
        ]

        if action_type in one_call_actions:
            return "one-call"
        elif action_type in two_call_actions:
            return "two-call"
        else:
            return "unknown"
