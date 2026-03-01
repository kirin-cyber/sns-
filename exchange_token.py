#!/usr/bin/env python3
"""
短期アクセストークン → 長期アクセストークン変換スクリプト
使い方: python exchange_token.py <短期トークン>
または:  python exchange_token.py  （インタラクティブに入力）

事前準備:
  Meta for Developers のユーザートークン生成ツールで短期トークンを取得してください
  https://developers.facebook.com/apps/1420336199883653/use_cases/customize/?use_case_enum=THREADS_API
"""

import json
import sys
import urllib.parse
import urllib.request

APP_ID = "1420336199883653"
APP_SECRET = "f07ffa632fa7933b658e6d5d86840373"


def exchange_for_long_lived_token(short_token: str) -> dict:
    params = urllib.parse.urlencode({
        "grant_type": "th_exchange_token",
        "client_secret": APP_SECRET,
        "access_token": short_token,
    })
    url = f"https://graph.threads.net/access_token?{params}"
    with urllib.request.urlopen(url) as res:
        return json.loads(res.read())


def get_user_info(token: str) -> dict:
    params = urllib.parse.urlencode({"fields": "id,username", "access_token": token})
    url = f"https://graph.threads.net/v1.0/me?{params}"
    with urllib.request.urlopen(url) as res:
        return json.loads(res.read())


def update_env_file(token: str, user_id: str, env_path: str = ".env"):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated = []
        token_updated = False
        user_id_updated = False
        for line in lines:
            if line.startswith("THREADS_ACCESS_TOKEN="):
                updated.append(f"THREADS_ACCESS_TOKEN={token}\n")
                token_updated = True
            elif line.startswith("THREADS_USER_ID="):
                updated.append(f"THREADS_USER_ID={user_id}\n")
                user_id_updated = True
            else:
                updated.append(line)

        if not token_updated:
            updated.append(f"THREADS_ACCESS_TOKEN={token}\n")
        if not user_id_updated:
            updated.append(f"THREADS_USER_ID={user_id}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(updated)
        print(f"\n✅ .env を自動更新しました: {env_path}")
    except FileNotFoundError:
        print(f"\n⚠️  .env が見つかりませんでした。手動でコピーしてください。")


def main():
    if len(sys.argv) > 1:
        short_token = sys.argv[1].strip()
    else:
        print("短期アクセストークンを貼り付けてください（Meta ユーザートークン生成ツールで取得）:")
        short_token = input("> ").strip()

    if not short_token:
        print("エラー: トークンが入力されていません")
        sys.exit(1)

    print("\n長期トークンに変換中（有効期限60日）...")

    try:
        result = exchange_for_long_lived_token(short_token)
    except Exception as e:
        print(f"エラー: トークン変換失敗 → {e}")
        sys.exit(1)

    long_token = result.get("access_token")
    expires_in = result.get("expires_in", "不明")

    print("ユーザー情報を取得中...")
    try:
        user_info = get_user_info(long_token)
        user_id = user_info.get("id", "")
        username = user_info.get("username", "")
    except Exception as e:
        print(f"⚠️  ユーザー情報取得失敗（トークンは有効）: {e}")
        user_id = ""
        username = ""

    print("\n" + "=" * 60)
    print("✅ 長期トークン取得成功！")
    print("=" * 60)
    print(f"THREADS_ACCESS_TOKEN={long_token}")
    print(f"THREADS_USER_ID={user_id}")
    if username:
        print(f"ユーザー名: @{username}")
    print(f"有効期限: 約 {int(expires_in) // 86400} 日" if isinstance(expires_in, int) else f"有効期限: {expires_in}秒")
    print("=" * 60)

    if user_id:
        answer = input("\n.env ファイルを自動更新しますか？ [y/N]: ").strip().lower()
        if answer == "y":
            update_env_file(long_token, user_id)

    print("\n完了。")


if __name__ == "__main__":
    main()
