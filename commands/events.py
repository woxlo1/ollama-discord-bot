"""Event handlers for the bot."""

import logging
import asyncio

import discord
from discord.ext import commands

from utils.message_handler import send_long_message

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
        if message.author.bot:
            return

        if bot.user in message.mentions:
            user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()

            if not user_input:
                await message.reply("💬 何か話しかけてね！", mention_author=True)
                return

            logger.info(f"📨 Mention | User: {message.author} | Input: {user_input[:50]}...")

            async with message.channel.typing():
                reply = await asyncio.to_thread(bot.ollama.generate, user_input)

            await send_long_message(message=message, content=reply, mention_user=True)

    @bot.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return

        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ エラーが発生しました: {str(error)}")
