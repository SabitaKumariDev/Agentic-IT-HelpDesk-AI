"""
LLM Abstraction using OpenAI SDK directly.
"""

import os
import uuid
from openai import AsyncOpenAI
from .constants import LLM_CONFIG


class LlmChat:
    """Simple async chat wrapper around OpenAI API."""

    def __init__(self, system_message: str):
        api_key = os.environ.get(LLM_CONFIG["api_key_env"])
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = LLM_CONFIG["model"]
        self.messages = [{"role": "system", "content": system_message}]

    async def send_message(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )
        reply = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        return reply


def create_chat(session_prefix: str, system_message: str) -> LlmChat:
    """Create a configured LLM chat instance."""
    return LlmChat(system_message=system_message)
