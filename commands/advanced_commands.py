"""Additional slash commands for advanced features."""

import asyncio
import io
import logging

import discord
from discord import app_commands

from bot.templates import apply_template, list_templates

logger = logging.getLogger(__name__)


def setup_advanced_commands(bot):
    """Setup advanced slash commands."""

    # テンプレート関連
    @bot.tree.command(name="templates", description="利用可能なプロンプトテンプレート一覧")
    async def templates_command(interaction: discord.Interaction):
        """List available prompt templates."""
        templates = list_templates()

        embed = discord.Embed(
            title="📝 プロンプトテンプレート",
            description="用途に応じたテンプレートを選択できます",
            color=discord.Color.blue(),
        )

        for key, template in templates.items():
            embed.add_field(
                name=f"{template['name']} (`/use_template {key}`)",
                value=template["description"],
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="use_template", description="プロンプトテンプレートを使用")
    @app_commands.describe(template_name="テンプレート名", question="質問内容")
    @app_commands.choices(
        template_name=[
            app_commands.Choice(name="💻 コーディング支援", value="coding"),
            app_commands.Choice(name="🌐 翻訳モード", value="translation"),
            app_commands.Choice(name="✨ 創作モード", value="creative"),
            app_commands.Choice(name="📝 要約モード", value="summary"),
            app_commands.Choice(name="👨‍🏫 教師モード", value="teacher"),
            app_commands.Choice(name="💼 ビジネスモード", value="business"),
            app_commands.Choice(name="🐛 デバッグモード", value="debug"),
            app_commands.Choice(name="💡 ブレインストーミング", value="brainstorm"),
        ]
    )
    async def use_template_command(
        interaction: discord.Interaction, template_name: str, question: str
    ):
        """Use a prompt template."""
        logger.info(
            f"📝 Template: {template_name} | User: {interaction.user} | Q: {question[:30]}..."
        )

        try:
            await interaction.response.defer(ephemeral=False)
        except discord.errors.NotFound:
            return

        try:
            user_id = interaction.user.id

            # Apply template
            enhanced_question = apply_template(template_name, question)

            # Generate response
            reply = await asyncio.to_thread(bot.ollama.generate, enhanced_question)

            # Save to history
            bot.memory.add_message(user_id, "user", question)
            bot.memory.add_message(user_id, "assistant", reply)

            # Track stats
            bot.stats.record_question(user_id, question)
            bot.stats.record_response(reply)

            await interaction.followup.send(f"**テンプレート:** {template_name}\n\n{reply}"[:2000])
        except Exception as e:
            logger.error(f"Error in use_template command: {e}")
            await interaction.followup.send("❌ エラーが発生しました。")

    # モデル管理
    @bot.tree.command(name="list_models", description="利用可能なモデル一覧")
    async def list_models_command(interaction: discord.Interaction):
        """List available Ollama models."""
        models = bot.model_manager.list_models()

        if not models:
            await interaction.response.send_message(
                "⚠️ モデルが見つかりませんでした。", ephemeral=True
            )
            return

        embed = discord.Embed(title="🤖 利用可能なモデル", color=discord.Color.green())

        for model in models[:10]:  # Limit to 10
            name = model.get("name", "Unknown")
            size = model.get("size", 0)
            size_gb = size / (1024**3) if size else 0

            embed.add_field(name=name, value=f"サイズ: {size_gb:.2f} GB", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # 統計情報
    @bot.tree.command(name="stats", description="Bot使用統計を表示")
    async def stats_command(interaction: discord.Interaction):
        """Display bot usage statistics."""
        summary = bot.stats.get_summary()

        embed = discord.Embed(title="📊 Bot統計情報", color=discord.Color.purple())

        for key, value in summary.items():
            embed.add_field(name=key, value=str(value), inline=True)

        # Top users
        top_users = bot.stats.get_top_users(3)
        if top_users:
            top_str = "\n".join([f"<@{uid}>: {count}回" for uid, count in top_users])
            embed.add_field(name="🏆 トップユーザー", value=top_str, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # エクスポート
    @bot.tree.command(name="export_chat", description="会話履歴をエクスポート")
    async def export_chat_command(interaction: discord.Interaction):
        """Export conversation history."""
        user_id = interaction.user.id
        conversation = bot.memory.get_context(user_id)

        if not conversation:
            await interaction.response.send_message("会話履歴がありません。", ephemeral=True)
            return

        # Export as markdown
        markdown = bot.export_manager.export_conversation_markdown(
            user_name=interaction.user.name, conversation=conversation
        )

        # Create file
        file_content = markdown.encode("utf-8")
        file = discord.File(
            io.BytesIO(file_content), filename=f"conversation_{interaction.user.name}.md"
        )

        await interaction.response.send_message("📄 会話履歴をエクスポートしました:", file=file)

    @bot.tree.command(name="export_memory", description="学習内容をエクスポート")
    async def export_memory_command(interaction: discord.Interaction):
        """Export learned facts."""
        facts = bot.memory.learned_facts

        if not facts:
            await interaction.response.send_message("学習内容がありません。", ephemeral=True)
            return

        # Export as JSON
        json_content = bot.export_manager.export_memory_json(facts)

        file = discord.File(io.BytesIO(json_content.encode("utf-8")), filename="memory.json")

        await interaction.response.send_message("🧠 学習内容をエクスポートしました:", file=file)

    # 画像分析
    @bot.tree.command(name="analyze_image", description="画像を分析（添付が必要）")
    @app_commands.describe(question="画像についての質問（省略可）")
    async def analyze_image_command(interaction: discord.Interaction, question: str = None):
        """Analyze an attached image."""
        # Check if image is attached
        if not interaction.message or not interaction.message.attachments:
            await interaction.response.send_message(
                "⚠️ 画像を添付してください。メッセージに画像を添付してからコマンドを実行してください。",
                ephemeral=True,
            )
            return

        attachment = interaction.message.attachments[0]

        # Check if it's an image
        if not attachment.content_type or not attachment.content_type.startswith("image"):
            await interaction.response.send_message(
                "⚠️ 画像ファイルを添付してください。", ephemeral=True
            )
            return

        try:
            await interaction.response.defer(ephemeral=False)
        except discord.errors.NotFound:
            return

        try:
            # Download image
            image_data = await attachment.read()

            # Analyze
            prompt = question or "この画像について詳しく説明してください。"
            result = await asyncio.to_thread(bot.vision.analyze_image, image_data, prompt)

            await interaction.followup.send(f"🖼️ **画像分析結果:**\n\n{result}"[:2000])
        except Exception as e:
            logger.error(f"Error in analyze_image command: {e}")
            await interaction.followup.send("❌ 画像分析に失敗しました。")
