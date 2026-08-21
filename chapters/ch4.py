"""第4章 Pythonらしさ — クラス / dataclass / 例外処理 / with / import"""

CHAPTER = {
    "title": "第4章 Pythonらしさ",
    "resources": [
        {"label": "公式チュートリアル: エラーと例外", "url": "https://docs.python.org/ja/3/tutorial/errors.html"},
        {"label": "公式チュートリアル: クラス", "url": "https://docs.python.org/ja/3/tutorial/classes.html"},
        {"label": "公式ドキュメント: dataclasses", "url": "https://docs.python.org/ja/3/library/dataclasses.html"},
    ],
    "lessons": [
        {
            "id": "class_basics",
            "title": "クラスの基本",
            "desc": '''<h2>4-1. クラス — データと処理をまとめる</h2>
<p>クラスは「データ + それを扱う関数（メソッド）」のセットです。<code>__init__</code> が作成時に呼ばれる初期化メソッド（JSの <code>constructor</code>）。メソッドの第1引数は必ず <code>self</code>（自分自身。JSの <code>this</code> にあたるものを、Pythonは明示的に書きます）。</p>
<pre>class Timer:
    def __init__(self, seconds):
        self.seconds = seconds        # self.○○ = に代入するとプロパティになる

    def label(self):
        return f"残り{self.seconds}秒"

t = Timer(30)      # new は不要
t.label()          # → "残り30秒"</pre>
<p class="task"><b>課題:</b> クラス <code>Track</code> を作ってください。<code>Track(title, seconds)</code> で作成でき、<code>describe()</code> メソッドが <code>"Voyage（245秒）"</code> のような文字列を返します。</p>''',
            "starter": '''# class Track を定義する
# Track("Voyage", 245).describe() → "Voyage（245秒）"
''',
            "hint": 'class Track: の中に def __init__(self, title, seconds): で self.title と self.seconds に保存し、def describe(self): で f-string を return します。',
            "solution": '''class Track:
    def __init__(self, title, seconds):
        self.title = title
        self.seconds = seconds

    def describe(self):
        return f"{self.title}（{self.seconds}秒）"''',
            "checks": [
                {"kind": "source", "name": "class Track を定義している", "pattern": "class\\s+Track\\b", "detail": "class Track: と書きます"},
                {"kind": "source", "name": "__init__ を定義している", "pattern": "def\\s+__init__\\s*\\(\\s*self", "detail": "def __init__(self, title, seconds): と書きます"},
                {"kind": "source", "name": "self. に保存している", "pattern": "self\\.", "detail": "self.title = title のように保存します"},
                {"kind": "eq", "name": 'Track("Voyage", 245).describe()', "expr": "Track('Voyage', 245).describe()", "want": "'Voyage（245秒）'"},
                {"kind": "eq", "name": "title プロパティで取り出せる", "expr": "Track('Demo', 30).title", "want": "'Demo'"},
            ],
        },
        {
            "id": "dataclass",
            "title": "dataclass",
            "desc": '''<h2>4-2. dataclass — データの入れ物を1行で</h2>
<p>「データを持つだけのクラス」なら、<code>@dataclass</code> を付けるだけで <code>__init__</code> や <code>==</code> 比較を自動生成してくれます。フィールドは <code>名前: 型</code> と書きます — TSでやった型注釈と同じ発想です。</p>
<pre>from dataclasses import dataclass

@dataclass(frozen=True)     # frozen=True で変更禁止（immutable）になる
class Note:
    pitch: str
    velocity: int

Note("C4", 100) == Note("C4", 100)   # → True（自動で中身を比較！）</pre>
<p>変更したいときは、元を書き換えるのではなく<b>新しいインスタンスを作って返します</b>。</p>
<p class="task"><b>課題:</b> <code>@dataclass(frozen=True)</code> 付きで <code>x: int</code> と <code>y: int</code> を持つクラス <code>Point</code> を定義し、関数 <code>move(p, dx, dy)</code> を作ってください。移動後の<b>新しい</b> Point を返します。</p>''',
            "starter": '''from dataclasses import dataclass

# @dataclass(frozen=True) を付けて class Point を定義（x: int と y: int）


# 関数 move(p, dx, dy) — 新しい Point(p.x + dx, p.y + dy) を返す
''',
            "hint": "@dataclass(frozen=True) の次の行に class Point: を書き、中は x: int と y: int の2行。move は return Point(p.x + dx, p.y + dy)。",
            "solution": '''from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


def move(p, dx, dy):
    return Point(p.x + dx, p.y + dy)''',
            "checks": [
                {"kind": "source", "name": "@dataclass を使っている", "pattern": "@\\s*dataclass", "detail": "class の直前の行に @dataclass(frozen=True) と書きます"},
                {"kind": "source", "name": "frozen=True にしている", "pattern": "frozen\\s*=\\s*True", "detail": "@dataclass(frozen=True) で変更禁止にします"},
                {"kind": "eq", "name": "== で中身が比較できる", "expr": "Point(1, 2) == Point(1, 2)", "want": "True"},
                {"kind": "eq", "name": "move(Point(1, 2), 3, 4) → Point(4, 6)", "expr": "move(Point(1, 2), 3, 4) == Point(4, 6)", "want": "True"},
                {"kind": "eq", "name": "x が取り出せる", "expr": "Point(1, 2).x", "want": "1"},
            ],
        },
        {
            "id": "try_except",
            "title": "try / except",
            "desc": '''<h2>4-3. try / except — 失敗に備える</h2>
<p>失敗しそうな処理は <code>try:</code> に書き、失敗したときの処理を <code>except エラー名:</code> に書きます（JSの <code>try/catch</code>）。Pythonでは<b>捕まえるエラーの種類を指定する</b>のがお作法。たとえば <code>int("abc")</code> は <code>ValueError</code> を投げます。</p>
<pre>try:
    n = int(text)
except ValueError:          # 「数字じゃなかった」だけを捕まえる
    n = 0</pre>
<p>裸の <code>except:</code>（種類指定なし）は、想定外のバグまで握りつぶすので避けます。</p>
<p class="task"><b>課題:</b> 関数 <code>to_int(text, fallback=0)</code> を作ってください。<code>int(text)</code> を試し、<code>ValueError</code> のときは <code>fallback</code> を返します。</p>''',
            "starter": '''def to_int(text, fallback=0):
    # int(text) を try して、ValueError なら fallback を返す
    pass
''',
            "hint": "try: return int(text) → except ValueError: return fallback の4行です。",
            "solution": '''def to_int(text, fallback=0):
    try:
        return int(text)
    except ValueError:
        return fallback''',
            "checks": [
                {"kind": "source", "name": "try を使っている", "pattern": "\\btry\\s*:", "detail": "try: のブロックで int(text) を試します"},
                {"kind": "source", "name": "except ValueError と種類を指定している", "pattern": "except\\s+ValueError\\b", "detail": "裸の except: ではなく except ValueError: と書きます"},
                {"kind": "eq", "name": 'to_int("42") → 42', "expr": "to_int('42')", "want": "42"},
                {"kind": "eq", "name": 'to_int("abc") → 0', "expr": "to_int('abc')", "want": "0"},
                {"kind": "eq", "name": 'to_int("3.5") → 0（int にできない）', "expr": "to_int('3.5')", "want": "0"},
                {"kind": "eq", "name": 'to_int("abc", -1) → -1', "expr": "to_int('abc', -1)", "want": "-1"},
            ],
        },
        {
            "id": "with_file",
            "title": "with文",
            "desc": '''<h2>4-4. with文 — 後片付けを任せる</h2>
<p>3-5で使った <code>with</code> の正体は<b>コンテキストマネージャ</b>。「使い終わったら必ず閉じる」という後片付けを、<b>途中でエラーが起きても</b>確実にやってくれる仕組みです。ファイル以外にもロックやDB接続など「開いたら閉じる」ものすべてに使われます。</p>
<pre>with open("data.txt", encoding="utf-8") as f:
    first = f.readline()        # 1行だけ読む（末尾に改行が付いてくる）
    rest = f.readlines()        # 残りを行のリストで</pre>
<p>行末の改行は <code>.strip()</code>（前後の空白・改行を除去）で落とすのが定番です。</p>
<p class="task"><b>課題:</b> <code>first_line(path)</code> はファイルの1行目を（改行を除いて）返す。<code>count_lines(path)</code> は行数を返す。どちらも with で開いてください。採点時は <code>song_list.txt</code>（3行）が用意されています。</p>''',
            "starter": '''def first_line(path):
    # 1行目を読んで .strip() して返す
    pass


def count_lines(path):
    # len(f.readlines()) で行数を返す
    pass
''',
            "hint": 'with open(path, encoding="utf-8") as f: の中で、first_line は return f.readline().strip()、count_lines は return len(f.readlines())。',
            "solution": '''def first_line(path):
    with open(path, encoding="utf-8") as f:
        return f.readline().strip()


def count_lines(path):
    with open(path, encoding="utf-8") as f:
        return len(f.readlines())''',
            "setup": '''from pathlib import Path
Path("song_list.txt").write_text("Voyage\\nAurora\\nNight Drive\\n", encoding="utf-8")
''',
            "checks": [
                {"kind": "source", "name": "with open を使っている", "pattern": "with\\s+open\\s*\\(", "detail": "with open(path, encoding=\"utf-8\") as f: と書きます"},
                {"kind": "eq", "name": 'first_line("song_list.txt") → "Voyage"', "expr": "first_line('song_list.txt')", "want": "'Voyage'"},
                {"kind": "eq", "name": 'count_lines("song_list.txt") → 3', "expr": "count_lines('song_list.txt')", "want": "3"},
            ],
        },
        {
            "id": "imports",
            "title": "import",
            "desc": '''<h2>4-5. import — 道具箱を持ってくる</h2>
<p>Pythonには「電池同梱（batteries included）」と呼ばれる豊富な標準ライブラリがあり、<code>import</code> で取り込んで使います。書き方は2通り:</p>
<pre>import math                  # math.sqrt(2) と、モジュール名を付けて使う
from math import sqrt        # sqrt(2) と、直接使う</pre>
<p>基本は <code>import math</code> 型（どこから来た関数か一目で分かる）。よく使うものだけ <code>from</code> 型にするのがバランスの良い使い分けです。importはファイルの先頭にまとめて書きます。</p>
<p class="task"><b>課題:</b> <code>import math</code> して、円の面積を返す <code>circle_area(r)</code>（<code>math.pi * r * r</code>）を作ってください。さらに <code>from math import sqrt</code> して、長方形の対角線の長さを返す <code>diagonal(w, h)</code>（<code>sqrt(w*w + h*h)</code>）も作ってください。</p>''',
            "starter": '''# import 2種類を書く

# circle_area(r) … math.pi * r * r

# diagonal(w, h) … sqrt(w*w + h*h)
''',
            "hint": "先頭に import math と from math import sqrt の2行。あとは def を2つ書くだけです。",
            "solution": '''import math
from math import sqrt


def circle_area(r):
    return math.pi * r * r


def diagonal(w, h):
    return sqrt(w * w + h * h)''',
            "checks": [
                {"kind": "source", "name": "import math している", "pattern": "^\\s*import\\s+math\\b", "detail": "import math と1行書きます"},
                {"kind": "source", "name": "from math import sqrt している", "pattern": "from\\s+math\\s+import\\s+sqrt\\b", "detail": "from math import sqrt と書きます"},
                {"kind": "eq", "name": "circle_area(1) → π", "expr": "circle_area(1) == math.pi", "want": "True"},
                {"kind": "eq", "name": "circle_area(2) → 4π", "expr": "circle_area(2) == math.pi * 4", "want": "True"},
                {"kind": "eq", "name": "diagonal(3, 4) → 5.0", "expr": "diagonal(3, 4)", "want": "5.0"},
            ],
        },
    ],
}
