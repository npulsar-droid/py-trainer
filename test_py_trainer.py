"""py-trainer のテスト。

実行: cd py-trainer && python3 -m pytest test_py_trainer.py -q

中心は「全レッスンの解答例が採点を通ること」。カリキュラムを増やしたり
チェックを書き換えたりしたら、これを回せば壊れていないか分かる。

採点ロジックのテストは runner を直接呼ぶ（in-process）。速く、
プロセス起動が遅い環境でも安定する。サブプロセス経由の配線
（py_trainer.grade）は最後に数本だけ確認する。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import runner  # noqa: E402
from chapters import CHAPTERS  # noqa: E402
from py_trainer import LESSONS, grade, valid_state, warm_up  # noqa: E402

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


# ---------------------------------------------------------------- 進捗の形式

def test_valid_state_accepts_normal_state():
    assert valid_state({"__seq": 3, "lessons": {"variables": {"done": True}}})


def test_valid_state_rejects_broken_state():
    assert not valid_state([])
    assert not valid_state({"__seq": "x", "lessons": {}})
    assert not valid_state({"__seq": 0})


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


def test_infinite_loop_times_out(warmed_runner):
    res = grade(ALL[0]["id"], "while True:\n    pass")
    assert res["error"] and "秒" in res["error"]


def test_unknown_lesson_id():
    res = grade("no_such_lesson", "x = 1")
    assert res["error"]
