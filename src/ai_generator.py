import os
import random
import anthropic


class AIContentGenerator:
    MAX_THREADS_LENGTH = 500

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.language = os.environ.get("POST_LANGUAGE", "ja")
        topics_raw = os.environ.get("POST_TOPIC", "テクノロジー,AI,日常")
        self.topics = [t.strip() for t in topics_raw.split(",")]

    def _pick_topic(self) -> str:
        return random.choice(self.topics)

    def generate_post(self, topic: str = None) -> str:
        """指定テーマ（省略時はランダム）でThreads投稿文を生成"""
        topic = topic or self._pick_topic()

        if self.language == "ja":
            lang_instruction = "日本語で"
            style_hint = "読者が思わず「いいね」したくなるような、自然な口語体で書いてください。"
        else:
            lang_instruction = f"in {self.language}"
            style_hint = "Write in a natural, conversational tone that encourages engagement."

        prompt = (
            f"Threadsに投稿する文章を{lang_instruction}1件だけ生成してください。\n"
            f"テーマ: {topic}\n"
            f"文字数: {self.MAX_THREADS_LENGTH}文字以内\n"
            f"条件:\n"
            f"- 挨拶文や前置きは不要\n"
            f"- ハッシュタグは2〜4個\n"
            f"- {style_hint}\n"
            f"- 投稿文のみを出力し、余分な説明は一切不要"
        )

        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )

        text = message.content[0].text.strip()
        print(f"[AI] テーマ「{topic}」で生成 ({len(text)}文字)")
        return text

    def generate_reply(self, original_text: str) -> str:
        """既存の投稿に対する返信文を生成"""
        prompt = (
            f"以下のThreads投稿への返信を日本語で1件生成してください。\n"
            f"元投稿:\n{original_text}\n\n"
            f"条件:\n"
            f"- 100文字以内\n"
            f"- 親しみやすく共感できる内容\n"
            f"- 返信文のみ出力"
        )

        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text.strip()
