"""Message handling utilities."""
import logging
import asyncio
from typing import Optional

import discord

from config import Config

logger = logging.getLogger(__name__)


async def send_long_message(
    interaction: Optional[discord.Interaction] = None,
    message: Optional[discord.Message] = None,
    content: str = "",
    mention_user: bool = True
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
            chunk = content[start:start + max_length]
            
            if mention_user and i == 0:
                chunk = f"{interaction.user.mention} {chunk}"
            
            try:
                await interaction.followup.send(chunk)
            except Exception as e:
                logger.error(f"Failed to send followup message: {e}")
    
    elif message:
        for start in range(0, len(content), max_length):
            chunk = content[start:start + max_length]
            try:
                await message.reply(chunk, mention_author=mention_user)
            except Exception as e:
                logger.error(f"Failed to send reply: {e}")


async def send_streaming_message(
    message: discord.Message,
    stream_generator,
    mention_user: bool = True,
) -> None:
    """
    Send streaming response with live updates.
    
    Args:
        message: Discord message to reply to
        stream_generator: Generator yielding response chunks
        mention_user: Whether to mention the user
    """
    buffer = ""
    sent_message = None
    update_counter = 0
    last_update_length = 0
    
    try:
        for chunk in stream_generator:
            buffer += chunk
            update_counter += 1
            
            # Update message every N chunks to avoid rate limits
            if update_counter >= Config.STREAMING_UPDATE_INTERVAL:
                current_length = len(buffer)
                # Only update if there's meaningful new content
                if current_length > last_update_length:
                    if sent_message is None:
                        # First message
                        content = f"{message.author.mention} {buffer}" if mention_user else buffer
                        sent_message = await message.reply(content[:Config.MAX_RESPONSE_LENGTH])
                        last_update_length = current_length
                    else:
                        # Update existing message
                        try:
                            await sent_message.edit(content=buffer[:Config.MAX_RESPONSE_LENGTH])
                            last_update_length = current_length
                        except discord.errors.HTTPException:
                            # If edit fails (rate limit), skip this update
                            pass
                
                update_counter = 0
        
        # Final update with complete response (only if there's new content)
        if buffer and len(buffer) > last_update_length:
            if sent_message is None:
                # No message sent yet (response was too short for interval)
                content = f"{message.author.mention} {buffer}" if mention_user else buffer
                await message.reply(content[:Config.MAX_RESPONSE_LENGTH])
            else:
                # Update with final content
                try:
                    await sent_message.edit(content=buffer[:Config.MAX_RESPONSE_LENGTH])
                except Exception:
                    pass
                    
    except Exception as e:
        logger.error(f"Error in streaming message: {e}")
        if sent_message:
            try:
                await sent_message.edit(content=f"{buffer}\n\n❌ エラーが発生しました")
            except Exception:
                pass