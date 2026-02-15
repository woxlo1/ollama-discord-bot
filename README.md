# 🤖 Ollama Discord Bot

[![CI](https://github.com/yourusername/ollama-discord-bot/workflows/CI/badge.svg)](https://github.com/yourusername/ollama-discord-bot/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)

ローカルLLM (Ollama) を活用したDiscord Botです。日本語での会話に最適化されています。

## ✨ 特徴

- 🚀 ローカルで動作するLLMを使用（データはサーバーに送信されません）
- 💬 **メンション & スラッシュコマンド両対応**
- 🧠 **会話から学習し進化する**（会話履歴・学習機能）
- 📝 **8種類のプロンプトテンプレート**（コーディング、翻訳、創作など）
- 🖼️ **画像認識機能**（LLaVAモデル対応）
- 🎤 **音声読み上げ機能**（VOICEVOX + ずんだもん）
- 📊 **使用統計トラッキング**
- 💾 **会話・学習内容のエクスポート**
- 🔄 **モデル管理機能**
- 🐳 Docker & Docker Composeで簡単セットアップ
- 📝 長文レスポンスの自動分割
- ⚙️ 環境変数による柔軟な設定
- 🏗️ モジュール化された整理されたコード構造

## 📋 必要要件

- Python 3.11以上
- [Ollama](https://ollama.ai/) （ローカル実行の場合）
- Discord Bot Token
- （オプション）[VOICEVOX](https://voicevox.hiroshiba.jp/) - 音声読み上げ用
- （オプション）FFmpeg - 音声機能用

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

# オプション: 画像認識用
ollama pull llava
```

### 3. Discord Botの作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 新しいアプリケーションを作成
3. **Bot タブ**:
   - トークンを取得
   - **Privileged Gateway Intents** で `MESSAGE CONTENT INTENT` を有効化
4. **OAuth2 → URL Generator** で以下を選択:
   - **Scopes**: `bot`, `applications.commands`
   - **Bot Permissions**: 
     - `Send Messages`
     - `Use Slash Commands`
     - `Read Message History`
     - `Connect` (音声機能用)
     - `Speak` (音声機能用)

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

### 💬 メンション（カジュアル）

```
@BotName こんにちは！
@BotName Pythonについて教えて
```

### ⚡ スラッシュコマンド

#### 基本コマンド
```bash
/ask question: Pythonの基本について教えて  # AIに質問
/model  # モデル情報
/help   # ヘルプ
```

#### 学習機能
```bash
/memory  # 学習内容を表示
/reset   # 会話履歴をリセット
```

#### プロンプトテンプレート
```bash
/templates  # テンプレート一覧
/use_template coding Pythonのソート実装  # テンプレート使用
```

#### 画像認識
```bash
/analyze_image  # 画像を添付して分析
```

#### 統計・エクスポート
```bash
/stats  # 使用統計
/export_chat  # 会話をMarkdownで保存
/export_memory  # 学習内容をJSON保存
```

#### モデル管理
```bash
/list_models  # 利用可能なモデル一覧
```

#### 🎤 音声機能（要VOICEVOX）
```bash
/vc_join  # VCに参加
/vc_ask question: Pythonについて  # 質問→音声読み上げ
/vc_character  # ずんだもん等のキャラ変更
/speak text: こんにちは  # テキスト読み上げ
/vc_status  # 接続状態確認
/vc_leave  # VC退出
```

### 🧠 学習機能について

- **会話履歴**: ユーザーごとに最新10件の会話を記憶
- **文脈理解**: 「それ」「その話」などの代名詞も理解可能
- **共有学習**: 全ユーザーの会話から学習（最大100件）
- **自動保存**: 学習内容は`bot_memory.json`に保存

## ⚙️ 設定

`.env` ファイルで以下の設定が可能です：

### 基本設定
| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `DISCORD_TOKEN` | Discord Botトークン | 必須 |
| `OLLAMA_MODEL` | 使用するOllamaモデル | `llama3` |
| `OLLAMA_HOST` | OllamaのホストURL | `http://localhost:11434` |
| `BOT_PREFIX` | コマンドプレフィックス | `!` |
| `MAX_RESPONSE_LENGTH` | 1メッセージの最大文字数 | `1900` |
| `REQUEST_TIMEOUT` | APIリクエストタイムアウト(秒) | `180` |
| `LOG_LEVEL` | ログレベル | `INFO` |

### 音声機能設定
| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `VOICEVOX_HOST` | VOICEVOXのURL | `http://localhost:50021` |
| `VOICEVOX_PATH` | VOICEVOX実行ファイルパス (オプション) | 空 |
| `FFMPEG_PATH` | FFmpeg実行ファイルパス (空で自動検出) | 空 |

### 設定例

**Windows:**
```bash
DISCORD_TOKEN=your_token_here
VOICEVOX_HOST=http://localhost:50021
FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe
```

**macOS/Linux:**
```bash
DISCORD_TOKEN=your_token_here
VOICEVOX_HOST=http://localhost:50021
# FFMPEG_PATH は不要（自動検出）
```

## 🎤 音声機能のセットアップ

詳細は [VOICEVOX_SETUP.md](VOICEVOX_SETUP.md) を参照してください。

### クイックセットアップ

1. **VOICEVOXをダウンロード**: https://voicevox.hiroshiba.jp/
2. **FFmpegをインストール**:
   ```bash
   # Windows
   choco install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Linux
   sudo apt install ffmpeg
   ```
3. **VOICEVOXを起動** (http://localhost:50021)
4. **Botを起動**して `/vc_join` で参加

## 🏗️ プロジェクト構成

```
ollama-discord-bot/
├── bot/                    # Botコア
│   ├── client.py          # メインクライアント
│   ├── ollama_client.py   # Ollama API
│   ├── memory.py          # 学習・記憶システム
│   ├── templates.py       # プロンプトテンプレート
│   ├── vision.py          # 画像認識
│   ├── voice_manager.py   # VC管理
│   ├── voicevox_client.py # VOICEVOX連携
│   ├── model_manager.py   # モデル管理
│   ├── stats_tracker.py   # 統計
│   └── export_manager.py  # エクスポート
├── commands/              # コマンド
│   ├── slash_commands.py  # 基本コマンド
│   ├── advanced_commands.py # 高度な機能
│   ├── voice_commands.py  # VC関連
│   └── events.py          # イベント
├── config/                # 設定
│   └── settings.py        # 環境変数管理
├── utils/                 # ユーティリティ
│   ├── message_handler.py
│   └── logger.py
├── main.py                # エントリーポイント
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 📝 全コマンド一覧（19個）

### 基本 (5)
- `/ask` - AI質問
- `/reset` - 会話リセット
- `/memory` - 学習内容表示
- `/model` - モデル情報
- `/help` - ヘルプ

### 高度な機能 (8)
- `/templates` - テンプレート一覧
- `/use_template` - テンプレート使用
- `/analyze_image` - 画像分析
- `/stats` - 統計情報
- `/export_chat` - 会話エクスポート
- `/export_memory` - 記憶エクスポート
- `/list_models` - モデル一覧

### 音声機能 (6)
- `/vc_join` - VC参加
- `/vc_leave` - VC退出
- `/vc_ask` - 音声で回答
- `/speak` - テキスト読み上げ
- `/vc_character` - キャラ変更
- `/vc_status` - 状態確認

## 🛠️ 開発

### 開発環境のセットアップ

```bash
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
curl http://localhost:11434/api/tags
ollama list
```

### Botがオンラインにならない

- Discord Tokenを確認
- Privileged Gateway Intentsを有効化
- Bot権限を確認（Connect, Speak含む）
- ログを確認: `docker-compose logs bot`

### VC接続エラー (4006)

[VC_TROUBLESHOOTING.md](VC_TROUBLESHOOTING.md) を参照:
1. Discord Developer PortalでIntentを有効化
2. Bot権限に「Connect」「Speak」を追加
3. 新しいURLでBotを再招待

### FFmpegが見つからない

```bash
# インストール確認
ffmpeg -version

# Windowsの場合は.envでパス指定
FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe
```

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

プルリクエストを歓迎します！大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📚 参考リンク

- [Ollama](https://ollama.ai/)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [VOICEVOX](https://voicevox.hiroshiba.jp/)
- [FFmpeg](https://ffmpeg.org/)

## 🎉 機能一覧

✅ 会話履歴・学習機能  
✅ プロンプトテンプレート (8種類)  
✅ 画像認識 (LLaVA)  
✅ 音声読み上げ (VOICEVOX + ずんだもん)  
✅ 統計トラッキング  
✅ データエクスポート  
✅ モデル管理  
✅ Docker対応  
✅ 環境変数で柔軟な設定