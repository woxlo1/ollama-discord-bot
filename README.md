# 🤖 Ollama Discord Bot

[![CI](https://github.com/yourusername/ollama-discord-bot/workflows/CI/badge.svg)](https://github.com/yourusername/ollama-discord-bot/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)

ローカルLLM (Ollama) を活用したDiscord Botです。日本語での会話に最適化されています。

## ✨ 特徴

- 🚀 ローカルで動作するLLMを使用（データはサーバーに送信されません）
- ⚡ スラッシュコマンドで簡単に質問
- 🐳 Docker & Docker Composeで簡単セットアップ
- 📝 長文レスポンスの自動分割
- ⚙️ 環境変数による柔軟な設定
- 🏗️ モジュール化された整理されたコード構造

## 📋 必要要件

- Python 3.11以上
- [Ollama](https://ollama.ai/) （ローカル実行の場合）
- Discord Bot Token

## 🚀 クイックスタート

### 1. Ollamaのインストール

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# https://ollama.ai/download からインストーラーをダウンロード
```

### 2. モデルのダウンロード

```bash
ollama pull llama3
# または他のモデル: mistral, codellama, など
```

### 3. Discord Botの作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 新しいアプリケーションを作成
3. Bot タブからトークンを取得
4. OAuth2 → URL Generator で以下を選択:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Use Slash Commands`, `Read Message History`

### 4. 環境設定

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/ollama-discord-bot.git
cd ollama-discord-bot

# 環境変数の設定
cp .env.example .env
# .env を編集してDISCORD_TOKENを設定
```

### 5. 実行方法

#### 方法A: Docker Compose (推奨)

```bash
docker-compose up -d
```

#### 方法B: Python直接実行

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 実行
python main.py
```

## 💡 使い方

### スラッシュコマンド

```
/ask question: Pythonの基本について教えて
/model  # 現在のモデル情報を表示
/help   # ヘルプを表示
```

## ⚙️ 設定

`.env` ファイルで以下の設定が可能です：

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `DISCORD_TOKEN` | Discord Botトークン | 必須 |
| `OLLAMA_MODEL` | 使用するOllamaモデル | `llama3` |
| `OLLAMA_HOST` | OllamaのホストURL | `http://localhost:11434` |
| `BOT_PREFIX` | コマンドプレフィックス | `!` |
| `MAX_RESPONSE_LENGTH` | 1メッセージの最大文字数 | `1900` |
| `REQUEST_TIMEOUT` | APIリクエストタイムアウト(秒) | `180` |
| `LOG_LEVEL` | ログレベル | `INFO` |

## 🏗️ プロジェクト構成

```
ollama-discord-bot/
├── bot/                    # Botコア
│   ├── __init__.py
│   ├── client.py          # Discord Bot クライアント
│   └── ollama_client.py   # Ollama API クライアント
├── commands/              # コマンド
│   ├── __init__.py
│   ├── slash_commands.py  # スラッシュコマンド
│   └── events.py          # イベントハンドラー
├── config/                # 設定
│   ├── __init__.py
│   └── settings.py        # 設定管理
├── utils/                 # ユーティリティ
│   ├── __init__.py
│   ├── message_handler.py # メッセージ処理
│   └── logger.py          # ロギング設定
├── tests/                 # テスト
├── .github/
│   └── workflows/
│       └── ci.yml         # CI/CD設定
├── main.py                # エントリーポイント
├── requirements.txt       # 依存関係
├── requirements-dev.txt   # 開発用依存関係
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🛠️ 開発

### 開発環境のセットアップ

```bash
# 開発用依存関係のインストール
pip install -r requirements-dev.txt

# コードフォーマット
black .
isort .

# Linting
flake8 .
```

### テスト実行

```bash
pytest
```

## 🐛 トラブルシューティング

### Ollamaに接続できない

```bash
# Ollamaが起動しているか確認
curl http://localhost:11434/api/tags

# モデルがダウンロードされているか確認
ollama list
```

### Botがオンラインにならない

- Discord Tokenが正しいか確認
- Botに必要な権限が付与されているか確認
- ログを確認: `docker-compose logs bot`

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

プルリクエストを歓迎します！大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📚 参考リンク

- [Ollama](https://ollama.ai/)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/applications)