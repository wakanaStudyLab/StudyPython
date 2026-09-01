"""
============================================================================
Python 01: モダン型ヒント・Dataclass・参照モデル (Types & Dataclasses)
============================================================================

【他言語経験者（Rust, C#, Go, Java）向け要点】
1. 動的型付け言語だが、現代Pythonは「Type Hints (型アノテーション)」が実務標準:
   - 実行時オーバーヘッドはゼロ（型ヒントは実行時には無視される）。
   - VS Code / Pyright / mypy などの静的解析ツールと組み合わせることで、
     RustやC#と同等の型安全性とIDE補完を得られます。
   - Python 3.10+ では `int | str` (Union) や `list[int]` (組込みジェネリクス) が標準構文。

2. 変数とメモリの参照モデル（全変数はポインタ）:
   - Pythonの変数はすべて「ヒープ上にあるオブジェクトへのポインタ（参照）」。
   - プリミティブ型（int, float, str, tuple）は「不変（Immutable）」。
   - コレクション型（list, dict, set）は「可変（Mutable）」。

3. `is` (同一性) vs `==` (同値性):
   - `a == b`: オブジェクトの中身（値）を比較（`__eq__` メソッドの呼び出し）。
   - `a is b`: メモリ上のアドレス（ポインタ）が同一かを比較（C/C++の `&a == &b`）。
   - 【重要作法】`None` の比較は必ず `x is None` または `x is not None` と書く（`== None` はアンチパターン）。

4. `@dataclass` (Python 3.7+):
   - C#の `record`、Javaの `record`、Rustの `struct` に相当。
   - `__init__`, `__repr__`, `__eq__` などを自動生成。
   - `frozen=True` を指定するとイミュータブル（不変）になり、ハッシュ可能になります。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any


# ============================================================================
# 1. モダン型ヒントの基本構文 (Python 3.10+)
# ============================================================================
def greet(name: str, age: int | None = None) -> str:
    """
    age は int または None (C#の int?, Rustの Option<i32>, Javaの Optional<Integer>)
    """
    if age is not None:
        return f"Hello, {name}! You are {age} years old."
    return f"Hello, {name}!"


def process_items(tags: list[str], config: dict[str, Any]) -> tuple[int, bool]:
    count = len(tags)
    is_active = bool(config.get("active", False))
    return count, is_active


# ============================================================================
# 2. @dataclass (不変データ構造 & バリデーション)
# ============================================================================
@dataclass(frozen=True)  # frozen=True でイミュータブル化 (Rustのデフォルト不変 / C# record / Java record 相当)
class User:
    id: str
    name: str
    age: int
    tags: list[str] = field(default_factory=list)  # 可変デフォルト引数は default_factory を使うのが鉄則

    def is_adult(self) -> bool:
        return self.age >= 18


# ============================================================================
# 3. 他言語経験者が最も引っかかる「デフォルト引数の参照共有の罠」
# ============================================================================
def dangerous_append(item: str, target_list: list[str] = []) -> list[str]:
    """❌ アンチパターン: デフォルト引数に可変オブジェクト (list/dict) を指定すると、
    関数定義時に一度だけ作成されたリストが全呼び出しで共有されてしまう！
    """
    target_list.append(item)
    return target_list


def safe_append(item: str, target_list: list[str] | None = None) -> list[str]:
    """⭕ 推奨イディオム: デフォルト値は None にして内部で新規インスタンス化する"""
    if target_list is None:
        target_list = []
    target_list.append(item)
    return target_list


def run() -> None:
    print("--- 1. Type Hints and f-strings ---")
    print(greet("Alice", 28))
    print(greet("Bob"))

    print("\n--- 2. is (Identity) vs == (Equality) ---")
    list1: list[int] = [1, 2, 3]
    list2: list[int] = [1, 2, 3]
    print(f"list1 == list2 (Value Comparison):    {list1 == list2}")  # True
    print(f"list1 is list2 (Pointer Comparison):  {list1 is list2}")  # False (別メモリ領域)

    none_val: str | None = None
    print(f"none_val is None: {none_val is None}")  # 推奨判定法

    print("\n--- 3. @dataclass (Immutable Data Carrier) ---")
    u1 = User("u001", "Alice", 25, ["admin", "dev"])
    u2 = User("u001", "Alice", 25, ["admin", "dev"])
    print(f"User: {u1}")
    print(f"u1 == u2 (Auto-generated Equality): {u1 == u2}")
    print(f"is_adult(): {u1.is_adult()}")
    # u1.age = 26  # frozen=True のため FrozenInstanceError (変更不可)

    print("\n--- 4. Mutable Default Argument Trap ---")
    # dangerous_append を2回呼ぶと、前回追加した要素が残ってしまう！
    print(f"dangerous call 1: {dangerous_append('A')}")  # ['A']
    print(f"dangerous call 2: {dangerous_append('B')}")  # ['A', 'B'] ❌ 意図しない共有

    # safe_append は安全
    print(f"safe call 1: {safe_append('A')}")  # ['A']
    print(f"safe call 2: {safe_append('B')}")  # ['B'] ⭕ 独立している


if __name__ == "__main__":
    run()
