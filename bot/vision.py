"""Vision capabilities using LLaVA model."""

import base64
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class VisionClient:
    """Client for image analysis using LLaVA."""

    def __init__(self, host: str, timeout: int = 180):
        self.host = host
        self.timeout = timeout
        self.url = f"{host}/api/generate"

    def analyze_image(
        self, image_data: bytes, prompt: str = "この画像について詳しく説明してください。"
    ) -> str:
        """
        Analyze an image using LLaVA model.

        Args:
            image_data: Image file bytes
            prompt: Question about the image

        Returns:
            Analysis result
        """
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        try:
            response = requests.post(
                self.url,
                json={
                    "model": "llava",
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json().get("response", "画像の分析ができませんでした。")

        except requests.exceptions.Timeout:
            logger.error("Vision request timed out.")
            return "⏳ 画像分析がタイムアウトしました。画像が大きすぎる可能性があります。"

        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to Ollama at {self.host}")
            return f"⚠️ Ollamaサーバーに接続できません ({self.host})"

        except requests.exceptions.RequestException as e:
            logger.error(f"Vision request failed: {e}")
            if "model 'llava' not found" in str(e).lower():
                return "⚠️ LLaVAモデルがインストールされていません。`ollama pull llava`を実行してください。"
            return "⚠️ 画像分析に失敗しました。"

        except Exception as e:
            logger.exception(f"Unexpected error in analyze_image: {e}")
            return "❌ 予期しないエラーが発生しました。"

    def is_llava_available(self) -> bool:
        """Check if LLaVA model is available."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any("llava" in model.get("name", "").lower() for model in models)
            return False
        except Exception as e:
            logger.error(f"Failed to check LLaVA availability: {e}")
            return False
