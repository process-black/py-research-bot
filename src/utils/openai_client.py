"""OpenAI client utility for PDF summarization and analysis."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from src.utils import colored_logs as llog

# Ensure environment variables are loaded
load_dotenv()


class OpenAIClient:
    """OpenAI client wrapper for document analysis."""
    
    def __init__(self):
        """Initialize OpenAI client with API key from environment."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        llog.gray(f"🔑 Initializing OpenAI client with API key: {api_key[:10]}...")
        self.client = OpenAI(api_key=api_key)
        
    
    def _estimate_cost(self, total_tokens):
        """Estimate cost based on gpt-4o-mini pricing."""
        # gpt-4o-mini pricing (approximate): $0.15 per 1M input tokens, $0.60 per 1M output tokens
        # For simplicity, using average of $0.375 per 1M tokens
        cost_per_million = 0.375
        estimated_cost = (total_tokens / 1_000_000) * cost_per_million
        return round(estimated_cost, 4)