"""Discord bot client."""

import logging

import discord
from discord.ext import commands

from bot.export_manager import ExportManager
from bot.memory import ConversationMemory
from bot.model_manager import ModelManager
from bot.ollama_client import OllamaClient
from bot.stats_tracker import StatsTracker
from bot.vision import VisionClient
from bot.voice_manager import VoiceManager
from config import Config

logger = logging.getLogger(__name__)


class OllamaBot(commands.Bot):
    """Discord bot with Ollama integration and advanced features."""

    def __init__(self):
        """Initialize the bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True  # Required for voice

        super().__init__(command_prefix=Config.BOT_PREFIX, intents=intents)

        self.ollama = OllamaClient(
            host=Config.OLLAMA_HOST, model=Config.OLLAMA_MODEL, timeout=Config.REQUEST_TIMEOUT
        )

        # Initialize all subsystems
        self.memory = ConversationMemory()
        logger.info("🧠 Memory system initialized")

        self.model_manager = ModelManager(host=Config.OLLAMA_HOST)
        logger.info("🔄 Model manager initialized")

        self.stats = StatsTracker()
        logger.info("📊 Stats tracker initialized")

        self.export_manager = ExportManager()
        logger.info("💾 Export manager initialized")

        self.vision = VisionClient(host=Config.OLLAMA_HOST, timeout=Config.REQUEST_TIMEOUT)
        logger.info("👁️ Vision client initialized")

        self.voice_manager = VoiceManager()
        logger.info("🎤 Voice manager initialized")

        # Per-user template selection
        self.user_templates = {}

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
        logger.info(f"📈 Total questions: {self.stats.stats['total_questions']}")

        # Health checks
        if self.ollama.health_check():
            logger.info(f"✅ Ollama server is healthy at {Config.OLLAMA_HOST}")
        else:
            logger.warning(f"⚠️ Could not connect to Ollama at {Config.OLLAMA_HOST}")

        if self.vision.is_llava_available():
            logger.info("👁️ LLaVA model is available")
        else:
            logger.warning("⚠️ LLaVA model not found. Run: ollama pull llava")

        if self.voice_manager.voicevox.is_available():
            logger.info("🎤 VOICEVOX is available")
        else:
            logger.warning("⚠️ VOICEVOX not found. Voice features will be unavailable.")
