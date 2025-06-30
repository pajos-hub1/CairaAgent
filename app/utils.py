"""
Helper functions and utilities for the Caira AI Engine
"""

import re
import json
import time
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class EmailPatternMatcher:
    """Utility class for matching email patterns and extracting information"""

    EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    FOLDER_REGEX = r'(?:into|to|in)\s+["\']?([^"\']+)["\']?'
    DATE_REGEX = r'\b(?:today|yesterday|last\s+week|this\s+week|last\s+\w+|\d{1,2}/\d{1,2}/\d{4})\b'

    @classmethod
    def extract_emails(cls, text: str) -> List[str]:
        """Extract email addresses from text"""
        return re.findall(cls.EMAIL_REGEX, text, re.IGNORECASE)

    @classmethod
    def extract_folders(cls, text: str) -> List[str]:
        """Extract folder/label names from text"""
        matches = re.findall(cls.FOLDER_REGEX, text, re.IGNORECASE)
        return [match.strip() for match in matches]

    @classmethod
    def extract_dates(cls, text: str) -> List[str]:
        """Extract date references from text"""
        return re.findall(cls.DATE_REGEX, text, re.IGNORECASE)

    @classmethod
    def clean_folder_name(cls, folder_name: str) -> str:
        """Clean and normalize folder names"""
        # Remove quotes and extra whitespace
        cleaned = re.sub(r'["\']', '', folder_name).strip()
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in cleaned.split())

class TextProcessor:
    """Text processing utilities"""

    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'into', 'sort', 'find', 'search', 'emails',
        'email', 'show', 'me', 'all', 'get', 'please', 'can', 'you', 'i', 'my'
    }

    @classmethod
    def extract_keywords(cls, text: str, max_keywords: int = 5) -> List[str]:
        """Extract meaningful keywords from text"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter out stop words and short words
        keywords = [
            word for word in words
            if word not in cls.STOP_WORDS and len(word) > 2
        ]

        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            if keyword not in seen:
                unique_keywords.append(keyword)
                seen.add(keyword)

        return unique_keywords[:max_keywords]

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Normalize text for processing"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s@.-]', '', text)
        return text

class CacheManager:
    """Simple in-memory cache for LLM responses"""

    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def _generate_key(self, prompt: str, model_config: Dict[str, Any]) -> str:
        """Generate cache key from prompt and model config"""
        content = f"{prompt}_{json.dumps(model_config, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, prompt: str, model_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        key = self._generate_key(prompt, model_config)

        if key in self.cache:
            cached_item = self.cache[key]
            if time.time() - cached_item['timestamp'] < self.ttl_seconds:
                logger.debug(f"Cache hit for key: {key[:8]}...")
                return cached_item['response']
            else:
                # Remove expired item
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key[:8]}...")

        return None

    def set(self, prompt: str, model_config: Dict[str, Any], response: Dict[str, Any]) -> None:
        """Cache response"""
        key = self._generate_key(prompt, model_config)
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        logger.debug(f"Cached response for key: {key[:8]}...")

    def clear(self) -> None:
        """Clear all cached items"""
        self.cache.clear()
        logger.info("Cache cleared")

    def cleanup_expired(self) -> None:
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.cache.items()
            if current_time - item['timestamp'] >= self.ttl_seconds
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

class PerformanceMonitor:
    """Monitor performance metrics"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}

    def record_processing_time(self, operation: str, duration_ms: float) -> None:
        """Record processing time for an operation"""
        if operation not in self.metrics:
            self.metrics[operation] = []

        self.metrics[operation].append(duration_ms)

        # Keep only last 100 measurements
        if len(self.metrics[operation]) > 100:
            self.metrics[operation] = self.metrics[operation][-100:]

    def get_average_time(self, operation: str) -> Optional[float]:
        """Get average processing time for an operation"""
        if operation not in self.metrics or not self.metrics[operation]:
            return None

        return sum(self.metrics[operation]) / len(self.metrics[operation])

    def get_stats(self, operation: str) -> Optional[Dict[str, float]]:
        """Get detailed stats for an operation"""
        if operation not in self.metrics or not self.metrics[operation]:
            return None

        times = self.metrics[operation]
        return {
            'count': len(times),
            'average': sum(times) / len(times),
            'min': min(times),
            'max': max(times),
            'latest': times[-1]
        }

class JSONValidator:
    """Validate and clean JSON responses from LLMs"""

    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text that might contain other content"""
        # Try to find JSON block
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            return None

        json_str = json_match.group()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to fix common JSON issues
            return JSONValidator._attempt_json_repair(json_str)

    @staticmethod
    def _attempt_json_repair(json_str: str) -> Optional[Dict[str, Any]]:
        """Attempt to repair malformed JSON"""
        try:
            # Fix common issues
            repaired = json_str

            # Fix trailing commas
            repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)

            # Fix unquoted keys
            repaired = re.sub(r'(\w+):', r'"\1":', repaired)

            # Fix single quotes
            repaired = repaired.replace("'", '"')

            return json.loads(repaired)
        except json.JSONDecodeError:
            logger.warning(f"Failed to repair JSON: {json_str[:100]}...")
            return None

    @staticmethod
    def validate_response_schema(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that response contains required fields"""
        return all(field in data for field in required_fields)

def timing_decorator(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        duration_ms = (end_time - start_time) * 1000
        logger.debug(f"{func.__name__} took {duration_ms:.2f}ms")

        return result
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")

            raise last_exception
        return wrapper
    return decorator
