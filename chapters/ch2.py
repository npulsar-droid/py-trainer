"""第2章 制御・関数 — def / if / for / while / 内包表記 / 引数いろいろ / lambda"""

CHAPTER = {
    "title": "第2章 制御・関数",
    "resources": [
        {"label": "公式チュートリアル: 制御構造", "url": "https://docs.python.org/ja/3/tutorial/controlflow.html"},
        {"label": "Automate the Boring Stuff Ch.2 (Flow Control)", "url": "https://automatetheboringstuff.com/2e/chapter2/"},
        {"label": "Automate the Boring Stuff Ch.3 (Functions)", "url": "https://automatetheboringstuff.com/2e/chapter3/"},
    ],
    "lessons": [
        {
            "id": "def_basics",
            "title": "関数の基本",
            "desc": '''<h2>2-1. 関数 — def と return とインデント</h2>
<p>関数は <code>def 名前(引数):</code> で定義します。JSの <code>{ }</code> の代わりに、Pythonは<b>コロン + インデント（字下げ4つ）</b>で中身の範囲を表します。インデントが文法の一部なのがPython最大の特徴です。</p>
<pre>def add(a, b):
    return a + b    # ← 半角スペース4つ下げる

add(1, 2)           # → 3</pre>
<p><code>return</code> を忘れると <code>None</code>（JSの <code>undefined</code> にあたる「何もない」値）が返ります。</p>
<p class="task"><b>課題:</b> 関数 <code>describe_track(title, seconds)</code> を定義してください。<code>"Voyage（245秒）"</code> のような文字列を f-string で作って return します。</p>''',
            "starter": '''# 関数 describe_track(title, seconds) を定義する
# 例: describe_track("Voyage", 245) → "Voyage（245秒）"
''',
            "hint": 'def describe_track(title, seconds): の次の行を4つ下げて、return f"{title}（{seconds}秒）" です。',
            "solution": '''def describe_track(title, seconds):
    return f"{title}（{seconds}秒）"''',
            "checks": [
                {"kind": "source", "name": "def で定義している", "pattern": "def\\s+describe_track\\s*\\(", "detail": "def describe_track(title, seconds): と書きます"},
                {"kind": "source", "name": "return している", "pattern": "\\breturn\\b", "detail": "print ではなく return で値を返します"},
                {"kind": "eq", "name": 'describe_track("Voyage", 245)', "expr": "describe_track('Voyage', 245)", "want": "'Voyage（245秒）'"},
                {"kind": "eq", "name": 'describe_track("Demo", 30)', "expr": "describe_track('Demo', 30)", "want": "'Demo（30秒）'"},
            ],
        },
        {
            "id": "if_elif",
            "title": "if / elif / else",
            "desc": '''<h2>2-2. if / elif / else — 条件分岐</h2>
<p>JSの <code>else if</code> はPythonでは <code>elif</code>。条件のカッコは不要で、ここでもコロンとインデントで範囲を表します。<code>&amp;&amp;</code> / <code>||</code> / <code>!</code> は <code>and</code> / <code>or</code> / <code>not</code> と英単語で書きます。</p>
<pre>def volume_label(v):
    if v == 0:
        return "無音"
    elif v &lt; 50:
        return "小さい"
    else:
        return "大きい"</pre>
<p class="task"><b>課題:</b> 関数 <code>tempo_label(bpm)</code> を作ってください。100未満なら <code>"slow"</code>、100以上140以下なら <code>"mid"</code>、それより大きければ <code>"fast"</code> を返します。</p>''',
            "starter": '''def tempo_label(bpm):
    # 100未満 → "slow" / 100〜140 → "mid" / それ以上 → "fast"
    pass
''',
            "hint": 'if bpm < 100: → elif bpm <= 140: → else: の3段です。pass（何もしない仮置き）は消してください。',
            "solution": '''def tempo_label(bpm):
    if bpm < 100:
        return "slow"
    elif bpm <= 140:
        return "mid"
    else:
        return "fast"''',
            "checks": [
                {"kind": "source", "name": "elif を使っている", "pattern": "\\belif\\b", "detail": "else if ではなく elif と書きます"},
                {"kind": "eq", "name": "tempo_label(90) → slow", "expr": "tempo_label(90)", "want": "'slow'"},
                {"kind": "eq", "name": "tempo_label(100) → mid（境界値）", "expr": "tempo_label(100)", "want": "'mid'"},
                {"kind": "eq", "name": "tempo_label(140) → mid（境界値）", "expr": "tempo_label(140)", "want": "'mid'"},
                {"kind": "eq", "name": "tempo_label(170) → fast", "expr": "tempo_label(170)", "want": "'fast'"},
            ],
        },
        {
            "id": "for_while",
            "title": "for と while",
            "desc": '''<h2>2-3. for と while — 繰り返し</h2>
<p>Pythonの <code>for</code> はJSの <code>for...of</code> にあたり、<b>要素を直接</b>取り出します。回数で回したいときは <code>range(n)</code>（0〜n-1）を使います。<code>while</code> は条件が真の間繰り返します。</p>
<pre>for note in ["C", "E", "G"]:
    print(note)

n = 3
while n &gt; 0:
    n = n - 1    # n -= 1 とも書ける</pre>
<p class="task"><b>課題:</b> 2つの関数を作ってください。<code>total_seconds(durations)</code> は for で合計を足し上げて返す（練習なので <code>sum()</code> は使わない）。<code>countdown(n)</code> は while で <code>[n, n-1, …, 1]</code> のリストを作って返す。</p>''',
            "starter": '''def total_seconds(durations):
    # for で1つずつ足し上げる（sum() は使わない）
    pass


def countdown(n):
    # while で [n, n-1, ..., 1] のリストを作る
    pass
''',
            "hint": "total = 0 を用意して for d in durations: total += d。countdown は result = [] に while n > 0: で append して n -= 1。",
            "solution": '''def total_seconds(durations):
    total = 0
    for d in durations:
        total += d
    return total


def countdown(n):
    result = []
    while n > 0:
        result.append(n)
        n -= 1
    return result''',
            "checks": [
                {"kind": "source", "name": "for を使っている", "pattern": "\\bfor\\b", "detail": "for d in durations: の形で回します"},
                {"kind": "source", "name": "while を使っている", "pattern": "\\bwhile\\b", "detail": "countdown は while で書きます"},
                {"kind": "source", "name": "sum() を使っていない（今回は手で足す練習）", "pattern": "\\bsum\\s*\\(", "not": True, "detail": "今回は sum() を使わず、for で足し上げてください"},
                {"kind": "eq", "name": "total_seconds([30, 90, 120])", "expr": "total_seconds([30, 90, 120])", "want": "240"},
                {"kind": "eq", "name": "total_seconds([])", "expr": "total_seconds([])", "want": "0"},
                {"kind": "eq", "name": "countdown(3)", "expr": "countdown(3)", "want": "[3, 2, 1]"},
                {"kind": "eq", "name": "countdown(0)", "expr": "countdown(0)", "want": "[]"},
            ],
        },
        {
            "id": "comprehension",
            "title": "内包表記",
            "desc": '''<h2>2-4. 内包表記 — リストを1行で作る</h2>
<p>「forで回して新しいリストを作る」処理は、Pythonでは<b>リスト内包表記</b>で1行に書けます。JSの <code>map</code> / <code>filter</code> にあたる、Pythonで一番よく見る書き方です。</p>
<pre>nums = [1, 2, 3, 4]
[n * 10 for n in nums]              # [10, 20, 30, 40]（map相当）
[n for n in nums if n % 2 == 0]     # [2, 4]（filter相当。if は後ろに付く）</pre>
<p class="task"><b>課題:</b> 内包表記で2つの関数を作ってください。<code>double_all(nums)</code> は各要素を2倍したリスト、<code>long_titles(titles, min_len)</code> は文字数が <code>min_len</code> 以上のものだけのリストを返します（文字数は <code>len(t)</code>）。</p>''',
            "starter": '''def double_all(nums):
    # 内包表記で [各要素の2倍] を返す
    pass


def long_titles(titles, min_len):
    # 内包表記で「len(t) が min_len 以上」だけを残す
    pass
''',
            "hint": "return [n * 2 for n in nums] と return [t for t in titles if len(t) >= min_len] の各1行です。",
            "solution": '''def double_all(nums):
    return [n * 2 for n in nums]


def long_titles(titles, min_len):
    return [t for t in titles if len(t) >= min_len]''',
            "checks": [
                {"kind": "source", "name": "内包表記を使っている", "pattern": "\\[[^\\]]*\\bfor\\b[^\\]]*\\]", "detail": "[式 for 変数 in リスト] の形で書きます"},
                {"kind": "source", "name": ".append を使っていない（内包表記の練習）", "pattern": "\\.append\\s*\\(", "not": True, "detail": "今回は append ではなく内包表記1行で書いてください"},
                {"kind": "eq", "name": "double_all([1, 2, 3])", "expr": "double_all([1, 2, 3])", "want": "[2, 4, 6]"},
                {"kind": "eq", "name": "double_all([])", "expr": "double_all([])", "want": "[]"},
                {"kind": "eq", "name": 'long_titles(["Voyage", "Aurora", "Sky"], 4)', "expr": "long_titles(['Voyage', 'Aurora', 'Sky'], 4)", "want": "['Voyage', 'Aurora']"},
            ],
        },
        {
            "id": "default_args",
            "title": "デフォルト引数と *args / **kwargs",
            "desc": '''<h2>2-5. 引数いろいろ — デフォルト・*args・**kwargs</h2>
<p>引数には3つの便利な形があります。</p>
<pre>def fade(volume, step=10):      # ① デフォルト値。省略すると 10
    ...

def total(*nums):               # ② 何個でも受け取る → nums はタプルになる
    ...                          #    total(1, 2, 3) → nums = (1, 2, 3)

def show(**settings):           # ③ キーワード引数を何個でも → 辞書になる
    ...                          #    show(bpm=120) → settings = {"bpm": 120}</pre>
<p class="task"><b>課題:</b> 3つの関数を作ってください。<br>
① <code>fade(volume, step=10)</code> — volumeからstepを引く。ただし0未満にしない（<code>max(0, …)</code>）<br>
② <code>total(*nums)</code> — 渡された数を全部足す（<code>sum(nums)</code> でOK）<br>
③ <code>show_config(**settings)</code> — <code>"bpm=120, vol=0.8"</code> のようにキー順（<code>sorted</code>）で並べた文字列を返す</p>''',
            "starter": '''def fade(volume, step=10):
    pass


# total(*nums) をここに定義


# show_config(**settings) をここに定義
# ヒント: ", ".join(f"{k}={v}" for k, v in sorted(settings.items()))
''',
            "hint": 'fade は return max(0, volume - step)。total は def total(*nums): return sum(nums)。show_config はヒントの join の1行を return します。',
            "solution": '''def fade(volume, step=10):
    return max(0, volume - step)


def total(*nums):
    return sum(nums)


def show_config(**settings):
    return ", ".join(f"{k}={v}" for k, v in sorted(settings.items()))''',
            "checks": [
                {"kind": "source", "name": "step=10 のデフォルト引数", "pattern": "step\\s*=\\s*10", "detail": "def fade(volume, step=10): と書きます"},
                {"kind": "source", "name": "*nums を使っている", "pattern": "\\*\\s*nums", "detail": "def total(*nums): と書きます"},
                {"kind": "source", "name": "**settings を使っている", "pattern": "\\*\\*\\s*settings", "detail": "def show_config(**settings): と書きます"},
                {"kind": "eq", "name": "fade(80) → 70（step省略）", "expr": "fade(80)", "want": "70"},
                {"kind": "eq", "name": "fade(80, 30) → 50", "expr": "fade(80, 30)", "want": "50"},
                {"kind": "eq", "name": "fade(5) は 0 で止まる", "expr": "fade(5)", "want": "0"},
                {"kind": "eq", "name": "total(1, 2, 3) → 6", "expr": "total(1, 2, 3)", "want": "6"},
                {"kind": "eq", "name": "total() → 0", "expr": "total()", "want": "0"},
                {"kind": "eq", "name": "show_config(bpm=120, vol=0.8)", "expr": "show_config(bpm=120, vol=0.8)", "want": "'bpm=120, vol=0.8'"},
            ],
        },
        {
            "id": "lambda_basics",
            "title": "lambda",
            "desc": '''<h2>2-6. lambda — 1行の無名関数</h2>
<p><code>lambda 引数: 式</code> で、名前を付けずに小さな関数を作れます。JSのアロー関数 <code>x =&gt; x * 2</code> にあたります。<code>return</code> は書かず、式の結果がそのまま返ります。</p>
<pre>double = lambda x: x * 2
double(5)    # → 10</pre>
<p>本領を発揮するのは第3章の <code>sorted(key=...)</code> のように「関数を渡す」場面です。ここでは形に慣れましょう。</p>
<p class="task"><b>課題:</b> lambda で2つの関数を作ってください（<code>def</code> は使わない）。<code>half</code> は半分にする（<code>x / 2</code>）、<code>shout</code> は大文字にして <code>"!"</code> を付ける（<code>s.upper() + "!"</code>）。</p>''',
            "starter": '''# half  … 半分にする lambda（例: half(10) → 5.0）
# shout … 大文字 + "!" にする lambda（例: shout("mix") → "MIX!"）
''',
            "hint": 'half = lambda x: x / 2、shout = lambda s: s.upper() + "!" の2行です。',
            "solution": '''half = lambda x: x / 2
shout = lambda s: s.upper() + "!"''',
            "checks": [
                {"kind": "source", "name": "lambda を使っている", "pattern": "\\blambda\\b", "detail": "half = lambda x: ... の形で書きます"},
                {"kind": "source", "name": "def を使っていない（lambdaの練習）", "pattern": "\\bdef\\b", "not": True, "detail": "今回は def ではなく lambda で書いてください"},
                {"kind": "eq", "name": "half(10) → 5.0", "expr": "half(10)", "want": "5.0"},
                {"kind": "eq", "name": "half(7) → 3.5", "expr": "half(7)", "want": "3.5"},
                {"kind": "eq", "name": 'shout("mix") → "MIX!"', "expr": "shout('mix')", "want": "'MIX!'"},
            ],
        },
    ],
}
