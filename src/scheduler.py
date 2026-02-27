import os
import time
import schedule
from datetime import datetime

from src.threads_client import ThreadsClient
from src.ai_generator import AIContentGenerator


class PostScheduler:
    def __init__(self):
        self.threads = ThreadsClient()
        self.generator = AIContentGenerator()
        self.interval_hours = int(os.environ.get("POST_INTERVAL_HOURS", "6"))

    def _run_post(self, topic: str = None):
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 投稿処理開始")
            text = self.generator.generate_post(topic)
            self.threads.post(text)
        except Exception as e:
            print(f"[ERROR] 投稿失敗: {e}")

    def post_once(self, topic: str = None):
        """今すぐ1回投稿"""
        self._run_post(topic)

    def start(self):
        """定期投稿を開始（{interval_hours}時間ごと）"""
        print(f"[Scheduler] {self.interval_hours}時間ごとに自動投稿を開始します")
        self._run_post()  # 起動直後に1回実行

        schedule.every(self.interval_hours).hours.do(self._run_post)

        while True:
            schedule.run_pending()
            time.sleep(60)
