"""Event handlers for the bot."""

import asyncio
import logging

import discord
from discord.ext import commands

from config import Config
from utils.message_handler import send_long_message, send_streaming_message

logger = logging.getLogger(__name__)


def setup_events(bot):
    """
    Setup bot events.

    Args:
        bot: OllamaBot instance
    """

    @bot.event
    async def on_message(message: discord.Message):
        """Handle messages that mention the bot."""
        # Ignore bot messages
        if message.author.bot:
            return

        # Process commands first
        await bot.process_commands(message)

        # Only respond to mentions that are not commands
        if bot.user in message.mentions and not message.content.startswith(bot.command_prefix):
            user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()

            if not user_input:
                await message.reply("💬 何か話しかけてね！", mention_author=True)
                return

            logger.info(f"📨 Mention | User: {message.author} | Input: {user_input[:50]}...")

            async with message.channel.typing():
                if Config.USE_STREAMING:
                    # Use streaming for faster initial response
                    stream_gen = await asyncio.to_thread(bot.ollama.generate_stream, user_input)
                    await send_streaming_message(message, stream_gen, mention_user=True)
                else:
                    # Use standard generation
                    reply = await asyncio.to_thread(bot.ollama.generate, user_input)
                    await send_long_message(message=message, content=reply, mention_user=True)

    @bot.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return

        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ エラーが発生しました: {str(error)}")
