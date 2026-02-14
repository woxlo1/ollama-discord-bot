"""Ollama API client."""
import logging
import requests

from config import Config

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, host: str, model: str, timeout: int = 180):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama API host URL
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.host = host
        self.model = model
        self.timeout = timeout
        self.url = f"{host}/api/generate"
    
    def generate(self, prompt: str) -> str:
        """
        Generate response from Ollama.
        
        Args:
            prompt: User input prompt
            
        Returns:
            Generated response text
        """
        full_prompt = Config.get_full_prompt(prompt)
        
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("response", "モデルから応答がありませんでした。")
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out.")
            return "⏳ モデルの応答がタイムアウトしました。サーバーが起動しているか確認してください。"
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to Ollama at {self.host}")
            return f"⚠️ Ollamaサーバーに接続できません ({self.host})"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return "⚠️ Ollama APIとの通信に失敗しました。"
            
        except Exception as e:
            logger.exception(f"Unexpected error in generate: {e}")
            return "❌ 予期しないエラーが発生しました。"
    
    def health_check(self) -> bool:
        """
        Check if Ollama server is healthy.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
