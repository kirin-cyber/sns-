import json
import os
from datetime import datetime
from pathlib import Path


class AnalyticsManager:
    HISTORY_FILE = "data/analytics_history.json"

    def __init__(self, threads_client):
        self.client = threads_client
        Path("data").mkdir(exist_ok=True)

    def _load_history(self) -> list:
        if not os.path.exists(self.HISTORY_FILE):
            return []
        with open(self.HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_history(self, data: list):
        with open(self.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def collect_and_save(self, limit: int = 20) -> list:
        """最近の投稿データを収集して履歴に保存"""
        posts = self.client.get_recent_posts(limit=limit)
        snapshot = {
            "collected_at": datetime.now().isoformat(),
            "posts": posts,
        }
        history = self._load_history()
        history.append(snapshot)
        history = history[-20:]  # 最新20スナップショットのみ保持
        self._save_history(history)
        return posts

    def get_engagement_summary(self, posts: list = None) -> dict:
        """エンゲージメント統計を計算"""
        if posts is None:
            posts = self.client.get_recent_posts(limit=20)
        if not posts:
            return {}

        total_likes = sum(p.get("like_count", 0) for p in posts)
        total_replies = sum(p.get("replies_count", 0) for p in posts)
        n = len(posts)
        return {
            "total_posts": n,
            "total_likes": total_likes,
            "total_replies": total_replies,
            "avg_likes": round(total_likes / n, 1),
            "avg_replies": round(total_replies / n, 1),
            "avg_engagement": round((total_likes + total_replies) / n, 1),
        }

    def get_top_posts(self, posts: list = None, n: int = 3) -> list:
        """エンゲージメントスコア上位の投稿を返す（返信は重み2倍）"""
        if posts is None:
            posts = self.client.get_recent_posts(limit=20)
        scored = sorted(
            posts,
            key=lambda p: p.get("like_count", 0) + p.get("replies_count", 0) * 2,
            reverse=True,
        )
        return scored[:n]

    def get_best_posts_hint(self, posts: list = None) -> str:
        """AI生成の改善参考用: パフォーマンス上位投稿のスニペット"""
        top = self.get_top_posts(posts, n=3)
        if not top:
            return ""
        lines = []
        for p in top:
            text = p.get("text", "")[:80]
            likes = p.get("like_count", 0)
            replies = p.get("replies_count", 0)
            lines.append(f"・{text}... (❤{likes} 💬{replies})")
        return "\n".join(lines)

    def print_report(self):
        """分析レポートをコンソールに表示"""
        posts = self.client.get_recent_posts(limit=20)
        summary = self.get_engagement_summary(posts)
        top_posts = self.get_top_posts(posts)

        print("\n===== エンゲージメント分析レポート =====")
        print(f"  対象投稿数    : {summary.get('total_posts', 0)} 件")
        print(f"  合計いいね    : {summary.get('total_likes', 0)}")
        print(f"  合計返信      : {summary.get('total_replies', 0)}")
        print(f"  平均いいね    : {summary.get('avg_likes', 0)}")
        print(f"  平均返信      : {summary.get('avg_replies', 0)}")
        print(f"  平均エンゲージ: {summary.get('avg_engagement', 0)}")

        if top_posts:
            print("\n--- エンゲージメント上位投稿 ---")
            for i, p in enumerate(top_posts, 1):
                ts = p.get("timestamp", "")[:10]
                text = p.get("text", "")[:60]
                likes = p.get("like_count", 0)
                replies = p.get("replies_count", 0)
                print(f"  {i}. [{ts}] {text}...")
                print(f"       ❤ {likes}  💬 {replies}")

        print("=" * 42)
