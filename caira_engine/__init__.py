"""
Caira AI Engine Package
A specialized service for Natural Language Processing tasks in Project Caira
"""

from .engine import CairaAIEngine
from .schemas import UserProfile, AIRequest, AIResponse, ActionType
from .prompts import PromptManager

__version__ = "1.0.0"
__all__ = ["CairaAIEngine", "UserProfile", "AIRequest", "AIResponse", "ActionType", "PromptManager"]
