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

    client = ThreadsClient()

    fixed_text = args.text if hasattr(args, "text") and args.text else None

    if fixed_text:
        text = fixed_text
    else:
        from src.ai_generator import AIContentGenerator
        generator = AIContentGenerator()
        topic = args.topic if hasattr(args, "topic") and args.topic else None
        text = generator.generate_post(topic)

    print("\n--- 投稿文 ---")
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


def cmd_analyze(args):
    from src.threads_client import ThreadsClient
    from src.analytics import AnalyticsManager
    client = ThreadsClient()
    analytics = AnalyticsManager(client)
    analytics.collect_and_save()
    analytics.print_report()

    followers = client.get_follower_count()
    if followers:
        print(f"\n  フォロワー数  : {followers} 人")


def cmd_webhook(args):
    """Webhookサーバーを起動する"""
    from src.webhook_server import run
    port = int(args.port) if hasattr(args, "port") and args.port else 5000
    print(f"[Webhook] サーバーを起動します: http://0.0.0.0:{port}/webhook")
    print("[Webhook] 停止するには Ctrl+C を押してください")
    run(port=port)


def cmd_growth(args):
    """分析 → AI最適化投稿 の成長サイクルを1回実行"""
    from src.threads_client import ThreadsClient
    from src.ai_generator import AIContentGenerator
    from src.analytics import AnalyticsManager

    client = ThreadsClient()
    analytics = AnalyticsManager(client)
    generator = AIContentGenerator()

    print("[Growth] 投稿データを分析中...")
    posts = analytics.collect_and_save()
    analytics.print_report()

    hint = analytics.get_best_posts_hint(posts)
    topic = args.topic if hasattr(args, "topic") and args.topic else None

    print("\n[Growth] 分析結果をもとに投稿文を最適化生成中...")
    text = generator.generate_optimized_post(topic=topic, best_posts_hint=hint)

    print("\n--- 生成された投稿文 ---")
    print(text)
    print(f"--- {len(text)}文字 ---\n")

    confirm = input("この内容で投稿しますか？ [y/N]: ").strip().lower()
    if confirm == "y":
        client.post(text)
        print("[Growth] 投稿しました！フォロワー増加を目指して継続しましょう。")
    else:
        print("キャンセルしました。")


def main():
    parser = argparse.ArgumentParser(description="Threads SNS 自動管理システム")
    subparsers = parser.add_subparsers(dest="command")

    # post
    post_parser = subparsers.add_parser("post", help="今すぐ1回投稿")
    post_parser.add_argument("--topic", help="投稿テーマを指定（AI生成時）")
    post_parser.add_argument("--text", help="固定テキストで投稿（ANTHROPIC_API_KEY不要）")

    # schedule
    subparsers.add_parser("schedule", help="定期投稿モード開始")

    # profile
    subparsers.add_parser("profile", help="プロフィール確認")

    # history
    subparsers.add_parser("history", help="最近の投稿一覧")

    # analyze
    subparsers.add_parser("analyze", help="投稿のエンゲージメント分析レポートを表示")

    # growth
    growth_parser = subparsers.add_parser("growth", help="分析→AI最適化投稿の成長サイクルを実行")
    growth_parser.add_argument("--topic", help="投稿テーマを指定")

    # webhook
    webhook_parser = subparsers.add_parser("webhook", help="Webhookサーバーを起動")
    webhook_parser.add_argument("--port", default=5000, help="ポート番号（デフォルト: 5000）")

    args = parser.parse_args()

    if args.command == "post":
        cmd_post(args)
    elif args.command == "schedule":
        cmd_schedule(args)
    elif args.command == "profile":
        cmd_profile(args)
    elif args.command == "history":
        cmd_history(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "growth":
        cmd_growth(args)
    elif args.command == "webhook":
        cmd_webhook(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
