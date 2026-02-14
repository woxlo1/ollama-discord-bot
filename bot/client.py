"""Discord bot client."""
import logging

import discord
from discord.ext import commands

from bot.memory import ConversationMemory
from bot.ollama_client import OllamaClient
from config import Config

logger = logging.getLogger(__name__)


class OllamaBot(commands.Bot):
    """Discord bot with Ollama integration and learning capabilities."""
    
    def __init__(self):
        """Initialize the bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(command_prefix=Config.BOT_PREFIX, intents=intents)
        
        self.ollama = OllamaClient(
            host=Config.OLLAMA_HOST,
            model=Config.OLLAMA_MODEL,
            timeout=Config.REQUEST_TIMEOUT
        )
        
        # Initialize memory system
        self.memory = ConversationMemory()
        logger.info("🧠 Memory system initialized")
    
    async def setup_hook(self):
        """Setup hook called when bot is ready."""
        await self.tree.sync()
        logger.info("Command tree synced")
    
    async def on_ready(self):
        """Called when bot successfully connects to Discord."""
        logger.info(f"✅ Logged in as {self.user}")
        logger.info(f"📊 Connected to {len(self.guilds)} guild(s)")
        logger.info(f"🤖 Using model: {Config.OLLAMA_MODEL}")
        logger.info(f"🧠 Learned facts: {len(self.memory.learned_facts)}")
        
        # Health check
        if self.ollama.health_check():
            logger.info(f"✅ Ollama server is healthy at {Config.OLLAMA_HOST}")
        else:
            logger.warning(f"⚠️ Could not connect to Ollama at {Config.OLLAMA_HOST}")
