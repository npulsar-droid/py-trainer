#!/usr/bin/env python3
"""py-trainer — 書いて覚えるPython。

書いて → このマシンのPythonで即採点 → 次へ、で基礎を体系立てて固めるドリル。
標準ライブラリのみ使用。進捗は同じフォルダの state.json に保存される。

使い方:
    python3 py_trainer.py               # サーバー起動 → ブラウザで開く
    python3 py_trainer.py --no-browser  # サーバーだけ起動（http://localhost:8346/）
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from chapters import CHAPTERS

BASE_DIR = Path(__file__).resolve().parent
RUNNER_PATH = BASE_DIR / "runner.py"
STATE_PATH = BASE_DIR / "state.json"
TEMPLATE_PATH = BASE_DIR / "template.html"

PORT = 8346
RUN_TIMEOUT_SEC = 5
MAX_CODE_CHARS = 100_000

LESSONS = {lesson["id"]: lesson for ch in CHAPTERS for lesson in ch["lessons"]}


# ---------------------------------------------------------------- 採点

def grade(lesson_id: str, code: str) -> dict:
    """ユーザーのコードを、このマシンのPython（サブプロセス）で実行して採点する。

    作業場所は毎回使い捨ての一時ディレクトリ。ファイルを作る問題でも
    このフォルダや他の場所を汚さない。
    """
    lesson = LESSONS.get(lesson_id)
    if lesson is None:
        return {"error": "不明な問題IDです", "results": [], "stdout": ""}
    payload = json.dumps(
        {"code": code, "checks": lesson["checks"], "setup": lesson.get("setup")},
        ensure_ascii=False,
    )
    with tempfile.TemporaryDirectory(prefix="py-trainer-") as workdir:
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(RUNNER_PATH)],
                input=payload, capture_output=True, text=True, encoding="utf-8",
                cwd=workdir, timeout=RUN_TIMEOUT_SEC,
            )
        except subprocess.TimeoutExpired:
            return {
                "error": f"{RUN_TIMEOUT_SEC}秒以内に終わりませんでした（無限ループになっていませんか？）",
                "results": [], "stdout": "",
            }
    if proc.returncode != 0:
        return {"error": "採点に失敗しました: " + proc.stderr.strip()[-500:],
                "results": [], "stdout": ""}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"error": "採点結果を読み取れませんでした", "results": [], "stdout": ""}


# ---------------------------------------------------------------- 進捗の保存

def empty_state() -> dict:
    return {"__seq": 0, "lessons": {}}


def load_state() -> dict:
    """state.json を読む。無い・読めない・形が壊れているときは空の進捗から始める。"""
    try:
        loaded = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):  # ValueError は JSON・UTF-8 の解読失敗を含む
        return empty_state()
    if not isinstance(loaded, dict):
        return empty_state()
    state = {**empty_state(), **loaded}
    return state if valid_state(state) else empty_state()


def save_state(state: dict) -> None:
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def valid_state(state) -> bool:
    return (
        isinstance(state, dict)
        and isinstance(state.get("__seq"), int)
        and isinstance(state.get("lessons"), dict)
    )


# ---------------------------------------------------------------- ページ生成

CLIENT_LESSON_KEYS = ("id", "title", "desc", "starter", "hint", "solution")


def client_payload() -> dict:
    """ブラウザ側に渡すデータ。チェック定義はサーバー側だけが持つ。"""
    chapters = [
        {
            "title": ch["title"],
            "resources": ch["resources"],
            "lessons": [{k: l[k] for k in CLIENT_LESSON_KEYS} for l in ch["lessons"]],
        }
        for ch in CHAPTERS
    ]
    return {"mode": "server", "chapters": chapters, "state": load_state()}


def render_page() -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    # "</script>" がJSON内に現れてもタグとして解釈されないようエスケープする
    data = json.dumps(client_payload(), ensure_ascii=False).replace("</", "<\\/")
    return template.replace("__PAYLOAD__", data)


# ---------------------------------------------------------------- サーバー

class QuietHandler(BaseHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass  # 静けさが機能。アクセスログは出さない。

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, obj: dict, status: int = 200) -> None:
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json")

    def _read_body(self) -> dict:
        """JSON オブジェクトの本文を読む。形が違うものは空の辞書として扱う。"""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return {}
        if length <= 0:
            return {}
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
        return body if isinstance(body, dict) else {}

    def _from_own_page(self) -> bool:
        """このアプリ自身の画面から送られたリクエストかを確かめる。

        確かめないと、ブラウザで開いている別のサイトが localhost のこのサーバーに
        コードを送りつけて実行させられる（CSRF）。そのため
        - Host が localhost / 127.0.0.1 であること（DNS rebinding 対策）
        - Origin が付いていれば、このサーバー自身であること
        - Content-Type が application/json であること（別サイトからは
          事前確認（preflight）なしには送れない形式）
        をすべて満たすものだけ受け付ける。
        """
        port = self.server.server_address[1]
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if self.headers.get("Host") not in hosts:
            return False
        origin = self.headers.get("Origin")
        if origin is not None and origin not in {f"http://{h}" for h in hosts}:
            return False
        content_type = self.headers.get("Content-Type") or ""
        return content_type.split(";")[0].strip().lower() == "application/json"

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._send(200, render_page().encode("utf-8"), "text/html; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:
        if not self._from_own_page():
            self._send_json({"ok": False, "error": "このサーバーの画面以外からのリクエストは受け付けません"}, 403)
            return
        body = self._read_body()
        if self.path == "/api/run":
            lesson_id, code = body.get("id"), body.get("code")
            if not isinstance(lesson_id, str) or not isinstance(code, str):
                self._send_json({"error": "bad request"}, 400)
                return
            if len(code) > MAX_CODE_CHARS:
                self._send_json({"error": "コードが長すぎます"}, 400)
                return
            self._send_json(grade(lesson_id, code))
        elif self.path == "/api/state":
            if not valid_state(body):
                self._send_json({"ok": False, "error": "bad request"}, 400)
                return
            save_state(body)
            self._send_json({"ok": True})
        else:
            self._send_json({"ok": False, "error": "not found"}, 404)


# ---------------------------------------------------------------- 入口

def warm_up() -> None:
    """起動時に一度だけ空の採点を走らせておく。

    macOSでは久しぶりに起動するプロセスの初回だけ、セキュリティ検証で
    数十秒待たされることがある。それを起動時に済ませておくと、
    最初の1問が誤ってタイムアウト扱いになるのを防げる。
    """
    try:
        subprocess.run(
            [sys.executable, "-I", str(RUNNER_PATH)],
            input='{"code": "", "checks": []}',
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
    except (subprocess.SubprocessError, OSError):
        pass  # 温めに失敗しても、本番の採点で再挑戦すればよい


def run_server(open_browser: bool = True) -> None:
    total = len(LESSONS)
    print("採点エンジンを準備しています…")
    warm_up()
    print(f"Python Trainer — 全{total}問。 http://localhost:{PORT}/ で開きます（Ctrl+Cで終了）")
    server = HTTPServer(("127.0.0.1", PORT), QuietHandler)
    if open_browser:
        threading.Timer(0.6, webbrowser.open, [f"http://localhost:{PORT}/"]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nおつかれさまでした。")


if __name__ == "__main__":
    run_server(open_browser="--no-browser" not in sys.argv)
