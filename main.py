"""Main entry point for Ollama Discord Bot."""

import logging

import discord
from dotenv import load_dotenv

from bot import OllamaBot
from commands import setup_events, setup_slash_commands
from commands.advanced_commands import setup_advanced_commands
from config import Config
from utils import setup_logger

# Load environment variables
load_dotenv()

# Validate configuration
Config.validate()

# Setup logging
setup_logger(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    try:
        # Initialize bot
        bot = OllamaBot()

        # Setup all commands and events
        setup_slash_commands(bot)
        setup_advanced_commands(bot)
        setup_events(bot)

        # Run bot
        logger.info("🚀 Starting Ollama Discord Bot with advanced features...")
        bot.run(Config.DISCORD_TOKEN)

    except discord.LoginFailure:
        logger.error("❌ Invalid Discord token. Please check your .env file.")
    except Exception as e:
        logger.exception(f"❌ Failed to start bot: {e}")


if __name__ == "__main__":
    main()
