#!/usr/bin/env python3
"""
Threads API 接続テストスクリプト
使い方: python test_connection.py

テスト内容:
  1. .env の読み込み確認
  2. プロフィール取得 (GET /me)
  3. 最近の投稿一覧取得 (GET /{user_id}/threads)
  4. フォロワー数取得
"""

import sys
from dotenv import load_dotenv

load_dotenv()


def check_env():
    import os
    print("[1] 環境変数チェック")
    token = os.environ.get("THREADS_ACCESS_TOKEN", "")
    user_id = os.environ.get("THREADS_USER_ID", "")

    if not token or token == "your_threads_access_token_here":
        print("  ✗ THREADS_ACCESS_TOKEN が未設定です")
        return False
    if not user_id or user_id == "your_threads_user_id_here":
        print("  ✗ THREADS_USER_ID が未設定です")
        return False

    print(f"  ✓ THREADS_ACCESS_TOKEN: ...{token[-10:]}")
    print(f"  ✓ THREADS_USER_ID: {user_id}")
    return True


def test_profile(client):
    print("\n[2] プロフィール取得テスト")
    try:
        profile = client.get_profile()
        print(f"  ✓ id       : {profile.get('id')}")
        print(f"  ✓ username : @{profile.get('username')}")
        print(f"  ✓ name     : {profile.get('name', '(未設定)')}")
        return True
    except Exception as e:
        print(f"  ✗ 失敗: {e}")
        return False


def test_recent_posts(client):
    print("\n[3] 最近の投稿取得テスト")
    try:
        posts = client.get_recent_posts(limit=3)
        if posts:
            print(f"  ✓ {len(posts)} 件取得")
            for p in posts:
                ts = p.get("timestamp", "")[:10]
                text = (p.get("text") or "")[:40]
                print(f"     [{ts}] {text}...")
        else:
            print("  ✓ 投稿なし（0件）")
        return True
    except Exception as e:
        print(f"  ✗ 失敗: {e}")
        return False


def test_follower_count(client):
    print("\n[4] フォロワー数取得テスト")
    try:
        count = client.get_follower_count()
        print(f"  ✓ フォロワー数: {count} 人")
        return True
    except Exception as e:
        print(f"  ✗ 失敗: {e}")
        return False


def main():
    print("=" * 50)
    print("Threads API 接続テスト")
    print("=" * 50)

    if not check_env():
        sys.exit(1)

    from src.threads_client import ThreadsClient
    client = ThreadsClient()

    results = [
        test_profile(client),
        test_recent_posts(client),
        test_follower_count(client),
    ]

    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 50}")
    print(f"結果: {passed}/{total} テスト通過")
    if passed == total:
        print("✓ すべてのテストが通過しました")
    else:
        print("✗ 一部のテストが失敗しました（ネットワーク接続を確認してください）")
    print("=" * 50)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
