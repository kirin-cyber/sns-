import hashlib
import hmac
import json
import logging
import os

from flask import Flask, abort, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _verify_signature(payload: bytes, signature: str) -> bool:
    """Meta が送信する X-Hub-Signature-256 を検証する"""
    secret = os.environ.get("WEBHOOK_APP_SECRET", "")
    if not secret:
        return True  # シークレット未設定時はスキップ
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.get("/webhook")
def verify():
    """Meta がコールバックURL の疎通確認に使うエンドポイント"""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    verify_token = os.environ.get("WEBHOOK_VERIFY_TOKEN", "")
    if mode == "subscribe" and token == verify_token:
        logger.info("Webhook verification succeeded")
        return challenge, 200

    logger.warning("Webhook verification failed: mode=%s token=%s", mode, token)
    abort(403)


@app.post("/webhook")
def receive():
    """Meta からのイベント通知を受信する"""
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not _verify_signature(request.data, signature):
        logger.warning("Invalid signature")
        abort(403)

    payload = request.get_json(silent=True) or {}
    object_type = payload.get("object", "")
    entries = payload.get("entry", [])

    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            field = change.get("field", "")
            value = change.get("value", {})
            logger.info("Event: object=%s field=%s value=%s", object_type, field, json.dumps(value, ensure_ascii=False))
            _handle_event(object_type, field, value)

    return jsonify({"status": "ok"}), 200


def _handle_event(object_type: str, field: str, value: dict):
    """受信したイベントを処理する"""
    if object_type == "threads":
        if field == "mentions":
            _on_mention(value)
        elif field == "replies":
            _on_reply(value)
        elif field == "follows":
            _on_follow(value)


def _on_mention(value: dict):
    logger.info("[Mention] %s", value)


def _on_reply(value: dict):
    logger.info("[Reply] %s", value)


def _on_follow(value: dict):
    logger.info("[Follow] %s", value)


def run(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    app.run(host=host, port=port, debug=debug)
