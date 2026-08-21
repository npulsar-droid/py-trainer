"""第5章 実践 — collections / itertools / pathlib / json / 卒業課題"""

CHAPTER = {
    "title": "第5章 実践",
    "resources": [
        {"label": "公式チュートリアル: 標準ライブラリめぐり", "url": "https://docs.python.org/ja/3/tutorial/stdlib.html"},
        {"label": "公式ドキュメント: collections", "url": "https://docs.python.org/ja/3/library/collections.html"},
        {"label": "公式ドキュメント: pathlib", "url": "https://docs.python.org/ja/3/library/pathlib.html"},
        {"label": "Automate the Boring Stuff（実践集）", "url": "https://automatetheboringstuff.com/"},
    ],
    "lessons": [
        {
            "id": "collections_tools",
            "title": "collections",
            "desc": '''<h2>5-1. collections — 集計の道具箱</h2>
<p>3-4で手書きした「出現回数の集計」、実は標準ライブラリに専用の道具があります。</p>
<pre>from collections import Counter, defaultdict

Counter(["a", "b", "a"])              # Counter({'a': 2, 'b': 1})
Counter(words).most_common(1)         # [('a', 2)] — 最多の1件（(値, 回数) のタプル）

d = defaultdict(list)                 # ないキーに触ると自動で [] ができる辞書
d["k"].append("kick")                 # いきなり append できる</pre>
<p class="task"><b>課題:</b> <code>most_common_genre(genres)</code> は Counter で最頻ジャンル名を1つ返す。<code>group_by_initial(words)</code> は defaultdict(list) で頭文字ごとにまとめた辞書を返す（例: <code>{"k": ["kick", "key"], "s": ["snare"]}</code>。最後に <code>dict(d)</code> で普通の辞書に戻す）。</p>''',
            "starter": '''from collections import Counter, defaultdict


def most_common_genre(genres):
    # Counter(...).most_common(1) の [0][0] がジャンル名
    pass


def group_by_initial(words):
    # d = defaultdict(list) に d[w[0]].append(w) して dict(d) を返す
    pass
''',
            "hint": "return Counter(genres).most_common(1)[0][0]。group は for w in words: d[w[0]].append(w) してから return dict(d)。",
            "solution": '''from collections import Counter, defaultdict


def most_common_genre(genres):
    return Counter(genres).most_common(1)[0][0]


def group_by_initial(words):
    d = defaultdict(list)
    for w in words:
        d[w[0]].append(w)
    return dict(d)''',
            "checks": [
                {"kind": "source", "name": "Counter を使っている", "pattern": "\\bCounter\\b", "detail": "from collections import Counter して使います"},
                {"kind": "source", "name": "defaultdict を使っている", "pattern": "\\bdefaultdict\\b", "detail": "defaultdict(list) を使います"},
                {"kind": "eq", "name": 'most_common_genre(["techno", "house", "techno"])', "expr": "most_common_genre(['techno', 'house', 'techno'])", "want": "'techno'"},
                {"kind": "eq", "name": 'group_by_initial(["kick", "key", "snare"])', "expr": "group_by_initial(['kick', 'key', 'snare'])", "want": "{'k': ['kick', 'key'], 's': ['snare']}"},
            ],
        },
        {
            "id": "itertools_tools",
            "title": "itertools",
            "desc": '''<h2>5-2. itertools — 繰り返しの道具箱</h2>
<p>ループの定番パターンを部品化したのが itertools です。今回は2つ:</p>
<pre>from itertools import chain, islice

list(chain.from_iterable([[1, 2], [3]]))   # [1, 2, 3] — 入れ子を平らに
list(islice(range(100), 3))                # [0, 1, 2] — 先頭からn個だけ</pre>
<p><code>islice</code> はリスト以外（<code>range</code> やジェネレータなど「順に出てくるもの」全般）から先頭を取り出せるのがスライスとの違いです。</p>
<p class="task"><b>課題:</b> <code>flatten(lists)</code> は chain.from_iterable で入れ子リストを平らに、<code>first_n(iterable, n)</code> は islice で先頭n個のリストを返してください。</p>''',
            "starter": '''from itertools import chain, islice


def flatten(lists):
    # list(chain.from_iterable(lists))
    pass


def first_n(iterable, n):
    # list(islice(iterable, n))
    pass
''',
            "hint": "コメントの式をそのまま return するだけです。list() で包むのを忘れずに。",
            "solution": '''from itertools import chain, islice


def flatten(lists):
    return list(chain.from_iterable(lists))


def first_n(iterable, n):
    return list(islice(iterable, n))''',
            "checks": [
                {"kind": "source", "name": "chain を使っている", "pattern": "\\bchain\\b", "detail": "chain.from_iterable(lists) を使います"},
                {"kind": "source", "name": "islice を使っている", "pattern": "\\bislice\\b", "detail": "islice(iterable, n) を使います"},
                {"kind": "eq", "name": "flatten([[1, 2], [3], [4, 5]])", "expr": "flatten([[1, 2], [3], [4, 5]])", "want": "[1, 2, 3, 4, 5]"},
                {"kind": "eq", "name": "flatten([])", "expr": "flatten([])", "want": "[]"},
                {"kind": "eq", "name": "first_n(range(100), 3)", "expr": "first_n(range(100), 3)", "want": "[0, 1, 2]"},
                {"kind": "eq", "name": "ジェネレータからも取れる", "expr": "first_n((n * n for n in range(10)), 4)", "want": "[0, 1, 4, 9]"},
            ],
        },
        {
            "id": "pathlib_tools",
            "title": "pathlib",
            "desc": '''<h2>5-3. pathlib — ファイルとフォルダをオブジェクトで</h2>
<p>パスの文字列連結や存在確認を、<code>Path</code> オブジェクトのメソッドですっきり書けます。</p>
<pre>from pathlib import Path

p = Path("samples") / "kick.wav"    # / でパスを連結！
p.name                               # "kick.wav"
p.suffix                             # ".wav"
Path(".").glob("*.wav")              # パターンに合うファイルを列挙</pre>
<p><code>read_text()</code> / <code>write_text()</code> を使うと、1行ファイルの読み書きなら open すら不要です。</p>
<p class="task"><b>課題:</b> 関数 <code>list_wavs(folder)</code> を作ってください。フォルダ内の <code>.wav</code> ファイル名（<code>p.name</code>）を<b>アルファベット順（sorted）</b>のリストで返します。採点時は wav 3つ + それ以外のファイルが置かれた一時フォルダで実行されます。</p>''',
            "starter": '''from pathlib import Path


def list_wavs(folder):
    # Path(folder).glob("*.wav") から p.name を集めて sorted で返す
    pass
''',
            "hint": 'return sorted(p.name for p in Path(folder).glob("*.wav")) の1行です。',
            "solution": '''from pathlib import Path


def list_wavs(folder):
    return sorted(p.name for p in Path(folder).glob("*.wav"))''',
            "setup": '''from pathlib import Path
for name in ["kick.wav", "snare.wav", "bass.wav", "memo.txt", "cover.png"]:
    Path(name).write_text("", encoding="utf-8")
''',
            "checks": [
                {"kind": "source", "name": "Path を使っている", "pattern": "\\bPath\\b", "detail": "from pathlib import Path して使います"},
                {"kind": "source", "name": "glob を使っている", "pattern": "\\.glob\\s*\\(", "detail": 'Path(folder).glob("*.wav") で列挙します'},
                {"kind": "eq", "name": 'list_wavs(".") が wav だけをアルファベット順で', "expr": "list_wavs('.')", "want": "['bass.wav', 'kick.wav', 'snare.wav']"},
            ],
        },
        {
            "id": "json_tools",
            "title": "json",
            "desc": '''<h2>5-4. json — データの保存と交換</h2>
<p>JSONはPythonの辞書・リストとほぼ1対1で行き来できます。</p>
<pre>import json

data = json.loads(text)                      # JSON文字列 → Pythonのデータ
text = json.dumps(data, ensure_ascii=False)  # Pythonのデータ → JSON文字列</pre>
<p><code>ensure_ascii=False</code> を付けないと日本語が <code>\\u591c</code> のような表記になります。日本語を扱うなら必須と覚えてOK。ファイルから読むなら <code>Path(path).read_text()</code> と組み合わせるのが手軽です。</p>
<p class="task"><b>課題:</b> <code>load_tracks(path)</code> はJSONファイルを読んでデータを返す。<code>to_json(data)</code> は <code>ensure_ascii=False</code> でJSON文字列にして返す。採点時は <code>tracks.json</code> が用意されています。</p>''',
            "starter": '''import json
from pathlib import Path


def load_tracks(path):
    # ファイルを読んで json.loads する
    pass


def to_json(data):
    # json.dumps(..., ensure_ascii=False)
    pass
''',
            "hint": "return json.loads(Path(path).read_text(encoding='utf-8')) と return json.dumps(data, ensure_ascii=False) です。",
            "solution": '''import json
from pathlib import Path


def load_tracks(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def to_json(data):
    return json.dumps(data, ensure_ascii=False)''',
            "setup": '''import json
from pathlib import Path
tracks = [{"title": "Voyage", "plays": 120}, {"title": "Aurora", "plays": 45}]
Path("tracks.json").write_text(json.dumps(tracks, ensure_ascii=False), encoding="utf-8")
''',
            "checks": [
                {"kind": "source", "name": "json.load(s) を使っている", "pattern": "json\\.loads?\\s*\\(", "detail": "json.loads(文字列) または json.load(ファイル) を使います"},
                {"kind": "source", "name": "ensure_ascii=False を付けている", "pattern": "ensure_ascii\\s*=\\s*False", "detail": "日本語のために json.dumps(data, ensure_ascii=False) とします"},
                {"kind": "eq", "name": 'load_tracks("tracks.json")', "expr": "load_tracks('tracks.json')", "want": "[{'title': 'Voyage', 'plays': 120}, {'title': 'Aurora', 'plays': 45}]"},
                {"kind": "eq", "name": "to_json で日本語がそのまま出る", "expr": "to_json({'title': '夜間飛行'})", "want": "'{\\\"title\\\": \\\"夜間飛行\\\"}'"},
            ],
        },
        {
            "id": "capstone",
            "title": "卒業課題",
            "desc": '''<h2>5-5. 卒業課題 — 小さな実用スクリプト</h2>
<p>総仕上げです。<b>JSONを読む → 集計する → レポートをファイルに書く</b>。ここまでの道具（json・Counter・sorted・f-string・with / write_text）を全部つなげます。</p>
<p class="task"><b>課題:</b> 関数 <code>make_report(src, dest)</code> を作ってください。</p>
<p><code>src</code> は <code>[{"title": …, "genre": …}, …]</code> という形のJSONファイル。ジャンルごとの曲数を数えて、次の形式で <code>dest</code> に書き出します:</p>
<pre>ジャンル別レポート
house: 2曲
techno: 2曲
ambient: 1曲
合計: 5曲</pre>
<p>並び順は<b>曲数の多い順、同数ならジャンル名のアルファベット順</b>。<code>sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))</code> というテクニック（マイナスを付けて降順 + 名前で昇順）が使えます。</p>''',
            "starter": '''import json
from collections import Counter
from pathlib import Path


def make_report(src, dest):
    # 1) src のJSONを読む
    # 2) genre を Counter で数える
    # 3) 多い順（同数なら名前順）に並べる
    # 4) レポート文字列を組み立てて dest に書く
    pass
''',
            "hint": 'tracks = json.loads(Path(src).read_text(...)) → counts = Counter(t["genre"] for t in tracks) → ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])) → 行のリストを "\\n".join して Path(dest).write_text(...)。',
            "solution": '''import json
from collections import Counter
from pathlib import Path


def make_report(src, dest):
    tracks = json.loads(Path(src).read_text(encoding="utf-8"))
    counts = Counter(t["genre"] for t in tracks)
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    lines = ["ジャンル別レポート"]
    for genre, count in ordered:
        lines.append(f"{genre}: {count}曲")
    lines.append(f"合計: {len(tracks)}曲")

    Path(dest).write_text("\\n".join(lines) + "\\n", encoding="utf-8")''',
            "setup": '''import json
from pathlib import Path
tracks = [
    {"title": "Voyage", "genre": "techno"},
    {"title": "Aurora", "genre": "house"},
    {"title": "Pulse", "genre": "techno"},
    {"title": "Dawn", "genre": "ambient"},
    {"title": "Mist", "genre": "house"},
]
Path("tracks.json").write_text(json.dumps(tracks, ensure_ascii=False), encoding="utf-8")
''',
            "checks": [
                {"kind": "source", "name": "json でファイルを読んでいる", "pattern": "json\\.loads?\\s*\\(", "detail": "json.loads / json.load で src を読みます"},
                {"kind": "source", "name": "集計している（Counter か .get）", "pattern": "\\bCounter\\b|\\.get\\s*\\(", "detail": "Counter か「counts.get(g, 0) + 1」パターンで数えます"},
                {"kind": "eq", "name": "make_report が実行できる", "expr": "make_report('tracks.json', 'report.txt')", "want": "None"},
                {"kind": "eq", "name": "report.txt の内容が正しい", "expr": "Path('report.txt').read_text(encoding='utf-8').strip()", "want": "'ジャンル別レポート\\nhouse: 2曲\\ntechno: 2曲\\nambient: 1曲\\n合計: 5曲'"},
            ],
        },
    ],
}
