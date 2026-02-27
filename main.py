#!/usr/bin/env python3
"""
Threads SNS 自動管理システム
Usage:
  python main.py post               # 今すぐ1回投稿
  python main.py post --topic AI    # テーマ指定で投稿
  python main.py schedule           # 定期投稿モード開始
  python main.py profile            # プロフィール確認
  python main.py history            # 最近の投稿一覧
"""

import argparse
import sys
from dotenv import load_dotenv

load_dotenv()


def cmd_post(args):
    from src.threads_client import ThreadsClient
    from src.ai_generator import AIContentGenerator

    generator = AIContentGenerator()
    client = ThreadsClient()

    topic = args.topic if hasattr(args, "topic") and args.topic else None
    text = generator.generate_post(topic)

    print("\n--- 生成された投稿文 ---")
    print(text)
    print(f"--- {len(text)}文字 ---\n")

    confirm = input("この内容で投稿しますか？ [y/N]: ").strip().lower()
    if confirm == "y":
        client.post(text)
        print("投稿しました！")
    else:
        print("キャンセルしました。")


def cmd_schedule(args):
    from src.scheduler import PostScheduler
    scheduler = PostScheduler()
    scheduler.start()


def cmd_profile(args):
    from src.threads_client import ThreadsClient
    client = ThreadsClient()
    profile = client.get_profile()
    print("\n--- プロフィール ---")
    for k, v in profile.items():
        print(f"  {k}: {v}")


def cmd_history(args):
    from src.threads_client import ThreadsClient
    client = ThreadsClient()
    posts = client.get_recent_posts(limit=5)
    print("\n--- 最近の投稿 ---")
    for post in posts:
        ts = post.get("timestamp", "")[:10]
        text = post.get("text", "")[:60]
        likes = post.get("like_count", 0)
        replies = post.get("replies_count", 0)
        print(f"  [{ts}] {text}... | ❤ {likes}  💬 {replies}")


def main():
    parser = argparse.ArgumentParser(description="Threads SNS 自動管理システム")
    subparsers = parser.add_subparsers(dest="command")

    # post
    post_parser = subparsers.add_parser("post", help="今すぐ1回投稿")
    post_parser.add_argument("--topic", help="投稿テーマを指定")

    # schedule
    subparsers.add_parser("schedule", help="定期投稿モード開始")

    # profile
    subparsers.add_parser("profile", help="プロフィール確認")

    # history
    subparsers.add_parser("history", help="最近の投稿一覧")

    args = parser.parse_args()

    if args.command == "post":
        cmd_post(args)
    elif args.command == "schedule":
        cmd_schedule(args)
    elif args.command == "profile":
        cmd_profile(args)
    elif args.command == "history":
        cmd_history(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
