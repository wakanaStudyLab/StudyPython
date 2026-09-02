# Python ラムダ式 & クロージャ 完全理解ガイド (Python Lambdas & Closures Deep Dive)

Python の **`lambda` 式（無名関数）** と **クロージャ（Closure）** について、構文の基本から「なぜ単一式しか書けないのか？」「ループ変数キャプチャの罠（遅延バインディング）」「バイトコードと `cell` オブジェクトの正体」まで完全解説します。

Rust, C#, Go, Java などの静的型付け言語エンジニアが最も誤解しやすいポイントを論理的に解き明かします。

---

## 📑 目次

1. [Python の `lambda` とは何か？（誕生背景と設計哲学）](#1-python-の-lambda-とは何か誕生背景と設計哲学)
2. [基本構文と厳格な制約（なぜ式しか書けないのか？）](#2-基本構文と厳格な制約なぜ式しか書けないのか)
3. [PEP 8 の推奨ルール：「lambda に名前をつけるな」](#3-pep-8-の推奨ルールlambda-に名前をつけるな)
4. [変数キャプチャの最大の罠：遅延バインディング (Late Binding)](#4-変数キャプチャの最大の罠遅延バインディング-late-binding)
5. [クロージャの内部構造：`__closure__` と `cell` オブジェクト](#5-クロージャの内部構造__closure__-と-cell-オブジェクト)
6. [外側の変数の書き換え：`nonlocal` キーワード](#6-外側の変数の書き換えnonlocal-キーワード)
7. [実務における主要ユースケース](#7-実務における主要ユースケース)
8. [`operator` モジュールとの使い分け（lambda より高速な標準ライブラリ）](#8-operator-モジュールとの使い分けlambda-より高速な標準ライブラリ)
9. [他言語エンジニア向け比較表 (Python vs Java vs C++ vs Rust vs Go)](#9-他言語エンジニア向け比較表-python-vs-java-vs-c-vs-rust-vs-go)
10. [理解度チェッククイズ](#10-理解度チェッククイズ)

---

## 1. Python の `lambda` とは何か？（誕生背景と設計哲学）

### 1-1. 一行の使い捨て関数を作るための構文
Python において関数は「第一級オブジェクト（First-class Object）」です。変数に代入したり、関数の引数に渡したり、戻り値として返すことができます。

通常の関数定義 `def` では名前が必須ですが、`lambda` は **「名前を持たない小さなインライン関数（無名関数）」** をその場で作るために導入されました。

```python
# 通常の def 定義
def square(x):
    return x * x

# lambda 式
square_lambda = lambda x: x * x
```

### 1-2. Python の生みの親（Guido）の思想
Python の作者 Guido van Rossum は、Python を純粋関数型言語（Lisp や Haskell）にするつもりはありませんでした。
そのため、Python の `lambda` は「構文の可読性を損なわない範囲での補助的なショートハンド」として極めてシンプルな仕様に限定されています。

---

## 2. 基本構文と厳格な制約（なぜ式しか書けないのか？）

### 2-1. 基本構文
```python
lambda 引数1, 引数2, ...: 単一の式 (戻り値)
```

- `def` と異なり、**`return` キーワードは書きません**（コロン `:` の右側の評価結果がそのまま戻り値になります）。
- 引数は通常の関数と同様に、デフォルト引数や可変長引数（`*args`, `**kwargs`）も使えます。

```python
# 複数引数
add = lambda a, b: a + b

# デフォルト引数
greet = lambda name, prefix="Hello": f"{prefix}, {name}!"

# 可変長引数
sum_all = lambda *args: sum(args)
```

### 2-2. 厳格な制約：文（Statement）は書けない！
Python の構文規則上、コロン `:` の右側には **「式（Expression）」しか書けず、「文（Statement）」は一切書けません**。

| 書けるもの (式: 値を評価するもの) | 書けないもの (文: 実行単位) |
| :--- | :--- |
| ⭕ 数値計算 `x + 1` | ❌ 代入文 `x = 10` |
| ⭕ 関数呼び出し `print(x)` | ❌ `if-else` 文（※三項条件式ならOK） |
| ⭕ リスト内包表記 `[x*2 for x in xs]` | ❌ `for`, `while` ループ文 |
| ⭕ 三項演算子 `a if cond else b` | ❌ `raise`, `try-except` 文 |
| ⭕ タプルや辞書の生成 `(x, y)` | ❌ `return` キーワード |

#### 条件分岐を書きたい場合は「三項演算子」を使う
```python
# ❌ 文としての if は書けない
bad = lambda x: if x > 0: return "Positive"

# ⭕ 三項演算子 (式) を使う
good = lambda x: "Positive" if x > 0 else "Non-positive"
```

---

## 3. PEP 8 の推奨ルール：「lambda に名前をつけるな」

Python の公式スタイルガイド PEP 8 では、以下のように明確に勧告されています：

> **PEP 8**:  
> Always use a def statement instead of an assignment statement that binds a lambda expression directly to an identifier.  
> （lambda 式を変数に代入して名前をつけるくらいなら、素直に `def` 文を使いなさい）

```python
# ❌ PEP 8 違反 (アンチパターン)
f = lambda x: 2 * x

# ⭕ 正しい Pythonic な書き方
def f(x):
    return 2 * x
```

### なぜ代入するなら `def` なのか？
1. **トレースバック（スタックトレース）の可読性**:  
   エラーが発生した時、`lambda` で作った関数は `<lambda>` と表示され、どの関数で例外が起きたのか特定しづらくなります。`def` なら関数名が正確に表示されます。
2. **型アノテーションと docstring**:  
   `def` なら引数・戻り値の型ヒントやドキュメンテーション文字列が綺麗に書けます。

> **💡 lambda を使うべき唯一の場所**:  
> 変数に代入せず、**`sorted(..., key=lambda ...)` やイベントコールバックなどの「関数の引数にその場でインライン渡しする場面」** だけに使うのが Python の定石です。

---

## 4. 変数キャプチャの最大の罠：遅延バインディング (Late Binding)

Python のクロージャにおいて、**全エンジニア（特に他言語経験者）が必ず一度はハマる最も危険な罠**です。

### 4-1. 事故コード（なぜ全部同じ値になるのか？）
```python
# 0, 1, 2 を返す関数リストを作りたい
functions = [lambda: i for i in range(3)]

# 実行してみる
print([f() for f in functions])
# 予想: [0, 1, 2]
# 実際: [2, 2, 2]  ← なぜ！？
```

### 4-2. 原因：Python の変数は「名前解決（参照）」で行われる
Python のクロージャは、ラムダ式が定義された瞬間の値（0 や 1）をコピー（値キャプチャ）しません。
**「スコープ内の変数名 `i` への参照（ポインタ）」を保持（遅延バインディング：Late Binding）** します。

そのため、ループが回り終わって関数が呼び出された時点では、`i` の最終的な値である `2` がすべてのラムダから参照されてしまいます。

```
[ループ終了時のスコープ]
i = 2 ◄──────────┐
                 ├── functions[0]() が i を見に行く → 2
                 ├── functions[1]() が i を見に行く → 2
                 └── functions[2]() が i を見に行く → 2
```

### 4-3. 解決策 2選

#### 解決策1: デフォルト引数ハック（Python の王道イディオム）★最重要★
Python の関数の**デフォルト引数は「関数定義時（ループのその瞬間）」に評価される**という性質を利用します。

```python
# i=i により、ループ時の各ステップの値が引数のデフォルト値としてコピー固定される
functions = [lambda i=i: i for i in range(3)]

print([f() for f in functions])
# 出力: [0, 1, 2] （大成功！）
```

#### 解決策2: `functools.partial` を使う
```python
from functools import partial

def identity(x):
    return x

functions = [partial(identity, i) for i in range(3)]
print([f() for f in functions]) # [0, 1, 2]
```

---

## 5. クロージャの内部構造：`__closure__` と `cell` オブジェクト

Python の関数が外部スコープの変数をキャプチャした時、内部では何が起きているのでしょうか？

```python
def make_multiplier(factor):
    return lambda x: x * factor

double = make_multiplier(2)
```

このとき、`double` オブジェクトの特殊属性を調査すると、`__closure__` というタプルが存在します：

```python
print(double.__closure__)
# (<cell at 0x...: int object at 0x...>,)

# キャプチャされた中身の値を取り出す
print(double.__closure__[0].cell_contents)
# 2
```

- Python は外部スコープ変数をキャプチャすると、その変数を **`cell` オブジェクト** で包みます。
- `cell` はポインタのラッパーであり、外側の関数と内側のクロージャが同一のメモリ領域を安全に共有できるようにしています。

---

## 6. 外側の変数の書き換え：`nonlocal` キーワード

Python でクロージャ内部から外側のローカル変数を再代入（書き換え）したい場合、**`nonlocal` 宣言** が必要です。

> **※注意**: `lambda` では文が書けないため `nonlocal` は使えません。内部 `def` 関数を使います。

```python
def create_counter():
    count = 0  # 外側のローカル変数
    
    def increment():
        nonlocal count  # これがないと「ローカル変数 count の代入」とみなされ参照エラーになる
        count += 1
        return count
        
    return increment

counter = create_counter()
print(counter()) # 1
print(counter()) # 2
print(counter()) # 3
```

---

## 7. 実務における主要ユースケース

### 7-1. `sorted()` や `list.sort()` の `key` 指定
実務で最も頻出するパターンです。

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    score: float

users = [
    User("Alice", 25, 88.5),
    User("Bob", 20, 95.0),
    User("Charlie", 25, 92.0),
]

# 年齢昇順、同じ年齢ならスコア降順
sorted_users = sorted(users, key=lambda u: (u.age, -u.score))
```

### 7-2. `defaultdict` のファクトリ関数
```python
from collections import defaultdict

# 存在しないキーに対して初期値 100 を与える辞書
scores = defaultdict(lambda: 100)
scores["Alice"] = 90
print(scores["Alice"]) # 90
print(scores["Bob"])   # 100 (デフォルト値)
```

### 7-3. `min()` / `max()` の比較条件
```python
words = ["apple", "banana", "pie", "watermelon"]
longest = max(words, key=lambda w: len(w))
print(longest) # "watermelon"
```

---

## 8. `operator` モジュールとの使い分け（lambda より高速な標準ライブラリ）

Python 標準の `operator` モジュールには、`lambda` よりも**高速（C言語レベルで実装）**かつ可読性の高い関数群が揃っています。

| lambda 記法 | `operator` モジュール推奨記法 | 速度 |
| :--- | :--- | :--- |
| `lambda x: x.name` | `operator.attrgetter("name")` | **約 20% 高速** |
| `lambda x: x["age"]` | `operator.itemgetter("age")` | **約 25% 高速** |
| `lambda a, b: a + b` | `operator.add` | **約 30% 高速** |

```python
from operator import attrgetter

# lambda u: u.age より高速かつクリーン
users.sort(key=attrgetter("age"))
```

---

## 9. 他言語エンジニア向け比較表 (Python vs Java vs C++ vs Rust vs Go)

| 特徴 | Python | Java (21+) | Modern C++ (20+) | Rust | Go |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **記法** | `lambda x: x*2` | `x -> x*2` | `[](auto x){ return x*2; }` | `\|x\| x*2` | `func(x int) int { return x*2 }` |
| **複数行・文** | ❌ **式のみ** | ⭕ ブロック `{}` 可 | ⭕ ブロック `{}` 可 | ⭕ ブロック `{}` 可 | ⭕ ブロック `{}` 可 |
| **キャプチャ機構** | 遅延バインディング (`cell`) | コピー (実質的 final) | 明示 (値/参照/ムーブ) | ムーブ / 借用 | 参照 (エスケープ解析) |
| **ループキャプチャ罠** | ⚠️ **あり** (`i=i`で回避) | なし (コンパイル拒絶) | ⚠️ 参照キャプチャ時 | なし (借用チェッカ) | ⚠️ Go 1.21以前あり (1.22で解消) |
| **オーバーヘッド** | 関数呼び出しコストあり | 初回Bootstrapのみ | **ゼロ (インライン化)** | **ゼロ (インライン化)** | ヒープ退避コストあり |

---

## 10. 理解度チェッククイズ

### Q1. 次のラムダ式のうち、Python の構文エラー（SyntaxError）になるものはどれですか？
- A. `lambda x: x if x > 0 else 0`
- B. `lambda x: print(x)`
- C. `lambda x: total = total + x`
- D. `lambda: 42`

<details>
<summary>▶ 解答と解説</summary>

**正解: C**
C は代入文（Statement）であるため、ラムダ式の中には記述できません。代入文が必要な場合は通常の `def` を使う必要があります。なお、A は三項演算子（式）、B は `print()` 関数呼び出し（戻り値 `None` の式）、D は引数なしの式なのでいずれも有効です。
</details>

### Q2. 以下のコードの出力結果は何になりますか？
```python
actions = [lambda: k * 10 for k in [1, 2, 3]]
print(actions[0]())
```
- A. `10`
- B. `30`
- C. `None`
- D. `NameError`

<details>
<summary>▶ 解答と解説</summary>

**正解: B**
Python のラムダ式は外部変数を遅延バインディングするため、呼び出された瞬間の `k` の最終値（`3`）を参照します。結果は `3 * 10 = 30` となります。`10` を得たい場合は `lambda k=k: k * 10` と書く必要があります。
</details>

---

## まとめ

1. **「lambda は引数渡しのインライン使い捨て」**: 名前を代入するなら素直に `def` を使う（PEP 8）。
2. **「ループ内 lambda は `i=i` で即時固定」**: 遅延バインディングによる意図せぬ共有バグを防ぐ。
3. **「属性やキー取得なら `operator` モジュール」**: `attrgetter` や `itemgetter` を使うことでさらに高速かつ Pythonic になる。
