"""Event handlers for the bot."""

import asyncio
import logging

import discord
from discord.ext import commands

from bot.memory import LearningSystem
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
        # Ignore bot messages
        if message.author.bot:
            return

        # Process commands first (important!)
        await bot.process_commands(message)

        # Only respond to mentions that are not commands
        if bot.user in message.mentions and not message.content.startswith("/"):
            user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()

            if not user_input:
                await message.reply("💬 何か話しかけてね！", mention_author=True)
                return

            logger.info(f"📨 Mention | User: {message.author} | Input: {user_input[:50]}...")

            async with message.channel.typing():
                try:
                    user_id = message.author.id

                    # Get enhanced prompt with history and learned facts
                    enhanced_question = bot.memory.get_enhanced_prompt(user_id, user_input)

                    # Generate response
                    reply = await asyncio.to_thread(bot.ollama.generate, enhanced_question)

                    # Save to conversation history
                    bot.memory.add_message(user_id, "user", user_input)
                    bot.memory.add_message(user_id, "assistant", reply)

                    # Try to learn from this interaction
                    learned = LearningSystem.extract_learnable_info(user_input, reply)
                    if learned:
                        bot.memory.learn_fact(learned, source=f"user_{user_id}")
                        logger.info(f"🧠 Learned: {learned[:50]}...")

                    # mention_author=True to avoid mention loops
                    await send_long_message(message=message, content=reply, mention_user=True)
                except Exception as e:
                    logger.error(f"Error in mention handler: {e}")
                    await message.reply("❌ エラーが発生しました。", mention_author=True)

    @bot.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return

        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ エラーが発生しました: {str(error)}")
