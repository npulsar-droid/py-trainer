#!/usr/bin/env python3
"""build.py — ブラウザだけで動く単一HTML（index.html）を生成する。

ローカル版（py_trainer.py）はこのマシンのPythonで採点するが、
生成される index.html は Pyodide で採点する。採点ロジック（runner.py）と
問題（chapters/）は両者で共通なので、判定はズレない。

    python3 build.py            # index.html を書き出す
"""
from __future__ import annotations

import json
from pathlib import Path

from chapters import CHAPTERS

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "template.html"
RUNNER_PATH = BASE_DIR / "runner.py"
OUT_PATH = BASE_DIR / "index.html"

# static 版はチェック定義もブラウザに渡す（解答例はもともと渡している）
LESSON_KEYS = ("id", "title", "desc", "starter", "hint", "solution", "checks", "setup")


def payload() -> dict:
    chapters = [
        {
            "title": ch["title"],
            "resources": ch["resources"],
            "lessons": [
                {k: lesson[k] for k in LESSON_KEYS if k in lesson}
                for lesson in ch["lessons"]
            ],
        }
        for ch in CHAPTERS
    ]
    return {
        "mode": "static",
        "chapters": chapters,
        "state": {},                                   # 進捗は localStorage 側で持つ
        "runner": RUNNER_PATH.read_text(encoding="utf-8"),
    }


def main() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    data = json.dumps(payload(), ensure_ascii=False).replace("</", "<\\/")
    OUT_PATH.write_text(template.replace("__PAYLOAD__", data), encoding="utf-8")
    total = sum(len(ch["lessons"]) for ch in CHAPTERS)
    size = OUT_PATH.stat().st_size / 1024
    print(f"{OUT_PATH.name} を書き出しました（全{total}問 / {size:.0f}KB）")


if __name__ == "__main__":
    main()
