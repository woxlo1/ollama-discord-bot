"""Message handling utilities."""

import logging
from typing import Optional

import discord

from config import Config

logger = logging.getLogger(__name__)


async def send_long_message(
    interaction: Optional[discord.Interaction] = None,
    message: Optional[discord.Message] = None,
    content: str = "",
    mention_user: bool = True,
) -> None:
    """
    Send long messages by splitting them into chunks.

    Args:
        interaction: Discord interaction (for slash commands)
        message: Discord message (for mention replies)
        content: Message content to send
        mention_user: Whether to mention the user
    """
    max_length = Config.MAX_RESPONSE_LENGTH

    if interaction:
        for i, start in enumerate(range(0, len(content), max_length)):
            chunk = content[start : start + max_length]

            if mention_user and i == 0:
                chunk = f"{interaction.user.mention} {chunk}"

            try:
                await interaction.followup.send(chunk)
            except Exception as e:
                logger.error(f"Failed to send followup message: {e}")

    elif message:
        for start in range(0, len(content), max_length):
            chunk = content[start : start + max_length]
            try:
                await message.reply(chunk, mention_author=mention_user)
            except Exception as e:
                logger.error(f"Failed to send reply: {e}")
