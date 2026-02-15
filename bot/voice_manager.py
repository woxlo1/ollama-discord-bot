"""Voice channel manager for reading AI responses."""

import asyncio
import io
import logging
import os
import shutil
import tempfile
from typing import Dict, Optional

import discord

from bot.voicevox_client import VOICEVOXClient
from config import Config

logger = logging.getLogger(__name__)


class VoiceManager:
    """Manage voice channel connections and TTS."""

    def __init__(self):
        self.voicevox = VOICEVOXClient()
        self.voice_clients: Dict[int, discord.VoiceClient] = {}  # guild_id -> VoiceClient
        self.voice_queues: Dict[int, asyncio.Queue] = {}  # guild_id -> Queue
        self.current_character: Dict[int, str] = {}  # guild_id -> character
        self.temp_dir = tempfile.gettempdir()
        self.ffmpeg_path = self._get_ffmpeg_path()

    def _get_ffmpeg_path(self) -> str:
        """Get FFmpeg path from config or auto-detect."""
        # Use configured path if provided
        if Config.FFMPEG_PATH:
            if os.path.exists(Config.FFMPEG_PATH):
                logger.info(f"Using FFmpeg from config: {Config.FFMPEG_PATH}")
                return Config.FFMPEG_PATH
            else:
                logger.warning(f"Configured FFmpeg path not found: {Config.FFMPEG_PATH}")

        # Try to find ffmpeg in PATH
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            logger.info(f"Found FFmpeg in PATH: {ffmpeg_path}")
            return ffmpeg_path

        # Default fallback
        logger.warning("FFmpeg not found. Voice features may not work.")
        return "ffmpeg"

    async def join_voice_channel(
        self, channel: discord.VoiceChannel, guild_id: int
    ) -> Optional[discord.VoiceClient]:
        """Join a voice channel."""
        try:
            # Disconnect if already connected
            if guild_id in self.voice_clients:
                await self.disconnect(guild_id)

            # Connect to new channel
            voice_client = await channel.connect()
            self.voice_clients[guild_id] = voice_client
            self.voice_queues[guild_id] = asyncio.Queue()
            self.current_character[guild_id] = "zundamon_normal"

            logger.info(f"Joined voice channel: {channel.name} in guild {guild_id}")

            # Start playing queue
            asyncio.create_task(self._process_voice_queue(guild_id))

            return voice_client

        except Exception as e:
            logger.error(f"Failed to join voice channel: {e}")
            return None

    async def disconnect(self, guild_id: int):
        """Disconnect from voice channel."""
        if guild_id in self.voice_clients:
            try:
                await self.voice_clients[guild_id].disconnect()
                del self.voice_clients[guild_id]
                if guild_id in self.voice_queues:
                    del self.voice_queues[guild_id]
                if guild_id in self.current_character:
                    del self.current_character[guild_id]
                logger.info(f"Disconnected from voice channel in guild {guild_id}")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")

    async def speak(self, guild_id: int, text: str, speed: float = 1.2):
        """
        Add text to voice queue for speaking.

        Args:
            guild_id: Guild ID
            text: Text to speak
            speed: Speech speed
        """
        if guild_id not in self.voice_clients:
            logger.warning(f"Not connected to voice in guild {guild_id}")
            return

        if guild_id not in self.voice_queues:
            logger.warning(f"No voice queue for guild {guild_id}")
            return

        # Truncate long text
        if len(text) > 200:
            text = text[:200] + "、以下略"

        # Add to queue
        character = self.current_character.get(guild_id, "zundamon_normal")
        await self.voice_queues[guild_id].put((text, character, speed))

    async def _process_voice_queue(self, guild_id: int):
        """Process voice queue and play audio."""
        while guild_id in self.voice_clients:
            try:
                # Get next item from queue
                text, character, speed = await asyncio.wait_for(
                    self.voice_queues[guild_id].get(), timeout=1.0
                )

                # Synthesize speech
                audio_data = await asyncio.to_thread(
                    self.voicevox.synthesize, text, character, speed
                )

                if not audio_data:
                    logger.error("Failed to synthesize speech")
                    continue

                # Save to temp file
                temp_file = os.path.join(self.temp_dir, f"tts_{guild_id}.wav")
                with open(temp_file, "wb") as f:
                    f.write(audio_data)

                # Play audio with configured FFmpeg path
                voice_client = self.voice_clients[guild_id]
                if not voice_client.is_playing():
                    audio_source = discord.FFmpegPCMAudio(temp_file, executable=self.ffmpeg_path)
                    voice_client.play(audio_source)

                    # Wait for playback to finish
                    while voice_client.is_playing():
                        await asyncio.sleep(0.1)

                # Clean up temp file
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in voice queue processing: {e}")
                await asyncio.sleep(1)

    def set_character(self, guild_id: int, character: str):
        """Set current character for guild."""
        if character in VOICEVOXClient.CHARACTERS:
            self.current_character[guild_id] = character
            logger.info(f"Set character to {character} for guild {guild_id}")
            return True
        return False

    def is_connected(self, guild_id: int) -> bool:
        """Check if connected to voice in guild."""
        return guild_id in self.voice_clients

    def get_current_character(self, guild_id: int) -> str:
        """Get current character for guild."""
        return self.current_character.get(guild_id, "zundamon_normal")
