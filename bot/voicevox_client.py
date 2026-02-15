"""VOICEVOX TTS client for voice synthesis."""

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class VOICEVOXClient:
    """Client for VOICEVOX TTS engine."""

    # Character IDs (ずんだもん中心)
    CHARACTERS = {
        "zundamon_normal": 3,  # ずんだもん（ノーマル）
        "zundamon_sweet": 1,  # ずんだもん（あまあま）
        "zundamon_tsundere": 7,  # ずんだもん（ツンツン）
        "zundamon_sexy": 5,  # ずんだもん（セクシー）
        "metan_normal": 2,  # 四国めたん（ノーマル）
        "tsumugi_normal": 8,  # 春日部つむぎ（ノーマル）
    }

    def __init__(self, host: str = "http://localhost:50021", timeout: int = 30):
        """
        Initialize VOICEVOX client.

        Args:
            host: VOICEVOX API host
            timeout: Request timeout
        """
        self.host = host
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if VOICEVOX is running."""
        try:
            response = requests.get(f"{self.host}/version", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"VOICEVOX health check failed: {e}")
            return False

    def synthesize(
        self, text: str, character: str = "zundamon_normal", speed: float = 1.0
    ) -> Optional[bytes]:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            character: Character name
            speed: Speech speed (0.5 - 2.0)

        Returns:
            Audio data (WAV format) or None
        """
        speaker_id = self.CHARACTERS.get(character, 3)

        try:
            # Step 1: Generate audio query
            query_response = requests.post(
                f"{self.host}/audio_query",
                params={"text": text, "speaker": speaker_id},
                timeout=self.timeout,
            )
            query_response.raise_for_status()
            query_data = query_response.json()

            # Adjust speed
            query_data["speedScale"] = speed

            # Step 2: Synthesize audio
            synthesis_response = requests.post(
                f"{self.host}/synthesis",
                params={"speaker": speaker_id},
                json=query_data,
                timeout=self.timeout,
            )
            synthesis_response.raise_for_status()

            return synthesis_response.content

        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to VOICEVOX at {self.host}")
            return None
        except requests.exceptions.Timeout:
            logger.error("VOICEVOX request timed out")
            return None
        except Exception as e:
            logger.exception(f"VOICEVOX synthesis failed: {e}")
            return None

    def get_speakers(self) -> list:
        """Get list of available speakers."""
        try:
            response = requests.get(f"{self.host}/speakers", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get speakers: {e}")
            return []
