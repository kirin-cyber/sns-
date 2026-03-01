#!/usr/bin/env python3
"""
Threads APIアクセストークン取得スクリプト
使い方: python get_threads_token.py
"""

import json
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

APP_ID = "1420336199883653"
APP_SECRET = "f07ffa632fa7933b658e6d5d86840373"
REDIRECT_URI = "http://localhost:8080/"
SCOPE = "threads_basic,threads_content_publish"

auth_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2>認証成功！このタブを閉じてターミナルに戻ってください。</h2>".encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: no code")

    def log_message(self, *args):
        pass


def get_short_lived_token(code):
    url = "https://graph.threads.net/oauth/access_token"
    data = urllib.parse.urlencode({
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())


def get_long_lived_token(short_token):
    params = urllib.parse.urlencode({
        "grant_type": "th_exchange_token",
        "client_secret": APP_SECRET,
        "access_token": short_token,
    })
    url = f"https://graph.threads.net/access_token?{params}"
    with urllib.request.urlopen(url) as res:
        return json.loads(res.read())


def get_user_id(token):
    params = urllib.parse.urlencode({"fields": "id,username", "access_token": token})
    url = f"https://graph.threads.net/v1.0/me?{params}"
    with urllib.request.urlopen(url) as res:
        return json.loads(res.read())


def main():
    auth_url = (
        f"https://threads.net/oauth/authorize"
        f"?client_id={APP_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope={SCOPE}"
        f"&response_type=code"
    )

    print("=" * 60)
    print("Threads APIトークン取得")
    print("=" * 60)
    print("\n以下のURLをブラウザで開いて認証してください:\n")
    print(auth_url)
    print("\n認証後、自動でトークンを取得します...")
    print("（ローカルサーバーをポート8080で起動中）\n")

    server = HTTPServer(("localhost", 8080), CallbackHandler)
    server.handle_request()

    if not auth_code:
        print("エラー: 認証コードを取得できませんでした")
        return

    print("認証コード取得成功。トークンを取得中...")

    try:
        short = get_short_lived_token(auth_code)
        short_token = short["access_token"]
        user_id = short.get("user_id", "")

        print("長期トークンに交換中（有効期限60日）...")
        long = get_long_lived_token(short_token)
        long_token = long["access_token"]

        if not user_id:
            info = get_user_id(long_token)
            user_id = info.get("id", "")

        print("\n" + "=" * 60)
        print("✅ 取得成功！以下を .env に貼り付けてください:")
        print("=" * 60)
        print(f"THREADS_ACCESS_TOKEN={long_token}")
        print(f"THREADS_USER_ID={user_id}")
        print("=" * 60)

    except Exception as e:
        print(f"エラー: {e}")


if __name__ == "__main__":
    main()
