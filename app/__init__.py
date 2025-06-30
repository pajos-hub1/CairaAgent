"""
Caira AI Engine Package
A specialized service for Natural Language Processing tasks in Project Caira
"""

from .engine import CairaAI_Engine
from .schemas import UserProfile, AIResponse, ActionType
from .prompts import PromptTemplates

__version__ = "1.0.0"
__all__ = ["CairaAI_Engine", "UserProfile", "AIResponse", "ActionType", "PromptTemplates"]
