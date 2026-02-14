"""Memory and learning system for the bot."""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages conversation history and learning from interactions."""

    def __init__(self, memory_file: str = "bot_memory.json"):
        self.memory_file = memory_file
        self.conversations: Dict[int, List[Dict]] = {}  # user_id -> messages
        self.learned_facts: List[Dict] = []  # Things learned from all users
        self.load_memory()

    def load_memory(self):
        """Load memory from file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.learned_facts = data.get("learned_facts", [])
                logger.info(f"Loaded {len(self.learned_facts)} learned facts")
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")

    def save_memory(self):
        """Save memory to file."""
        try:
            data = {"learned_facts": self.learned_facts, "last_updated": datetime.now().isoformat()}
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("Memory saved successfully")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def add_message(self, user_id: int, role: str, content: str):
        """Add a message to conversation history."""
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        self.conversations[user_id].append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )

        # Keep only last 10 messages per user
        if len(self.conversations[user_id]) > 10:
            self.conversations[user_id] = self.conversations[user_id][-10:]

    def get_context(self, user_id: int) -> List[Dict]:
        """Get conversation context for a user."""
        return self.conversations.get(user_id, [])

    def clear_context(self, user_id: int):
        """Clear conversation history for a user."""
        if user_id in self.conversations:
            del self.conversations[user_id]

    def learn_fact(self, fact: str, source: str = "user"):
        """Learn a new fact from conversations."""
        self.learned_facts.append(
            {"fact": fact, "source": source, "learned_at": datetime.now().isoformat()}
        )

        # Keep only last 100 facts
        if len(self.learned_facts) > 100:
            self.learned_facts = self.learned_facts[-100:]

        self.save_memory()

    def get_learned_facts(self, limit: int = 5) -> List[str]:
        """Get recent learned facts."""
        return [f["fact"] for f in self.learned_facts[-limit:]]

    def get_enhanced_prompt(self, user_id: int, question: str) -> str:
        """Get enhanced prompt with context and learned facts."""
        parts = []

        # Add learned facts
        if self.learned_facts:
            recent_facts = self.get_learned_facts(3)
            parts.append("これまでの会話で学んだこと:")
            parts.extend(f"- {fact}" for fact in recent_facts)
            parts.append("")

        # Add conversation history
        context = self.get_context(user_id)
        if context:
            parts.append("最近の会話履歴:")
            for msg in context[-3:]:  # Last 3 messages
                role = "あなた" if msg["role"] == "assistant" else "ユーザー"
                parts.append(f"{role}: {msg['content'][:100]}")
            parts.append("")

        parts.append(f"新しい質問: {question}")

        return "\n".join(parts)


class LearningSystem:
    """System for extracting learnings from conversations."""

    @staticmethod
    def extract_learnable_info(question: str, response: str) -> Optional[str]:
        """Extract potentially learnable information from Q&A."""
        # Simple heuristics for learning
        learning_triggers = [
            "好き",
            "嫌い",
            "趣味",
            "興味",
            "名前は",
            "住んでいる",
            "仕事は",
            "おすすめ",
            "良い",
            "悪い",
        ]

        for trigger in learning_triggers:
            if trigger in question or trigger in response:
                # Extract a summary
                summary = f"{question[:50]} → {response[:100]}"
                return summary

        return None
