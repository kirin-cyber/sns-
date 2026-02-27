import os
import requests


class ThreadsClient:
    BASE_URL = "https://graph.threads.net/v1.0"

    def __init__(self):
        self.access_token = os.environ["THREADS_ACCESS_TOKEN"]
        self.user_id = os.environ["THREADS_USER_ID"]

    def _get(self, path: str, params: dict = None) -> dict:
        params = params or {}
        params["access_token"] = self.access_token
        response = requests.get(f"{self.BASE_URL}/{path}", params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, data: dict = None) -> dict:
        data = data or {}
        data["access_token"] = self.access_token
        response = requests.post(f"{self.BASE_URL}/{path}", data=data)
        response.raise_for_status()
        return response.json()

    def create_text_post(self, text: str) -> str:
        """テキスト投稿を作成してメディアコンテナIDを返す"""
        result = self._post(f"{self.user_id}/threads", {
            "media_type": "TEXT",
            "text": text,
        })
        return result["id"]

    def publish_post(self, creation_id: str) -> str:
        """作成した投稿を公開してスレッドIDを返す"""
        result = self._post(f"{self.user_id}/threads_publish", {
            "creation_id": creation_id,
        })
        return result["id"]

    def post(self, text: str) -> str:
        """テキストを投稿して公開済みスレッドIDを返す"""
        creation_id = self.create_text_post(text)
        thread_id = self.publish_post(creation_id)
        print(f"[Threads] 投稿完了: thread_id={thread_id}")
        return thread_id

    def get_profile(self) -> dict:
        """プロフィール情報を取得"""
        return self._get(self.user_id, {"fields": "id,username,name,threads_profile_picture_url"})

    def get_recent_posts(self, limit: int = 10) -> list:
        """最近の投稿一覧を取得"""
        result = self._get(f"{self.user_id}/threads", {
            "fields": "id,text,timestamp,like_count,replies_count",
            "limit": limit,
        })
        return result.get("data", [])

    def get_post_insights(self, thread_id: str) -> dict:
        """投稿ごとのインサイト（表示数・いいね・返信・リポスト）を取得"""
        try:
            result = self._get(f"{thread_id}/insights", {
                "metric": "views,likes,replies,reposts,quotes",
            })
            metrics = {}
            for item in result.get("data", []):
                metrics[item["name"]] = item.get("values", [{}])[-1].get("value", 0)
            return metrics
        except Exception:
            return {}

    def get_follower_count(self) -> int:
        """フォロワー数を取得"""
        try:
            result = self._get(self.user_id, {"fields": "followers_count"})
            return result.get("followers_count", 0)
        except Exception:
            return 0
