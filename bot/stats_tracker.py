"""Statistics tracking for the bot."""

import json
import logging
import os
from collections import Counter
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class StatsTracker:
    """Track bot usage statistics."""

    def __init__(self, stats_file: str = "bot_stats.json"):
        self.stats_file = stats_file
        self.stats = {
            "total_questions": 0,
            "total_responses": 0,
            "questions_by_user": {},
            "questions_today": 0,
            "last_reset": datetime.now().date().isoformat(),
            "most_common_words": {},
            "total_tokens_estimate": 0,
        }
        self.load_stats()

    def load_stats(self):
        """Load statistics from file."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    self.stats = json.load(f)
                logger.info("Statistics loaded")
            except Exception as e:
                logger.error(f"Failed to load stats: {e}")

    def save_stats(self):
        """Save statistics to file."""
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def record_question(self, user_id: int, question: str):
        """Record a question from a user."""
        # Check if day has changed
        today = datetime.now().date().isoformat()
        if self.stats["last_reset"] != today:
            self.stats["questions_today"] = 0
            self.stats["last_reset"] = today

        # Update counts
        self.stats["total_questions"] += 1
        self.stats["questions_today"] += 1

        # Track by user
        user_key = str(user_id)
        self.stats["questions_by_user"][user_key] = (
            self.stats["questions_by_user"].get(user_key, 0) + 1
        )

        # Estimate tokens (rough: 1 token ≈ 4 chars)
        self.stats["total_tokens_estimate"] += len(question) // 4

        self.save_stats()

    def record_response(self, response: str):
        """Record a bot response."""
        self.stats["total_responses"] += 1
        self.stats["total_tokens_estimate"] += len(response) // 4
        self.save_stats()

    def get_summary(self) -> Dict:
        """Get statistics summary."""
        return {
            "総質問数": self.stats["total_questions"],
            "今日の質問数": self.stats["questions_today"],
            "総応答数": self.stats["total_responses"],
            "ユニークユーザー数": len(self.stats["questions_by_user"]),
            "推定トークン数": f'{self.stats["total_tokens_estimate"]:,}',
        }

    def get_top_users(self, limit: int = 5) -> list:
        """Get top users by question count."""
        sorted_users = sorted(
            self.stats["questions_by_user"].items(), key=lambda x: x[1], reverse=True
        )
        return sorted_users[:limit]
