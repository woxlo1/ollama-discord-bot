"""Event handlers for the bot."""

import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


def setup_events(bot):
    """
    Setup bot events.

    Args:
        bot: OllamaBot instance
    """

    @bot.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return

        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ エラーが発生しました: {str(error)}")
