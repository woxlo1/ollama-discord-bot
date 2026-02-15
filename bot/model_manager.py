"""Model management for Ollama."""

import logging
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)


class ModelManager:
    """Manage Ollama models."""

    def __init__(self, host: str):
        self.host = host

    def list_models(self) -> List[dict]:
        """List all available models."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama library."""
        try:
            response = requests.post(
                f"{self.host}/api/pull", json={"name": model_name}, timeout=300, stream=True
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False

    def delete_model(self, model_name: str) -> bool:
        """Delete a model."""
        try:
            response = requests.delete(
                f"{self.host}/api/delete", json={"name": model_name}, timeout=30
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to delete model {model_name}: {e}")
            return False

    def get_model_info(self, model_name: str) -> Optional[dict]:
        """Get information about a specific model."""
        try:
            response = requests.post(f"{self.host}/api/show", json={"name": model_name}, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get model info for {model_name}: {e}")
            return None
