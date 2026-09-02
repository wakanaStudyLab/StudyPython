"""
============================================================================
Python 05: ラムダ式・クロージャ・遅延バインディング (Lambdas & Closures)
============================================================================

【他言語経験者（Rust, C#, Go, Java）向け要点】
1. Python の lambda 式は「単一の式（Expression）」しか書けない:
   - 文（Statement）である代入や if-else、for、raise は書けません。
   - 条件分岐は三項演算子 `val if cond else default` を使用します。

2. PEP 8 の公式ルール:「lambda を変数に代入するな」:
   - `f = lambda x: x * 2` ではなく、素直に `def f(x): return x * 2` と書くのが Pythonic。
   - lambda は `sorted(..., key=lambda ...)` のように「引数に直接インラインで渡す」用途に限定します。

3. 遅延バインディング (Late Binding) の罠:
   - ループ内で lambda を作ると、外側の変数は「参照」としてキャプチャされるため、
     すべての関数がループの最終値を参照してしまいます。
   - 回避策: `lambda i=i: ...` のようにデフォルト引数を使ってその瞬間の値をコピー固定します。

4. 内部構造:
   - クロージャは `__closure__` 属性に `cell` オブジェクトとして環境データを保持します。
"""

from __future__ import annotations
from dataclasses import dataclass
from functools import partial
import operator
from typing import Callable


# ============================================================================
# 1. 基本構文と三項演算子
# ============================================================================
def demo_basic_lambda() -> None:
    print("--- 1. Basic Lambda Syntax & Conditional Expressions ---")

    # 基本: lambda 引数: 式
    # (型ヒント上は Callable[[int, int], int] として扱える)
    add: Callable[[int, int], int] = lambda a, b: a + b
    print(f"Add(10, 20): {add(10, 20)}")

    # 三項演算子を使った条件付き lambda
    classify: Callable[[int], str] = lambda n: "Even" if n % 2 == 0 else "Odd"
    print(f"Classify 42: {classify(42)}")
    print(f"Classify 17: {classify(17)}")


# ============================================================================
# 2. 遅延バインディングの罠 (Late Binding Trap) と解決策
# ============================================================================
def demo_late_binding_trap() -> None:
    print("\n--- 2. Late Binding Trap in Loops & Fix ---")

    # ❌ 罠: すべての lambda がループ完了後の変数 i (最終値 2) を参照してしまう
    buggy_funcs = [lambda: i for i in range(3)]
    results_buggy = [f() for f in buggy_funcs]
    print(f"Buggy closures result (Expected [0, 1, 2]): {results_buggy}")  # [2, 2, 2]

    # ⭕ 解決策1: デフォルト引数 i=i による即時キャプチャ (Early Binding)
    fixed_funcs_default = [lambda i=i: i for i in range(3)]
    results_fixed = [f() for f in fixed_funcs_default]
    print(f"Fixed with default arg (i=i):              {results_fixed}")  # [0, 1, 2]

    # ⭕ 解決策2: functools.partial による引数固定
    def identity(x: int) -> int:
        return x

    fixed_funcs_partial = [partial(identity, i) for i in range(3)]
    print(f"Fixed with functools.partial:             {[f() for f in fixed_funcs_partial]}")


# ============================================================================
# 3. クロージャの内部構造 (__closure__ と cell オブジェクト)
# ============================================================================
def demo_closure_internals() -> None:
    print("\n--- 3. Closure Internals (__closure__ and cell) ---")

    def make_multiplier(factor: int) -> Callable[[int], int]:
        # factor が内側の lambda にキャプチャされる
        return lambda x: x * factor

    triple = make_multiplier(3)
    print(f"Triple 10: {triple(10)}")

    # __closure__ の中身を確認
    if triple.__closure__ is not None:
        captured_cell = triple.__closure__[0]
        print(f"Cell object: {captured_cell}")
        print(f"Captured value in cell: {captured_cell.cell_contents}")  # 3


# ============================================================================
# 4. nonlocal による状態変更クロージャ
# ============================================================================
def demo_nonlocal_counter() -> None:
    print("\n--- 4. Stateful Closure with nonlocal ---")

    def create_counter(start: int = 0) -> Callable[[], int]:
        count = start

        def increment() -> int:
            nonlocal count  # 外側のスコープの count を再代入可能にする
            count += 1
            return count

        return increment

    counter_a = create_counter(0)
    counter_b = create_counter(100)

    print(f"Counter A: {counter_a()}, {counter_a()}, {counter_a()}")  # 1, 2, 3
    print(f"Counter B: {counter_b()}, {counter_b()}")                  # 101, 102


# ============================================================================
# 5. 実務頻出パターン & operator モジュールとの比較
# ============================================================================
@dataclass
class Product:
    category: str
    name: str
    price: int


def demo_practical_sorting_and_operator() -> None:
    print("\n--- 5. Practical Sorting & operator Module ---")

    products = [
        Product("Book", "Python Mastery", 3800),
        Product("Book", "Rust in Action", 4200),
        Product("Device", "Mouse", 2500),
        Product("Device", "Keyboard", 12000),
    ]

    # 1. lambda を使った多段ソート (カテゴリ昇順、価格降順)
    sorted_by_lambda = sorted(products, key=lambda p: (p.category, -p.price))
    print("Sorted by lambda (category asc, price desc):")
    for p in sorted_by_lambda:
        print(f"  {p}")

    # 2. operator.attrgetter の活用 (lambda より高速で Pythonic)
    # 単一キーの場合、C言語実装の attrgetter が推奨される
    sorted_by_op = sorted(products, key=operator.attrgetter("price"))
    print("\nSorted by operator.attrgetter('price'):")
    for p in sorted_by_op:
        print(f"  {p.name}: JPY {p.price}")


def run() -> None:
    demo_basic_lambda()
    demo_late_binding_trap()
    demo_closure_internals()
    demo_nonlocal_counter()
    demo_practical_sorting_and_operator()


if __name__ == "__main__":
    run()
