"""py-trainer のテスト。

実行: cd py-trainer && python3 -m pytest test_py_trainer.py -q

中心は「全レッスンの解答例が採点を通ること」。カリキュラムを増やしたり
チェックを書き換えたりしたら、これを回せば壊れていないか分かる。

採点ロジックのテストは runner を直接呼ぶ（in-process）。速く、
プロセス起動が遅い環境でも安定する。サブプロセス経由の配線
（py_trainer.grade）は最後に数本だけ確認する。
"""
from __future__ import annotations

import http.client
import json
import sys
import threading
from http.server import HTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import runner  # noqa: E402
from chapters import CHAPTERS  # noqa: E402
import py_trainer  # noqa: E402
from py_trainer import LESSONS, QuietHandler, grade, load_state, valid_state, warm_up  # noqa: E402

ALL = [lesson for ch in CHAPTERS for lesson in ch["lessons"]]
REQUIRED_KEYS = ("id", "title", "desc", "starter", "hint", "solution", "checks")


def run_lesson(lesson: dict, code: str, tmp_path, monkeypatch) -> dict:
    """runner をサブプロセスなしで直接呼ぶ。cwd は使い捨てディレクトリ。"""
    monkeypatch.chdir(tmp_path)
    return runner.run(
        {"code": code, "checks": lesson["checks"], "setup": lesson.get("setup")}
    )


# ---------------------------------------------------------------- カリキュラムの整合性

def test_lesson_ids_are_unique():
    ids = [l["id"] for l in ALL]
    assert len(ids) == len(set(ids))
    assert len(LESSONS) == len(ALL)


@pytest.mark.parametrize("lesson", ALL, ids=lambda l: l["id"])
def test_lesson_has_required_fields(lesson):
    for key in REQUIRED_KEYS:
        assert lesson.get(key), f"{lesson.get('id')} に {key} がありません"
    assert lesson["checks"], "チェックが空です"


# ---------------------------------------------------------------- 採点（in-process）

@pytest.mark.parametrize("lesson", ALL, ids=lambda l: l["id"])
def test_solution_passes(lesson, tmp_path, monkeypatch):
    """解答例は、全チェックを通らなければならない。"""
    res = run_lesson(lesson, lesson["solution"], tmp_path, monkeypatch)
    assert res["error"] is None, f"実行エラー: {res['error']}"
    failed = [r for r in res["results"] if not r["pass"]]
    assert not failed, f"落ちたチェック: {failed}"


@pytest.mark.parametrize("lesson", ALL, ids=lambda l: l["id"])
def test_starter_does_not_pass(lesson, tmp_path, monkeypatch):
    """初期コードのままでは合格にならない（問題として成立している）。"""
    res = run_lesson(lesson, lesson["starter"], tmp_path, monkeypatch)
    all_pass = res["error"] is None and res["results"] and all(r["pass"] for r in res["results"])
    assert not all_pass, "初期コードのままで合格してしまいます"


def test_syntax_error_is_reported(tmp_path, monkeypatch):
    res = run_lesson(ALL[0], "def broken(:", tmp_path, monkeypatch)
    assert res["error"] and "SyntaxError" in res["error"]


def test_runtime_error_has_line_number(tmp_path, monkeypatch):
    res = run_lesson(ALL[0], "x = 1\ny = x / 0", tmp_path, monkeypatch)
    assert res["error"] and "2行目" in res["error"] and "ZeroDivisionError" in res["error"]


def test_name_error_gets_friendly_note(tmp_path, monkeypatch):
    res = run_lesson(ALL[0], "x = undefined_name", tmp_path, monkeypatch)
    assert res["error"] and "NameError" in res["error"] and "タイプミス" in res["error"]


def test_print_output_is_captured(tmp_path, monkeypatch):
    res = run_lesson(ALL[0], "print('こんにちは')", tmp_path, monkeypatch)
    assert "こんにちは" in res["stdout"]


# ---------------------------------------------------------------- 書き方チェックとコメント

def test_source_check_ignores_comments_in_starter(tmp_path, monkeypatch):
    """初期コードのコメント（「sum() は使わない」）を残したまま正解しても落とさない。"""
    lesson = LESSONS["for_while"]
    code = lesson["starter"].replace("    pass\n", "    total = 0\n    for d in durations:\n        total += d\n    return total\n", 1)
    code = code.replace("    pass\n", "    result = []\n    while n > 0:\n        result.append(n)\n        n -= 1\n    return result\n", 1)
    res = run_lesson(lesson, code, tmp_path, monkeypatch)
    assert res["error"] is None
    assert all(r["pass"] for r in res["results"]), res["results"]


