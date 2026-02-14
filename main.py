"""Main entry point for Ollama Discord Bot."""
import logging

import discord
from dotenv import load_dotenv

from config import Config
from bot import OllamaBot
from commands import setup_slash_commands, setup_events
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
        
        # Setup commands and events
        setup_slash_commands(bot)
        setup_events(bot)
        
        # Run bot
        logger.info("🚀 Starting Ollama Discord Bot...")
        bot.run(Config.DISCORD_TOKEN)
        
    except discord.LoginFailure:
        logger.error("❌ Invalid Discord token. Please check your .env file.")
    except Exception as e:
        logger.exception(f"❌ Failed to start bot: {e}")


if __name__ == "__main__":
    main()
