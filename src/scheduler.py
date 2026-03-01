import os
import time
import schedule
from datetime import datetime

from src.threads_client import ThreadsClient
from src.ai_generator import AIContentGenerator
from src.discord_notifier import DiscordNotifier


class PostScheduler:
    def __init__(self):
        self.threads = ThreadsClient()
        self.generator = AIContentGenerator()
        self.notifier = DiscordNotifier()
        self.interval_hours = int(os.environ.get("POST_INTERVAL_HOURS", "6"))

    def _run_post(self, topic: str = None):
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 投稿処理開始")
            text = self.generator.generate_post(topic)
            thread_id = self.threads.post(text)
            self.notifier.post_success(text, thread_id)
        except Exception as e:
            print(f"[ERROR] 投稿失敗: {e}")
            self.notifier.post_failed(str(e))

    def post_once(self, topic: str = None):
        """今すぐ1回投稿"""
        self._run_post(topic)

    def start(self):
        """定期投稿を開始（{interval_hours}時間ごと）"""
        print(f"[Scheduler] {self.interval_hours}時間ごとに自動投稿を開始します")
        self.notifier.scheduler_started(self.interval_hours)
        self._run_post()  # 起動直後に1回実行

        schedule.every(self.interval_hours).hours.do(self._run_post)

        while True:
            schedule.run_pending()
            time.sleep(60)