def test_source_check_is_not_satisfied_by_comment(tmp_path, monkeypatch):
    """コメントに frozen=True と書いてあるだけでは「frozen=True にしている」にならない。"""
    lesson = LESSONS["dataclass"]
    code = lesson["starter"].replace("\n\n\n# 関数", "\n@dataclass\nclass Point:\n    x: int\n    y: int\n\n\n# 関数")
    code += "def move(p, dx, dy):\n    return Point(p.x + dx, p.y + dy)\n"
    res = run_lesson(lesson, code, tmp_path, monkeypatch)
    frozen = [r for r in res["results"] if "frozen" in r["name"]]
    assert frozen and not frozen[0]["pass"]


def test_strip_comments_keeps_hash_in_strings():
    assert runner.strip_comments('x = "a#b"  # note\n') == 'x = "a#b"  \n'


def test_strip_comments_survives_broken_code():
    assert "sum(" not in runner.strip_comments("def f(:\n    # sum(\n")


# ---------------------------------------------------------------- 進捗の形式

def test_valid_state_accepts_normal_state():
    assert valid_state({"__seq": 3, "lessons": {"variables": {"done": True}}})


def test_valid_state_rejects_broken_state():
    assert not valid_state([])
    assert not valid_state({"__seq": "x", "lessons": {}})
    assert not valid_state({"__seq": 0})


@pytest.mark.parametrize("content", ["[1]", "{\"__seq\": \"x\"}", "{", "null"])
def test_broken_state_file_starts_fresh(content, tmp_path, monkeypatch):
    """state.json が壊れていても、ページを出せる（空の進捗から始める）。"""
    path = tmp_path / "state.json"
    path.write_text(content, encoding="utf-8")
    monkeypatch.setattr(py_trainer, "STATE_PATH", path)
    assert load_state() == {"__seq": 0, "lessons": {}}
    assert "__PAYLOAD__" not in py_trainer.render_page()


# ---------------------------------------------------------------- HTTP サーバー

@pytest.fixture
def server(tmp_path, monkeypatch):
    monkeypatch.setattr(py_trainer, "STATE_PATH", tmp_path / "state.json")
    srv = HTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield srv.server_address[1]
    srv.shutdown()
    srv.server_close()


def post(port, path, body, headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    hdrs = {"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{port}"}
    hdrs.update(headers or {})
    conn.request("POST", path, body=body, headers=hdrs)
    res = conn.getresponse()
    return res.status, json.loads(res.read())


def test_server_saves_state_from_own_page(server):
    status, body = post(server, "/api/state", json.dumps({"__seq": 1, "lessons": {}}))
    assert status == 200 and body["ok"]


@pytest.mark.parametrize("headers", [
    {"Content-Type": "text/plain"},              # 別サイトが preflight なしで送れる形式
    {"Origin": "https://evil.example"},          # 別サイトの画面から
    {"Host": "evil.example:8346"},               # DNS rebinding
], ids=["text-plain", "foreign-origin", "foreign-host"])
def test_server_rejects_requests_from_other_sites(server, headers):
    payload = json.dumps({"id": ALL[0]["id"], "code": "x = 1"})
    status, _ = post(server, "/api/run", payload, headers)
    assert status == 403


@pytest.mark.parametrize("raw", ["[]", "\"x\"", "1", "{"])
def test_server_answers_400_for_non_object_body(server, raw):
    status, _ = post(server, "/api/run", raw)
    assert status == 400


# ---------------------------------------------------------------- 配線（サブプロセス経由）

@pytest.fixture(scope="session")
def warmed_runner():
    """macOSは久しぶりのプロセス起動だけ数十秒待たされることがあるので、先に温める。"""
    warm_up()


def test_grade_subprocess_roundtrip(warmed_runner):
    """ブラウザから来るのと同じ経路（サブプロセス採点）が通ること。"""
    lesson = ALL[0]
    res = grade(lesson["id"], lesson["solution"])
    # 環境依存のプロセス起動遅延によるタイムアウトだけは、一度やり直す
    if res["error"] and "秒以内" in res["error"]:
        res = grade(lesson["id"], lesson["solution"])
    assert res["error"] is None, f"実行エラー: {res['error']}"
    assert res["results"] and all(r["pass"] for r in res["results"])


def test_grade_subprocess_handles_japanese(warmed_runner):
    """日本語を含むコードと出力が、サブプロセスとの受け渡しで化けない。"""
    res = grade(ALL[0]["id"], '# コメント\nprint("こんにちは")')
    if res["error"] and "秒以内" in res["error"]:
        res = grade(ALL[0]["id"], '# コメント\nprint("こんにちは")')
    assert res["error"] is None and res["stdout"] == "こんにちは\n"


def test_infinite_loop_times_out(warmed_runner):
    res = grade(ALL[0]["id"], "while True:\n    pass")
    assert res["error"] and "秒" in res["error"]


def test_unknown_lesson_id():
    res = grade("no_such_lesson", "x = 1")
    assert res["error"]
