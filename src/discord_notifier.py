import logging
import os

import requests

logger = logging.getLogger(__name__)


class DiscordNotifier:
    def __init__(self):
        self.webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")

    def _send(self, content: str):
        if not self.webhook_url:
            return
        try:
            requests.post(self.webhook_url, json={"content": content}, timeout=10)
        except Exception as e:
            logger.warning("Discord通知失敗: %s", e)

    def post_success(self, text: str, thread_id: str):
        preview = text[:80] + ("..." if len(text) > 80 else "")
        self._send(
            f"✅ **投稿完了**\n"
            f"> {preview}\n"
            f"Thread ID: `{thread_id}`"
        )

    def post_failed(self, error: str):
        self._send(f"❌ **投稿失敗**\nエラー: `{error}`")

    def scheduler_started(self, interval_hours: int):
        self._send(f"🚀 **スケジューラー起動**\n{interval_hours}時間ごとに自動投稿します")

    def on_mention(self, value: dict):
        user = value.get("from", {}).get("name", "不明")
        text = value.get("text", "")[:80]
        self._send(f"📣 **メンションされました**\nFrom: {user}\n> {text}")

    def on_reply(self, value: dict):
        user = value.get("from", {}).get("name", "不明")
        text = value.get("text", "")[:80]
        self._send(f"💬 **返信がきました**\nFrom: {user}\n> {text}")

    def on_follow(self, value: dict):
        user = value.get("name", "不明")
        self._send(f"👤 **新しいフォロワー**\n{user} さんにフォローされました")
