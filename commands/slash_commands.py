"""Slash commands for the bot."""
import asyncio
import logging

import discord
from discord import app_commands

from bot.memory import LearningSystem
from config import Config
from utils.message_handler import send_long_message

logger = logging.getLogger(__name__)


def setup_slash_commands(bot):
    """
    Setup bot slash commands.
    
    Args:
        bot: OllamaBot instance
    """
    
    @bot.tree.command(name="ask", description="AIに質問する（会話履歴を考慮）")
    @app_commands.describe(question="質問内容")
    async def ask_command(interaction: discord.Interaction, question: str):
        """
        Ask a question to the AI with conversation context.
        
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
        
        # Generate response with context
        try:
            user_id = interaction.user.id
            
            # Get enhanced prompt with history and learned facts
            enhanced_question = bot.memory.get_enhanced_prompt(user_id, question)
            
            # Generate response
            reply = await asyncio.to_thread(bot.ollama.generate, enhanced_question)
            
            # Save to conversation history
            bot.memory.add_message(user_id, 'user', question)
            bot.memory.add_message(user_id, 'assistant', reply)
            
            # Try to learn from this interaction
            learned = LearningSystem.extract_learnable_info(question, reply)
            if learned:
                bot.memory.learn_fact(learned, source=f"user_{user_id}")
                logger.info(f"🧠 Learned: {learned[:50]}...")
            
            await send_long_message(interaction=interaction, content=reply, mention_user=True)
        except Exception as e:
            logger.error(f"Error in ask command: {e}")
            try:
                await interaction.followup.send("❌ エラーが発生しました。もう一度お試しください。")
            except Exception:
                pass
    
    @bot.tree.command(name="reset", description="会話履歴をリセット")
    async def reset_command(interaction: discord.Interaction):
        """Reset conversation history for the user."""
        user_id = interaction.user.id
        bot.memory.clear_context(user_id)
        
        embed = discord.Embed(
            title="🔄 会話リセット",
            description="会話履歴をクリアしました。新しい会話を始めましょう！",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="memory", description="Botが学んだことを表示")
    async def memory_command(interaction: discord.Interaction):
        """Display what the bot has learned."""
        facts = bot.memory.get_learned_facts(10)
        
        embed = discord.Embed(
            title="🧠 Botの記憶",
            description="これまでの会話で学んだことです",
            color=discord.Color.purple()
        )
        
        if facts:
            for i, fact in enumerate(facts, 1):
                embed.add_field(
                    name=f"学習 #{i}",
                    value=fact[:200],
                    inline=False
                )
        else:
            embed.description = "まだ何も学習していません。会話を始めましょう！"
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
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
            description="ローカルLLMを使用したDiscord Botです\n🧠 会話から学習する機能付き！",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="⚡ 基本コマンド",
            value=(
                "`/ask <質問>` - AIに質問（会話履歴を考慮）\n"
                "`/model` - モデル情報表示\n"
                "`/help` - このヘルプ"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🧠 学習機能",
            value=(
                "`/memory` - Botが学んだことを表示\n"
                "`/reset` - 会話履歴をリセット"
            ),
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ その他",
            value="・会話履歴は最新10件まで保持\n・学習した知識は全ユーザーで共有\n・長い応答は自動分割",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
