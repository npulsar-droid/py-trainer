#!/usr/bin/env python3
"""runner.py — 採点ハーネス（py_trainer.py からサブプロセスとして起動される）。

標準入力から JSON（ユーザーのコード + チェック一覧）を受け取り、
コードを実行して結果を JSON で標準出力に返す。

py_trainer.py が一時ディレクトリを作業場所（cwd）にして起動するので、
ファイルを作る問題でも、本物のファイルを安全に読み書きできる。

チェックの種類:
    source — ソースコードへの正規表現チェック（"not": true なら「書かれていないこと」）
             コメントは除いてから調べる（初期コードのコメントに反応しないように）
    eq     — 式を評価して期待値と == 比較（"type" があれば型名も確認）
    stdout — print 出力の確認（"expr" なしなら プログラム全体の出力）
"""
from __future__ import annotations

import collections
import io
import itertools
import json
import math
import re
import sys
import tokenize
import traceback
from contextlib import redirect_stdout
from pathlib import Path

USER_FILENAME = "<あなたのコード>"
MAX_STDOUT = 10_000  # 暴走した print で結果が溢れないように

# チェック式の評価時に、ユーザーが import していなくても使える名前
CHECK_EXTRAS = {
    "Path": Path,
    "json": json,
    "math": math,
    "collections": collections,
    "itertools": itertools,
}


def error_summary(exc: BaseException) -> str:
    """ユーザーコード内の行番号つきで、例外を1行にまとめる。"""
    if isinstance(exc, SyntaxError):
        where = f"{exc.lineno}行目: " if exc.lineno else ""
        return f"{where}SyntaxError: {exc.msg}"
    line = None
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == USER_FILENAME:
            line = frame.lineno
    where = f"{line}行目: " if line else ""
    message = f"{type(exc).__name__}: {exc}"
    if isinstance(exc, NameError):
        message += "（名前のタイプミス、または定義し忘れかもしれません）"
    return where + message


def strip_comments(code: str) -> str:
    """書き方チェック用に、コメント（# から行末まで）を取り除いたソースを返す。

    文字列の中の # は残す。構文が壊れていても、読めたところまでは取り除く。
    """
    comments = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            if tok.type == tokenize.COMMENT:
                comments.append(tok)
    except (tokenize.TokenError, SyntaxError):
        pass
    lines = code.splitlines(keepends=True)
    for tok in comments:
        (row, start), (_, end) = tok.start, tok.end
        lines[row - 1] = lines[row - 1][:start] + lines[row - 1][end:]
    return "".join(lines)


def eval_quiet(expr: str, ns: dict) -> tuple:
    """式を評価し、(戻り値, その間の print 出力) を返す。"""
    buf = io.StringIO()
    with redirect_stdout(buf):
        value = eval(expr, ns)
    return value, buf.getvalue()


def passed(name: str) -> dict:
    return {"pass": True, "name": name, "detail": None}


def failed(name: str, detail: str) -> dict:
    return {"pass": False, "name": name, "detail": detail}


def run_check(check: dict, ns: dict, program_stdout: str) -> dict:
    name = check["name"]
    try:
        if check["kind"] == "eq":
            got, _ = eval_quiet(check["expr"], ns)
            want, _ = eval_quiet(check["want"], dict(CHECK_EXTRAS))
            wanted_type = check.get("type")
            if wanted_type and type(got).__name__ != wanted_type:
                return failed(name, f"型が {wanted_type} ではなく {type(got).__name__} になっています")
            if got != want:
                return failed(name, f"期待値 {want!r} / 実際 {got!r}")
            return passed(name)
        if check["kind"] == "stdout":
            if check.get("expr"):
                _, out = eval_quiet(check["expr"], ns)
            else:
                out = program_stdout
            if "want" in check:
                if out.rstrip("\n") != check["want"]:
                    return failed(name, f"期待する出力 {check['want']!r} / 実際 {out.rstrip(chr(10))!r}")
            elif check["contains"] not in out:
                return failed(name, f"出力に {check['contains']!r} が見つかりません（実際の出力: {out!r}）")
            return passed(name)
        return failed(name, f"不明なチェック種別: {check['kind']}")
    except BaseException as exc:  # noqa: BLE001 — 採点は何が起きても結果として返す
        return failed(name, "例外: " + error_summary(exc))


def run(payload: dict) -> dict:
    code = payload["code"]
    checks = payload.get("checks", [])
    results = []

    # 1) 書き方チェック（コードが実行できなくても判定できる）
    source = strip_comments(code)
    for check in checks:
        if check["kind"] != "source":
            continue
        found = re.search(check["pattern"], source, re.MULTILINE) is not None
        ok = (not found) if check.get("not") else found
        results.append(
            passed("[書き方] " + check["name"]) if ok
            else failed("[書き方] " + check["name"], check.get("detail") or "")
        )

    # 2) 問題側の準備（入力ファイルの用意など）。cwd は一時ディレクトリ。
    setup = payload.get("setup")
    if setup:
        exec(setup, {"__name__": "__setup__"})

    # 3) ユーザーコードの実行
    ns = {"__name__": "__main__"}
    buf = io.StringIO()
    try:
        compiled = compile(code, USER_FILENAME, "exec")
        with redirect_stdout(buf):
            exec(compiled, ns)
    except BaseException as exc:  # noqa: BLE001
        return {"error": error_summary(exc), "results": results,
                "stdout": buf.getvalue()[:MAX_STDOUT]}
    program_stdout = buf.getvalue()

    # 4) 値と出力のチェック
    check_ns = {**CHECK_EXTRAS, **ns}
    for check in checks:
        if check["kind"] == "source":
            continue
        results.append(run_check(check, check_ns, program_stdout))
    return {"error": None, "results": results, "stdout": program_stdout[:MAX_STDOUT]}


if __name__ == "__main__":
    # 入出力は環境の既定エンコーディング（Windows なら cp932 など）に頼らず UTF-8 で読み、
    # 結果は ASCII だけの JSON で返す（日本語は \uXXXX になるが、受け側の json.loads で元に戻る）
    payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    sys.stdout.write(json.dumps(run(payload)) + "\n")
