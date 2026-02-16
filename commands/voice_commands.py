"""Voice channel commands."""

import asyncio
import logging

import discord
from discord import app_commands

from bot.memory import LearningSystem

logger = logging.getLogger(__name__)


def setup_voice_commands(bot):
    """Setup voice channel commands."""

    @bot.tree.command(name="vc_join", description="VCに参加")
    async def vc_join_command(interaction: discord.Interaction):
        """Join user's voice channel."""
        if not interaction.user.voice or not interaction.user.voice.channel:
            embed = discord.Embed(description="❌ VCに入ってから使ってください。", color=0xFF5555)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        channel = interaction.user.voice.channel
        guild_id = interaction.guild.id

        try:
            vc = interaction.guild.voice_client
            if vc and vc.is_connected():
                embed = discord.Embed(description="⚠ すでにVCに接続しています。", color=0xFFFF55)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            voice_client = await channel.connect()
            await bot.voice_manager.speak(guild_id, "よろしくなのだ！")

            embed = discord.Embed(
                description=f"✅ **{channel.name}** に接続しました！\n💬 `/ask` コマンドで質問すると、ずんだもんが読み上げます。",
                color=0x55FF55,
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"VC接続エラー: {e}")
            embed = discord.Embed(
                description="❌ ボイスチャンネルへの接続に失敗しました。", color=0xFF5555
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="vc_leave", description="VCから退出")
    async def vc_leave_command(interaction: discord.Interaction):
        """Leave voice channel."""
        guild_id = interaction.guild.id

        if not bot.voice_manager.is_connected(guild_id):
            await interaction.response.send_message(
                "❌ ボイスチャンネルに接続していません。", ephemeral=True
            )
            return

        # Say goodbye
        await bot.voice_manager.speak(guild_id, "またなのだ！")
        await asyncio.sleep(2)

        await bot.voice_manager.disconnect(guild_id)
        await interaction.response.send_message(
            "👋 ボイスチャンネルから退出しました。", ephemeral=False
        )

    @bot.tree.command(name="vc_character", description="読み上げキャラクターを変更")
    @app_commands.describe(character="キャラクター名")
    @app_commands.choices(
        character=[
            app_commands.Choice(name="🍡 ずんだもん（ノーマル）", value="zundamon_normal"),
            app_commands.Choice(name="💕 ずんだもん（あまあま）", value="zundamon_sweet"),
            app_commands.Choice(name="😤 ずんだもん（ツンツン）", value="zundamon_tsundere"),
            app_commands.Choice(name="😏 ずんだもん（セクシー）", value="zundamon_sexy"),
            app_commands.Choice(name="🌸 四国めたん", value="metan_normal"),
            app_commands.Choice(name="🌺 春日部つむぎ", value="tsumugi_normal"),
        ]
    )
    async def vc_character_command(interaction: discord.Interaction, character: str):
        """Change voice character."""
        guild_id = interaction.guild.id

        if not bot.voice_manager.is_connected(guild_id):
            await interaction.response.send_message(
                "❌ ボイスチャンネルに接続していません。", ephemeral=True
            )
            return

        # Set character
        if bot.voice_manager.set_character(guild_id, character):
            character_names = {
                "zundamon_normal": "ずんだもん（ノーマル）",
                "zundamon_sweet": "ずんだもん（あまあま）",
                "zundamon_tsundere": "ずんだもん（ツンツン）",
                "zundamon_sexy": "ずんだもん（セクシー）",
                "metan_normal": "四国めたん",
                "tsumugi_normal": "春日部つむぎ",
            }

            await interaction.response.send_message(
                f"🎭 読み上げキャラクターを「{character_names[character]}」に変更しました。",
                ephemeral=False,
            )

            # Test voice
            await bot.voice_manager.speak(guild_id, "声を変更したのだ")
        else:
            await interaction.response.send_message(
                "❌ キャラクターの変更に失敗しました。", ephemeral=True
            )

    @bot.tree.command(name="speak", description="指定したテキストを読み上げ")
    @app_commands.describe(text="読み上げるテキスト")
    async def speak_command(interaction: discord.Interaction, text: str):
        """Speak custom text."""
        guild_id = interaction.guild.id

        if not bot.voice_manager.is_connected(guild_id):
            await interaction.response.send_message(
                "❌ ボイスチャンネルに接続していません。`/vc_join` で参加してください。",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(f"🔊 読み上げ: {text[:50]}...", ephemeral=False)
        await bot.voice_manager.speak(guild_id, text)

    @bot.tree.command(name="vc_ask", description="AIに質問して音声で読み上げ")
    @app_commands.describe(question="質問内容")
    async def vc_ask_command(interaction: discord.Interaction, question: str):
        """Ask AI and read response aloud."""
        guild_id = interaction.guild.id

        if not bot.voice_manager.is_connected(guild_id):
            await interaction.response.send_message(
                "❌ ボイスチャンネルに接続していません。`/vc_join` で参加してください。",
                ephemeral=True,
            )
            return

        logger.info(f"🎤 VC Ask | User: {interaction.user} | Q: {question[:50]}...")

        try:
            await interaction.response.defer(ephemeral=False)
        except discord.errors.NotFound:
            return

        try:
            user_id = interaction.user.id

            # Get enhanced prompt
            enhanced_question = bot.memory.get_enhanced_prompt(user_id, question)

            # Generate response
            reply = await asyncio.to_thread(bot.ollama.generate, enhanced_question)

            # Save to history
            bot.memory.add_message(user_id, "user", question)
            bot.memory.add_message(user_id, "assistant", reply)

            # Learn
            learned = LearningSystem.extract_learnable_info(question, reply)
            if learned:
                bot.memory.learn_fact(learned, source=f"user_{user_id}")

            # Track stats
            bot.stats.record_question(user_id, question)
            bot.stats.record_response(reply)

            # Send text response
            await interaction.followup.send(f"**質問:** {question}\n\n**回答:** {reply[:500]}...")

            # Speak response
            await bot.voice_manager.speak(guild_id, reply, speed=1.2)

        except Exception as e:
            logger.error(f"Error in vc_ask command: {e}")
            await interaction.followup.send("❌ エラーが発生しました。")

    @bot.tree.command(name="vc_status", description="VC接続状態を確認")
    async def vc_status_command(interaction: discord.Interaction):
        """Check voice connection status."""
        guild_id = interaction.guild.id

        embed = discord.Embed(title="🎤 ボイスチャンネル状態", color=discord.Color.blue())

        # VOICEVOX status
        voicevox_status = "✅ 起動中" if bot.voice_manager.voicevox.is_available() else "❌ 停止中"
        embed.add_field(name="VOICEVOX", value=voicevox_status, inline=False)

        # Connection status
        if bot.voice_manager.is_connected(guild_id):
            voice_client = bot.voice_manager.voice_clients[guild_id]
            channel_name = voice_client.channel.name
            character = bot.voice_manager.get_current_character(guild_id)

            embed.add_field(name="接続状態", value=f"✅ {channel_name} に接続中", inline=False)
            embed.add_field(name="現在のキャラクター", value=character, inline=False)
        else:
            embed.add_field(name="接続状態", value="❌ 未接続", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
