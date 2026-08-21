"""第1章 基本 — 変数・型 / f-string・スライス / リスト・辞書・タプル・セット"""

CHAPTER = {
    "title": "第1章 基本",
    "resources": [
        {"label": "公式チュートリアル: 形式ばらない入門", "url": "https://docs.python.org/ja/3/tutorial/introduction.html"},
        {"label": "公式チュートリアル: データ構造", "url": "https://docs.python.org/ja/3/tutorial/datastructures.html"},
        {"label": "Automate the Boring Stuff Ch.1", "url": "https://automatetheboringstuff.com/2e/chapter1/"},
    ],
    "lessons": [
        {
            "id": "variables",
            "title": "変数と型",
            "desc": '''<h2>1-1. 変数と型 — 名前に値を入れる</h2>
<p>Pythonの変数は <code>名前 = 値</code> と書くだけ。JS/TSと違って <code>let</code> も <code>const</code> も型注釈も不要で、<b>入れた値で型が決まります</b>。基本の型は4つ:</p>
<pre>song = "Aurora"      # str（文字列。" でも ' でもOK）
count = 3            # int（整数）
gain = 0.5           # float（小数点があると float）
muted = True         # bool（True / False — 先頭が大文字！JSの true とは違う）</pre>
<p>値の型は <code>type(count)</code> で確認できます。</p>
<p class="task"><b>課題:</b> コメントの指定どおりに4つの変数を作ってください。</p>''',
            "starter": '''# title      … 文字列 "Night Drive"
# bpm        … 整数 128
# volume     … 小数 0.8
# is_playing … 真偽値 False
''',
            "hint": 'title = "Night Drive" のように1行ずつ書くだけです。False の先頭は大文字。0.8 はそのまま小数点つきで。',
            "solution": '''title = "Night Drive"
bpm = 128
volume = 0.8
is_playing = False''',
            "checks": [
                {"kind": "eq", "name": 'title は文字列 "Night Drive"', "expr": "title", "want": "'Night Drive'", "type": "str"},
                {"kind": "eq", "name": "bpm は整数 128", "expr": "bpm", "want": "128", "type": "int"},
                {"kind": "eq", "name": "volume は小数 0.8", "expr": "volume", "want": "0.8", "type": "float"},
                {"kind": "eq", "name": "is_playing は真偽値 False", "expr": "is_playing", "want": "False", "type": "bool"},
            ],
        },
        {
            "id": "fstring",
            "title": "f-string と print",
            "desc": '''<h2>1-2. f-string — 文字列に値を埋め込む</h2>
<p>文字列の前に <code>f</code> を付けると、中の <code>{ }</code> に変数や式を埋め込めます。JSのテンプレートリテラル <code>`${name}`</code> のPython版です。</p>
<pre>artist = "Rin"
line = f"演奏: {artist}"        # → "演奏: Rin"
total = f"{1500 * 2:,}円"       # → "3,000円"（:, は3桁区切りの書式指定）</pre>
<p>画面への出力は <code>print(line)</code>。<code>console.log</code> にあたります。</p>
<p class="task"><b>課題:</b> f-string を使って <code>intro</code> と <code>msg</code> を作り、<code>intro</code> を print してください。</p>''',
            "starter": '''name = "Miku"
age = 16
price = 1980

# intro … 「Miku（16歳）」という文字列（f-string で name と age を埋め込む）
# msg   … 「合計: 1,980円」という文字列（:, で3桁区切りに）
# intro を print する
''',
            "hint": 'intro = f"{name}（{age}歳）"、msg = f"合計: {price:,}円"。最後に print(intro) です。',
            "solution": '''name = "Miku"
age = 16
price = 1980

intro = f"{name}（{age}歳）"
msg = f"合計: {price:,}円"
print(intro)''',
            "checks": [
                {"kind": "source", "name": "f-string を使っている", "pattern": "f[\"']", "detail": '文字列の前に f を付けます（例: f"{name}"）'},
                {"kind": "eq", "name": "intro が「Miku（16歳）」", "expr": "intro", "want": "'Miku（16歳）'"},
                {"kind": "eq", "name": "msg が「合計: 1,980円」", "expr": "msg", "want": "'合計: 1,980円'"},
                {"kind": "stdout", "name": "intro を print している", "contains": "Miku（16歳）"},
            ],
        },
        {
            "id": "slice",
            "title": "スライス",
            "desc": '''<h2>1-3. スライス — 文字列を切り出す</h2>
<p><code>word[開始:終了]</code> で部分文字列を切り出せます。<b>終了は含まない</b>のがポイント。負の数は「後ろから数える」、省略は「端まで」という意味です。</p>
<pre>word = "keyboard"
word[0]      # "k"（1文字の取り出し）
word[:3]     # "key"（最初の3文字）
word[-2:]    # "rd"（最後の2文字）
word[1:-1]   # "eyboar"（最初と最後を除く）
word[::-1]   # "draobyek"（ステップ -1 = 逆順）</pre>
<p>スライスはリストにもそのまま使えます。</p>
<p class="task"><b>課題:</b> <code>word</code> からコメントの指定どおりに4つの変数を切り出してください。</p>''',
            "starter": '''word = "synthesizer"

# first3        … 最初の3文字 "syn"
# last3         … 最後の3文字 "zer"
# inner         … 最初と最後の1文字を除いた "ynthesize"
# reversed_word … 逆順 "rezisehtnys"（[::-1] を使う）
''',
            "hint": "first3 = word[:3]、last3 = word[-3:]、inner = word[1:-1]、reversed_word = word[::-1] です。",
            "solution": '''word = "synthesizer"

first3 = word[:3]
last3 = word[-3:]
inner = word[1:-1]
reversed_word = word[::-1]''',
            "checks": [
                {"kind": "eq", "name": 'first3 は "syn"', "expr": "first3", "want": "'syn'"},
                {"kind": "eq", "name": 'last3 は "zer"', "expr": "last3", "want": "'zer'"},
                {"kind": "eq", "name": 'inner は "ynthesize"', "expr": "inner", "want": "'ynthesize'"},
                {"kind": "eq", "name": 'reversed_word は "rezisehtnys"', "expr": "reversed_word", "want": "'rezisehtnys'"},
                {"kind": "source", "name": "[::-1] で逆順にしている", "pattern": "\\[\\s*:\\s*:\\s*-1\\s*\\]", "detail": "reversed_word は word[::-1] と書きます"},
            ],
        },
        {
            "id": "list_dict",
            "title": "リストと辞書",
            "desc": '''<h2>1-4. リストと辞書 — 一番よく使う入れ物</h2>
<p><b>リスト</b>はJSの配列。<code>.append()</code> で末尾に追加し、<code>[0]</code> で取り出します。<b>辞書（dict）</b>はJSのオブジェクトに近いキーと値のペアで、<code>d["key"]</code> で読み書きします（<code>d.key</code> とは書けません）。</p>
<pre>chords = ["Am", "F"]
chords.append("C")      # ["Am", "F", "C"]
first = chords[0]       # "Am"

song = {"artist": "Rin", "year": 2026}
song["genre"] = "pop"   # キーの追加も代入するだけ
year = song["year"]     # 2026</pre>
<p class="task"><b>課題:</b> コメントの4つの操作を上から順に書いてください。</p>''',
            "starter": '''notes = ["C", "E", "G"]
track = {"title": "Voyage", "bpm": 128}

# 1) notes の末尾に "B" を追加する（.append を使う）
# 2) first_note に notes の最初の要素を入れる
# 3) track に "genre" キーを追加して値を "techno" にする
# 4) bpm に track の "bpm" の値を取り出す
''',
            "hint": 'notes.append("B") → first_note = notes[0] → track["genre"] = "techno" → bpm = track["bpm"] の順です。',
            "solution": '''notes = ["C", "E", "G"]
track = {"title": "Voyage", "bpm": 128}

notes.append("B")
first_note = notes[0]
track["genre"] = "techno"
bpm = track["bpm"]''',
            "checks": [
                {"kind": "source", "name": ".append を使っている", "pattern": "\\.append\\s*\\(", "detail": 'notes.append("B") と書きます'},
                {"kind": "eq", "name": 'notes の末尾に "B" が追加されている', "expr": "notes", "want": "['C', 'E', 'G', 'B']"},
                {"kind": "eq", "name": 'first_note は "C"', "expr": "first_note", "want": "'C'"},
                {"kind": "eq", "name": "track に genre が追加されている", "expr": "track", "want": "{'title': 'Voyage', 'bpm': 128, 'genre': 'techno'}"},
                {"kind": "eq", "name": "bpm は 128", "expr": "bpm", "want": "128"},
            ],
        },
        {
            "id": "tuple_set",
            "title": "タプルとセット",
            "desc": '''<h2>1-5. タプルとセット — 変えない・重複しない</h2>
<p><b>タプル</b>は「変更できないリスト」。<code>(3, 4)</code> のように作り、<code>x, y = point</code> で一気に複数の変数に展開できます（アンパック）。座標やペアなど「セットで1つ」の値に使います。</p>
<p><b>セット（set）</b>は「重複のない集合」。リストを <code>set()</code> に通すと重複が消えます。順番は保証されません。</p>
<pre>pair = (60, 100)         # タプル
note, velocity = pair    # アンパック

tags = set(["rock", "pop", "rock"])   # {"rock", "pop"} — 重複が消える
"pop" in tags                          # True（含まれるか確認）</pre>
<p class="task"><b>課題:</b> アンパックとセットを使って、コメントの3つを書いてください。</p>''',
            "starter": '''point = (3, 4)
genres = ["techno", "house", "techno", "techno", "house"]

# 1) x, y = point の形で、タプルを2つの変数に展開する
# 2) unique に genres の重複を除いたセットを作る（set() を使う）
# 3) count に unique の要素数を入れる（len() を使う）
''',
            "hint": "x, y = point → unique = set(genres) → count = len(unique) の3行です。",
            "solution": '''point = (3, 4)
genres = ["techno", "house", "techno", "techno", "house"]

x, y = point
unique = set(genres)
count = len(unique)''',
            "checks": [
                {"kind": "source", "name": "set() を使っている", "pattern": "\\bset\\s*\\(", "detail": "unique = set(genres) と書きます"},
                {"kind": "eq", "name": "x は 3", "expr": "x", "want": "3"},
                {"kind": "eq", "name": "y は 4", "expr": "y", "want": "4"},
                {"kind": "eq", "name": "unique は {'techno', 'house'}", "expr": "unique", "want": "{'techno', 'house'}"},
                {"kind": "eq", "name": "count は 2", "expr": "count", "want": "2"},
            ],
        },
    ],
}
