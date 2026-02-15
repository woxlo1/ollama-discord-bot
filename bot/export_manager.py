"""Export conversation and memory data."""

import json
from datetime import datetime
from typing import Dict, List


class ExportManager:
    """Manage data export functionality."""

    @staticmethod
    def export_conversation_markdown(
        user_name: str, conversation: List[Dict], title: str = "会話履歴"
    ) -> str:
        """Export conversation history as Markdown."""
        lines = [
            f"# {title}",
            "",
            f"**ユーザー:** {user_name}",
            f"**日時:** {datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            "",
            "---",
            "",
        ]

        for i, msg in enumerate(conversation, 1):
            role = "🤖 Bot" if msg["role"] == "assistant" else "👤 あなた"
            timestamp = msg.get("timestamp", "")
            content = msg.get("content", "")

            lines.append(f"## {i}. {role}")
            if timestamp:
                lines.append(f"*{timestamp}*")
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def export_memory_json(learned_facts: List[Dict]) -> str:
        """Export learned facts as JSON."""
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_facts": len(learned_facts),
            "facts": learned_facts,
        }
        return json.dumps(export_data, ensure_ascii=False, indent=2)

    @staticmethod
    def export_stats(stats_data: Dict) -> str:
        """Export statistics as formatted text."""
        lines = [
            "# 📊 Bot統計情報",
            "",
            f"**生成日時:** {datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            "",
            "## 基本統計",
        ]

        for key, value in stats_data.items():
            lines.append(f"- **{key}:** {value}")

        return "\n".join(lines)
