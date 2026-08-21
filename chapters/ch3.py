"""第3章 データ操作 — sorted / zip / enumerate / map / filter / 辞書操作 / ファイルI/O"""

CHAPTER = {
    "title": "第3章 データ操作",
    "resources": [
        {"label": "公式チュートリアル: データ構造", "url": "https://docs.python.org/ja/3/tutorial/datastructures.html"},
        {"label": "公式チュートリアル: 入力と出力", "url": "https://docs.python.org/ja/3/tutorial/inputoutput.html"},
        {"label": "Automate the Boring Stuff Ch.9 (Files)", "url": "https://automatetheboringstuff.com/2e/chapter9/"},
    ],
    "lessons": [
        {
            "id": "sorted_key",
            "title": "sorted と key",
            "desc": '''<h2>3-1. sorted — 並べ替えの決定版</h2>
<p><code>sorted(リスト)</code> は<b>新しい</b>並べ替え済みリストを返します（元は変えない）。<code>.sort()</code> は元を書き換えるので、基本は <code>sorted</code> を使いましょう。</p>
<p>並べ替えの基準は <code>key=関数</code> で渡します。前章の lambda の出番です。</p>
<pre>sorted(["bb", "a", "ccc"], key=len)              # 文字数順
sorted(nums, reverse=True)                        # 大きい順
sorted(tracks, key=lambda t: t["plays"])          # 辞書の値で並べ替え</pre>
<p class="task"><b>課題:</b> 2つの関数を作ってください。<code>sort_by_length(words)</code> は文字数の短い順。<code>top_played(tracks)</code> は <code>{"title": …, "plays": …}</code> の辞書リストを再生数の<b>多い順</b>に（<code>reverse=True</code>）。どちらも <code>.sort()</code> ではなく <code>sorted</code> で。</p>''',
            "starter": '''def sort_by_length(words):
    # 文字数の短い順（key=len）
    pass


def top_played(tracks):
    # plays の多い順（key=lambda ..., reverse=True）
    pass
''',
            "hint": 'return sorted(words, key=len) と return sorted(tracks, key=lambda t: t["plays"], reverse=True) です。',
            "solution": '''def sort_by_length(words):
    return sorted(words, key=len)


def top_played(tracks):
    return sorted(tracks, key=lambda t: t["plays"], reverse=True)''',
            "checks": [
                {"kind": "source", "name": "key= を使っている", "pattern": "key\\s*=", "detail": "sorted(..., key=...) の形で書きます"},
                {"kind": "source", "name": "reverse=True を使っている", "pattern": "reverse\\s*=\\s*True", "detail": "多い順は reverse=True です"},
                {"kind": "source", "name": ".sort() を使っていない（元を壊さない）", "pattern": "\\.sort\\s*\\(", "not": True, "detail": "元のリストを変更しない sorted() を使ってください"},
                {"kind": "eq", "name": 'sort_by_length(["bb", "a", "ccc"])', "expr": "sort_by_length(['bb', 'a', 'ccc'])", "want": "['a', 'bb', 'ccc']"},
                {"kind": "eq", "name": "top_played が再生数の多い順", "expr": "[t['title'] for t in top_played([{'title': 'A', 'plays': 10}, {'title': 'B', 'plays': 90}, {'title': 'C', 'plays': 50}])]", "want": "['B', 'C', 'A']"},
            ],
        },
        {
            "id": "zip_enumerate",
            "title": "zip と enumerate",
            "desc": '''<h2>3-2. zip と enumerate — forの相棒</h2>
<p>「番号付きで回したい」「2つのリストを同時に回したい」はPython頻出の場面。インデックス変数を手で管理せず、この2つを使います。</p>
<pre>for i, name in enumerate(["kick", "snare"], 1):   # 1 から番号を振る
    print(i, name)        # 1 kick / 2 snare

for name, age in zip(["Miku", "Rin"], [16, 14]):  # 同じ位置同士をペアに
    print(name, age)      # Miku 16 / Rin 14</pre>
<p>どちらも内包表記と組み合わせられます。</p>
<p class="task"><b>課題:</b> <code>numbered(items)</code> は <code>["1. kick", "2. snare"]</code> のような番号付きリストを（enumerateを1始まりで）、<code>pair_up(names, ages)</code> は <code>["Miku（16歳）", …]</code> をzipで作って返してください。</p>''',
            "starter": '''def numbered(items):
    # enumerate(items, 1) で「1. 名前」のリストに
    pass


def pair_up(names, ages):
    # zip で「名前（○歳）」のリストに
    pass
''',
            "hint": 'return [f"{i}. {item}" for i, item in enumerate(items, 1)] と return [f"{n}（{a}歳）" for n, a in zip(names, ages)] です。',
            "solution": '''def numbered(items):
    return [f"{i}. {item}" for i, item in enumerate(items, 1)]


def pair_up(names, ages):
    return [f"{n}（{a}歳）" for n, a in zip(names, ages)]''',
            "checks": [
                {"kind": "source", "name": "enumerate を使っている", "pattern": "\\benumerate\\s*\\(", "detail": "enumerate(items, 1) で1始まりの番号を振ります"},
                {"kind": "source", "name": "zip を使っている", "pattern": "\\bzip\\s*\\(", "detail": "zip(names, ages) でペアにします"},
                {"kind": "eq", "name": 'numbered(["kick", "snare"])', "expr": "numbered(['kick', 'snare'])", "want": "['1. kick', '2. snare']"},
                {"kind": "eq", "name": "numbered([])", "expr": "numbered([])", "want": "[]"},
                {"kind": "eq", "name": 'pair_up(["Miku", "Rin"], [16, 14])', "expr": "pair_up(['Miku', 'Rin'], [16, 14])", "want": "['Miku（16歳）', 'Rin（14歳）']"},
            ],
        },
        {
            "id": "map_filter",
            "title": "map と filter",
            "desc": '''<h2>3-3. map と filter — 関数を渡して変換・絞り込み</h2>
<p>JSでおなじみの <code>map</code> / <code>filter</code> はPythonにもあります。ただし返るのはリストではなく「イテレータ」なので、<code>list()</code> で包んでリストにします。</p>
<pre>list(map(lambda n: n * 10, [1, 2]))            # [10, 20]
list(filter(lambda n: n &gt; 0, [-1, 2, -3]))     # [2]</pre>
<p>実は2-4の内包表記と同じことができます（Pythonでは内包表記の方が好まれる場面が多い）。両方読めるようにしておきましょう。</p>
<p class="task"><b>課題:</b> 今回は map / filter の練習です。<code>doubled(nums)</code> は map で各要素を2倍に、<code>evens(nums)</code> は filter で偶数（<code>n % 2 == 0</code>）だけにして返してください。</p>''',
            "starter": '''def doubled(nums):
    # map を使う
    pass


def evens(nums):
    # filter を使う
    pass
''',
            "hint": "return list(map(lambda n: n * 2, nums)) と return list(filter(lambda n: n % 2 == 0, nums)) です。list() を忘れずに。",
            "solution": '''def doubled(nums):
    return list(map(lambda n: n * 2, nums))


def evens(nums):
    return list(filter(lambda n: n % 2 == 0, nums))''',
            "checks": [
                {"kind": "source", "name": "map を使っている", "pattern": "\\bmap\\s*\\(", "detail": "map(lambda n: n * 2, nums) の形で書きます"},
                {"kind": "source", "name": "filter を使っている", "pattern": "\\bfilter\\s*\\(", "detail": "filter(lambda n: n % 2 == 0, nums) の形で書きます"},
                {"kind": "eq", "name": "doubled([1, 2, 3])", "expr": "doubled([1, 2, 3])", "want": "[2, 4, 6]"},
                {"kind": "eq", "name": "evens([1, 2, 3, 4])", "expr": "evens([1, 2, 3, 4])", "want": "[2, 4]"},
                {"kind": "eq", "name": "evens([])", "expr": "evens([])", "want": "[]"},
            ],
        },
        {
            "id": "dict_ops",
            "title": "辞書の操作",
            "desc": '''<h2>3-4. 辞書の操作 — .get と集計とマージ</h2>
<p><code>d["key"]</code> はキーがないとエラー（<code>KeyError</code>）になります。<code>d.get("key", 既定値)</code> なら、なくても既定値が返って安全。この性質を使うと「出現回数の集計」が定番パターンで書けます。</p>
<pre>counts = {}
for g in genres:
    counts[g] = counts.get(g, 0) + 1   # 初出なら 0 から数え始める</pre>
<p>2つの辞書をまとめるのは <code>{**a, **b}</code>（同じキーは後ろが勝つ）。JSのスプレッド <code>{...a, ...b}</code> と同じ発想です。</p>
<p class="task"><b>課題:</b> <code>count_genres(genres)</code> は上のパターンで出現回数の辞書を、<code>merged(a, b)</code> は <code>{**a, **b}</code> で合体した<b>新しい</b>辞書を返してください。</p>''',
            "starter": '''def count_genres(genres):
    # .get(g, 0) + 1 のパターンで数える
    pass


def merged(a, b):
    # {**a, **b} で新しい辞書に
    pass
''',
            "hint": "counts = {} → for g in genres: counts[g] = counts.get(g, 0) + 1 → return counts。merged は return {**a, **b} の1行。",
            "solution": '''def count_genres(genres):
    counts = {}
    for g in genres:
        counts[g] = counts.get(g, 0) + 1
    return counts


def merged(a, b):
    return {**a, **b}''',
            "checks": [
                {"kind": "source", "name": ".get を使っている", "pattern": "\\.get\\s*\\(", "detail": "counts.get(g, 0) の形で書きます"},
                {"kind": "eq", "name": 'count_genres(["techno", "house", "techno"])', "expr": "count_genres(['techno', 'house', 'techno'])", "want": "{'techno': 2, 'house': 1}"},
                {"kind": "eq", "name": "count_genres([])", "expr": "count_genres([])", "want": "{}"},
                {"kind": "eq", "name": 'merged({"a": 1}, {"b": 2})', "expr": "merged({'a': 1}, {'b': 2})", "want": "{'a': 1, 'b': 2}"},
                {"kind": "eq", "name": "同じキーは後ろの辞書が勝つ", "expr": "merged({'a': 1}, {'a': 9})", "want": "{'a': 9}"},
                {"kind": "eq", "name": "元の辞書を変更しない", "expr": "(lambda a: (merged(a, {'b': 2}), a)[1])({'a': 1})", "want": "{'a': 1}"},
            ],
        },
        {
            "id": "file_io",
            "title": "ファイル入出力",
            "desc": '''<h2>3-5. ファイル入出力 — 書いて、読む</h2>
<p>ファイルは <code>open(パス, モード)</code> で開きます。モードは <code>"w"</code>（書き込み・上書き）と <code>"r"</code>（読み込み・省略時はこれ）。日本語を扱うので <code>encoding="utf-8"</code> を必ず付けます。</p>
<p>開いたファイルは閉じる必要がありますが、<code>with</code> 構文を使うとブロックを抜けたとき<b>自動で</b>閉じてくれます。ファイルを開くときは常に with — がPythonのお作法です（仕組みは第4章で）。</p>
<pre>with open("log.txt", "w", encoding="utf-8") as f:
    f.write("こんにちは")

with open("log.txt", encoding="utf-8") as f:
    text = f.read()</pre>
<p class="task"><b>課題:</b> <code>save_memo(text)</code> は <code>memo.txt</code> にtextを書き込む。<code>load_memo()</code> は <code>memo.txt</code> を読んで中身を返す。どちらも with を使ってください。（採点は使い捨ての一時フォルダで実行されるので、実際にファイルを作って大丈夫です）</p>''',
            "starter": '''def save_memo(text):
    # memo.txt に text を書き込む（with open を使う）
    pass


def load_memo():
    # memo.txt を読んで中身を return する
    pass
''',
            "hint": 'save は with open("memo.txt", "w", encoding="utf-8") as f: f.write(text)。load は "r" で開いて return f.read()（with ブロックの中で return してOK）。',
            "solution": '''def save_memo(text):
    with open("memo.txt", "w", encoding="utf-8") as f:
        f.write(text)


def load_memo():
    with open("memo.txt", encoding="utf-8") as f:
        return f.read()''',
            "checks": [
                {"kind": "source", "name": "with open を使っている", "pattern": "with\\s+open\\s*\\(", "detail": "with open(...) as f: の形で書きます"},
                {"kind": "eq", "name": "save_memo が実行できる（返り値はなし）", "expr": "save_memo('今日の練習メモ')", "want": "None"},
                {"kind": "eq", "name": "memo.txt に書き込まれている", "expr": "Path('memo.txt').read_text(encoding='utf-8')", "want": "'今日の練習メモ'"},
                {"kind": "eq", "name": "load_memo が中身を返す", "expr": "load_memo()", "want": "'今日の練習メモ'"},
            ],
        },
    ],
}
