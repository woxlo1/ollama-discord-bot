import os
import logging
import discord
import requests
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import asyncio

# ==============================
# Load Environment
# ==============================
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN is not set in environment variables.")

# ==============================
# Logging Setup
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ==============================
# Discord Bot Setup
# ==============================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # <-- tree を定義

# ==============================
# Ollama API
# ==============================
def ask_ollama(prompt: str) -> str:
    url = f"{OLLAMA_HOST}/api/generate"
    full_prompt = f"""
あなたは優秀な日本語アシスタントです。
必ず日本語で自然に回答してください。

ユーザーの質問:
{prompt}
"""
    try:
        response = requests.post(
            url,
            json={"model": OLLAMA_MODEL, "prompt": full_prompt, "stream": False},
            timeout=180
        )
        response.raise_for_status()
        return response.json().get("response", "モデルから応答がありませんでした。")
    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out.")
        return "⏳ モデルの応答がタイムアウトしました。"
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama request failed: {e}")
        return "⚠ Ollama APIとの通信に失敗しました。"
    except Exception:
        logger.exception("Unexpected error in ask_ollama")
        return "❌ 予期しないエラーが発生しました。"

# ==============================
# Utility: Long Reply
# ==============================
async def send_long_reply_interaction(interaction: discord.Interaction, content: str, mention_user=True):
    """defer した interaction に長文を分割して送信 + メンション"""
    max_length = 1900

    for start in range(0, len(content), max_length):
        chunk = content[start:start + max_length]

        if mention_user:
            chunk = f"{interaction.user.mention} {chunk}"  # ここで明示的にメンション

        try:
            await interaction.followup.send(chunk)
        except Exception as e:
            logger.error(f"❌ followup.send でエラー: {e}")

async def send_long_reply_message(message, content: str, mention_author=False):
    max_length = 1900
    for i in range(0, len(content), max_length):
        await message.reply(content[i:i + max_length], mention_author=mention_author)

# ==============================
# Discord Events
# ==============================
@bot.event
async def on_ready():
    await tree.sync()
    logger.info(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not user_input:
            await message.reply("💬 何か話しかけてね！", mention_author=True)
            return

        logger.info(f"User: {message.author} | Prompt: {user_input}")
        async with message.channel.typing():
            reply = ask_ollama(user_input)
        await send_long_reply_message(message, reply, mention_author=True)

# ==============================
# Slash Command /ask
# ==============================
@tree.command(name="ask", description="AIに質問")
async def ask(interaction: discord.Interaction, question: str):
    logger.info(f"Slash Ask | User: {interaction.user} | Prompt: {question}")

    # defer して処理中を表示
    await interaction.response.defer(ephemeral=False)

    # Ollama API を非同期呼び出し
    reply = await asyncio.to_thread(ask_ollama, question)

    # 長文返信 + メンション
    await send_long_reply_interaction(interaction, reply, mention_user=True)

# ==============================
# Run Bot
# ==============================
if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except Exception:
        logger.exception("❌ Failed to start Discord bot")
