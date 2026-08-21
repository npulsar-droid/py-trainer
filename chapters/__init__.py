"""カリキュラム全体。各章は chapters/chN.py に1章ずつ。

レッスンの形式:
    id       — 一意なID（進捗保存のキー）
    title    — サイドバーに出る短い名前
    desc     — 問題文（HTML）
    starter  — エディタの初期コード
    hint     — ヒントボタンで出る1〜2行
    solution — 解答例
    checks   — 採点チェック（runner.py が解釈する）
    setup    — 任意。採点前に一時ディレクトリで実行する準備コード
"""
from . import ch1, ch2, ch3, ch4, ch5

CHAPTERS = [ch1.CHAPTER, ch2.CHAPTER, ch3.CHAPTER, ch4.CHAPTER, ch5.CHAPTER]
