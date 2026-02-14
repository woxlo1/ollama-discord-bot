"""Configuration settings for Ollama Discord Bot."""

import os


class Config:
    """Bot configuration settings."""

    # Discord
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    BOT_PREFIX: str = os.getenv("BOT_PREFIX", "!")

    # Ollama
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    # Bot Behavior
    MAX_RESPONSE_LENGTH: int = int(os.getenv("MAX_RESPONSE_LENGTH", "1900"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "180"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # System Prompt
    SYSTEM_PROMPT: str = """あなたは優秀な日本語アシスタントです。
必ず日本語で自然に回答してください。

ユーザーの質問:
{prompt}"""

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is not set in environment variables.")

    @classmethod
    def get_full_prompt(cls, user_input: str) -> str:
        """Generate full prompt with system message."""
        return cls.SYSTEM_PROMPT.format(prompt=user_input)
