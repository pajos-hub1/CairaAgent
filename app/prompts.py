"""
Caira AI Engine: Prompt Templates (Optimized for Llama Models)
Centralized prompt management for different AI tasks
"""

from typing import Dict, List, Any
import json

class PromptTemplates:
    """Collection of prompt templates optimized for Llama models"""

    @staticmethod
    def get_master_router_prompt(command_text: str, user_profile: Dict, email_context: Dict = None) -> str:
        """
        Master Router Prompt: Optimized for Mistral 7B Instruct
        """

        context_info = ""
        if email_context:
            context_info = f"""
Current Email Context:
- Subject: {email_context.get('subject', 'N/A')}
- Sender: {email_context.get('sender', 'N/A')}
- Body Preview: {email_context.get('body', 'N/A')[:200]}...
"""

        return f"""<s>[INST] You are the Caira AI Engine's Master Router. Analyze the user's email command and return ONLY a JSON response.

User Profile:
- Email: {user_profile.get('email', 'N/A')}
- Timezone: {user_profile.get('timezone', 'UTC')}
- Language: {user_profile.get('language', 'en')}

{context_info}

User Command: "{command_text}"

CLASSIFICATION RULES:

1. GMAIL_QUERY_GENERATED (One-Call):
   - Search, find, show, list emails
   - Example: "Show emails from John" → {{"action_type": "GMAIL_QUERY_GENERATED", "payload": {{"gmail_search_string": "from:john"}}}}

2. ACTION_REQUIRED (One-Call):
   - Direct actions: block, delete, archive
   - Example: "Block sender X" → {{"action_type": "ACTION_REQUIRED", "payload": {{"action": "BLOCK_SENDER", "parameters": {{"email": "x@example.com"}}}}}}

3. FETCH_AND_SUMMARIZE (Two-Call):
   - Summaries, overviews
   - Example: "Summarize HR emails" → {{"action_type": "FETCH_AND_SUMMARIZE", "payload": {{"gmail_search_string": "from:hr"}}}}

4. FETCH_AND_ANSWER (Two-Call):
   - Specific questions about content
   - Example: "What time is the meeting?" → {{"action_type": "FETCH_AND_ANSWER", "payload": {{"gmail_search_string": "meeting"}}}}

Current date: 2025-06-30

Respond with ONLY valid JSON: [/INST]"""

    @staticmethod
    def get_summarization_prompt(email_data: List[Dict], original_command: str) -> str:
        """Summarization prompt optimized for Mistral 7B"""

        emails_text = ""
        for i, email in enumerate(email_data, 1):
            emails_text += f"""
Email {i}:
Subject: {email.get('subject', 'No Subject')}
From: {email.get('sender', 'Unknown')}
Content: {email.get('body', 'No content')[:1000]}
---
"""

        return f"""<s>[INST] You are Caira, an intelligent email assistant. The user requested: "{original_command}"

Here are the emails to summarize:
{emails_text}

Provide a clear summary focusing on:
1. Key information and main points
2. Important dates/times/deadlines
3. Action items or requests
4. Overall themes

Be conversational and helpful. [/INST]"""

    @staticmethod
    def get_question_answering_prompt(email_data: List[Dict], original_command: str) -> str:
        """Question answering prompt optimized for Mistral 7B"""

        emails_text = ""
        for i, email in enumerate(email_data, 1):
            emails_text += f"""
Email {i}:
Subject: {email.get('subject', 'No Subject')}
From: {email.get('sender', 'Unknown')}
Content: {email.get('body', 'No content')[:1200]}
---
"""

        return f"""<s>[INST] You are Caira, an intelligent email assistant. The user asked: "{original_command}"

Here are the relevant emails:
{emails_text}

Answer the user's question based on the email content. Be specific and quote relevant details when possible. If the information isn't available, say so honestly. [/INST]"""

    @staticmethod
    def get_gmail_query_builder_prompt(command_text: str) -> str:
        """Gmail query builder optimized for Mistral 7B"""

        return f"""<s>[INST] Convert this request into a Gmail search query.

Request: "{command_text}"

Gmail operators: from:, to:, subject:, has:attachment, is:unread, after:YYYY/MM/DD, newer_than:7d

Examples:
- "emails from john" → from:john
- "unread emails from HR" → from:hr is:unread
- "emails about project" → subject:project OR project

Respond with ONLY the search string: [/INST]"""

    @staticmethod
    def get_action_classifier_prompt(command_text: str) -> str:
        """Prompt for classifying direct actions - optimized for Llama"""

        return f"""Classify this email management command and extract parameters.

Command: "{command_text}"

Available Actions:
- BLOCK_SENDER: Block emails from a sender
- DELETE_EMAIL: Delete specific email(s)  
- ARCHIVE_EMAIL: Archive email(s)
- MARK_READ: Mark email(s) as read
- MARK_UNREAD: Mark email(s) as unread
- ADD_LABEL: Add label to email(s)
- REMOVE_LABEL: Remove label from email(s)
- FORWARD_EMAIL: Forward an email
- REPLY_EMAIL: Reply to an email

Examples:
"Block emails from spam@example.com" → {{"action": "BLOCK_SENDER", "parameters": {{"email": "spam@example.com"}}}}
"Archive all emails from newsletters" → {{"action": "ARCHIVE_EMAIL", "parameters": {{"filter": "from:newsletters"}}}}
"Mark this email as read" → {{"action": "MARK_READ", "parameters": {{"target": "current"}}}}

Respond with ONLY valid JSON in this format:
{{"action": "ACTION_NAME", "parameters": {{"key": "value"}}}}

Response:"""
