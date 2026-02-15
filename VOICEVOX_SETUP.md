# 🎤 VOICEVOX音声読み上げ機能のセットアップ

## 必要なもの

1. **VOICEVOX** - 無料の音声合成ソフト
2. **FFmpeg** - 音声処理ライブラリ

## セットアップ手順

### 1. VOICEVOXのインストール

#### Windows
```bash
# https://voicevox.hiroshiba.jp/ からダウンロード
# インストーラーを実行
```

#### macOS
```bash
# https://voicevox.hiroshiba.jp/ からダウンロード
# アプリケーションフォルダにコピー
```

#### Linux
```bash
# AppImageをダウンロード
wget https://github.com/VOICEVOX/voicevox/releases/latest/download/VOICEVOX.AppImage
chmod +x VOICEVOX.AppImage
./VOICEVOX.AppImage
```

### 2. FFmpegのインストール

#### Windows
```bash
# Chocolateyを使用
choco install ffmpeg

# または https://ffmpeg.org/download.html からダウンロード
```

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### 3. VOICEVOXを起動

```bash
# VOICEVOXアプリケーションを起動
# デフォルトで http://localhost:50021 で動作します
```

### 4. Botの起動

```bash
# Pythonの場合
pip install -r requirements.txt
python main.py

# Dockerの場合
docker-compose up -d
```

## 使い方

### VCに参加

```bash
/vc_join  # 自分が参加しているVCにBotが参加
```

### AIに質問（音声読み上げ）

```bash
/vc_ask question: Pythonについて教えて
```

### キャラクター変更

```bash
/vc_character  # ずんだもん、めたん、つむぎなどを選択
```

### カスタムテキスト読み上げ

```bash
/speak text: こんにちは！
```

### VCから退出

```bash
/vc_leave
```

### 状態確認

```bash
/vc_status
```

## 利用可能なキャラクター

- 🍡 **ずんだもん（ノーマル）** - 標準的な声
- 💕 **ずんだもん（あまあま）** - 甘い声
- 😤 **ずんだもん（ツンツン）** - ツンデレ
- 😏 **ずんだもん（セクシー）** - セクシー
- 🌸 **四国めたん** - 落ち着いた声
- 🌺 **春日部つむぎ** - 明るい声

## トラブルシューティング

### VOICEVOXに接続できない

```bash
# VOICEVOXが起動しているか確認
curl http://localhost:50021/version

# 起動していない場合はVOICEVOXアプリを起動
```

### FFmpegが見つからない

```bash
# インストール確認
ffmpeg -version

# ない場合は上記の手順でインストール
```

### Botがエラーを出す

```bash
# ログを確認
docker-compose logs bot

# または
python main.py
```

### 音声が再生されない

1. Discordでマイク権限を確認
2. VOICEVOXが起動しているか確認
3. FFmpegがインストールされているか確認
4. VCに正しく参加しているか確認

## Docker環境での注意点

Dockerを使用する場合、VOICEVOXは**ホストマシン**で起動する必要があります。

```yaml
# docker-compose.yml
environment:
  - VOICEVOX_HOST=http://host.docker.internal:50021  # macOS/Windows
  # または
  - VOICEVOX_HOST=http://172.17.0.1:50021  # Linux
```

## 音声の調整

コード内で調整可能：

```python
# bot/voice_manager.py
await bot.voice_manager.speak(
    guild_id, 
    text, 
    speed=1.2  # 速度調整 (0.5 - 2.0)
)
```

## リソース

- [VOICEVOX公式](https://voicevox.hiroshiba.jp/)
- [VOICEVOX API仕様](https://voicevox.github.io/voicevox_engine/api/)
- [FFmpeg公式](https://ffmpeg.org/)
- [discord.py Voice](https://discordpy.readthedocs.io/en/stable/api.html#voice-related)
