# Threads SNS 自動管理システム

Claude AI を使って Threads への投稿を自動化するツールです。

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して以下を設定：

| 変数名 | 説明 |
|---|---|
| `THREADS_ACCESS_TOKEN` | Threads APIのアクセストークン |
| `THREADS_USER_ID` | ThreadsのユーザーID |
| `ANTHROPIC_API_KEY` | Anthropic APIキー |
| `POST_TOPIC` | 投稿テーマ（カンマ区切りで複数指定可） |
| `POST_INTERVAL_HOURS` | 定期投稿の間隔（時間） |
| `POST_LANGUAGE` | 投稿言語（`ja` または `en`） |

### 3. APIキーの取得方法

**Threads API:**
1. https://developers.facebook.com にアクセス
2. アプリを作成 → Threads API を追加
3. アクセストークンとユーザーIDを取得

**Anthropic API:**
1. https://console.anthropic.com にアクセス
2. API Keys → Create Key

## 使い方

```bash
# 今すぐ1回投稿（確認あり）
python main.py post

# テーマを指定して投稿
python main.py post --topic AI

# 定期投稿モード（バックグラウンド実行推奨）
python main.py schedule

# プロフィール確認
python main.py profile

# 最近の投稿一覧
python main.py history
```

## 定期実行（cron設定例）

6時間ごとに自動投稿する場合：

```cron
0 */6 * * * cd /path/to/sns- && python main.py post --topic "" >> logs/post.log 2>&1
```
