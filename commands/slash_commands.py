"""Slash commands for the bot."""

import asyncio
import logging

import discord
from discord import app_commands

from config import Config
from utils.message_handler import send_long_message

logger = logging.getLogger(__name__)


def setup_slash_commands(bot):
    """
    Setup bot slash commands.

    Args:
        bot: OllamaBot instance
    """

    @bot.tree.command(name="ask", description="AIに質問する")
    @app_commands.describe(question="質問内容")
    async def ask_command(interaction: discord.Interaction, question: str):
        """
        Ask a question to the AI.

        Args:
            interaction: Discord interaction
            question: User's question
        """
        logger.info(f"💬 Slash Command | User: {interaction.user} | Question: {question[:50]}...")

        # Defer immediately to prevent timeout
        try:
            await interaction.response.defer(ephemeral=False)
        except discord.errors.NotFound:
            logger.error("Interaction expired before defer")
            return

        # Generate response
        try:
            reply = await asyncio.to_thread(bot.ollama.generate, question)
            await send_long_message(interaction=interaction, content=reply, mention_user=True)
        except Exception as e:
            logger.error(f"Error in ask command: {e}")
            try:
                await interaction.followup.send("❌ エラーが発生しました。もう一度お試しください。")
            except Exception:
                pass

    @bot.tree.command(name="model", description="現在使用中のモデル情報を表示")
    async def model_command(interaction: discord.Interaction):
        """Display current model information."""
        embed = discord.Embed(title="🤖 モデル情報", color=discord.Color.blue())
        embed.add_field(name="モデル", value=Config.OLLAMA_MODEL, inline=False)
        embed.add_field(name="ホスト", value=Config.OLLAMA_HOST, inline=False)
        embed.add_field(name="タイムアウト", value=f"{Config.REQUEST_TIMEOUT}秒", inline=False)

        # Health check
        is_healthy = bot.ollama.health_check()
        status = "✅ 正常" if is_healthy else "❌ 接続不可"
        embed.add_field(name="ステータス", value=status, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="help", description="ボットの使い方を表示")
    async def help_command(interaction: discord.Interaction):
        """Display bot help information."""
        embed = discord.Embed(
            title="🤖 Ollama Discord Bot - ヘルプ",
            description="ローカルLLMを使用したDiscord Botです",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="⚡ コマンド",
            value=(
                "`/ask <質問>` - AIに質問\n" "`/model` - モデル情報表示\n" "`/help` - このヘルプ"
            ),
            inline=False,
        )

        embed.add_field(name="ℹ️ その他", value="長い応答は自動的に分割されます", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
