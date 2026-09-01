"""
============================================================================
Python 02: パターンマッチング・内包表記・ジェネレータ (Pattern Matching & Streams)
============================================================================

【他言語経験者（Rust, C#, Go, Java）向け要点】
1. 構造的パターンマッチング (`match ... case` - Python 3.10+):
   - Rustの `match`、C#の `switch` 式、Javaの `switch` パターンマッチングに相当。
   - 単なる値の分岐だけでなく、**データ構造の分解代入（Destructuring）** と **ガード節 (if)** が可能。
   - クラスの属性分解 `case User(name=n, age=a) if a >= 18:`
   - シーケンスの分解 `case [first, *rest]:` (Rustの `[head, tail @ ..]`)
   - 辞書のキー構造分解 `case {"type": "command", "action": act}:`

2. 内包表記 (Comprehensions):
   - C#の LINQ (`.Where().Select()`)、Rustの Iterator (`.filter().map()`) を
     Pythonで最も高速かつ慣用的に書く記法。
   - リスト内包表記 `[expr for x in iterable if condition]`
   - 辞書内包表記 `{k: v for ...}` / 集合内包表記 `{x for ...}`

3. ジェネレータ (`yield` / ジェネレータ式):
   - すべての要素を一度にメモリに確保せず、「1要素ずつ遅延生成（Lazy Evaluation）」する。
   - C#の `yield return`、Rustの `Iterator`、Javaの `Stream` と同様のメモリ効率。

4. セイウチ演算子 `:=` (Walrus Operator - Python 3.8+):
   - 式の中で代入と評価を同時に行う（Goの `if val, ok := map[key]; ok { ... }` 相当）。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Generator, Any, TypedDict


# ============================================================================
# 1. 構造的パターンマッチングの定義
# ============================================================================
@dataclass
class CreditCard:
    number: str
    holder: str

@dataclass
class BankTransfer:
    account: str
    bank_code: str

@dataclass
class Crypto:
    address: str
    chain: str

Payment = CreditCard | BankTransfer | Crypto  # 型エイリアス (代数的データ型)


# 内包表記用の型定義 (TypedDict: 辞書の各キーの型を静的型チェッカーに教える)
class ProductDict(TypedDict):
    name: str
    category: str
    price: int
    stock: int


def process_payment(payment: Payment) -> str:
    """Rustの match や Java/C#の switch パターンマッチングと同等の網羅分岐"""
    match payment:
        case CreditCard(number=num, holder=h):
            masked = f"****-****-****-{num[-4:]}"
            return f"CreditCard [{h} / {masked}]"

        case BankTransfer(account=acc, bank_code=code):
            return f"BankTransfer [Bank: {code}, Acc: {acc}]"

        # ガード節 (if) による追加条件フィルタ
        case Crypto(address=addr, chain="Ethereum"):
            return f"Ethereum Transfer to: {addr}"

        case Crypto(address=addr, chain=chain):
            return f"Other Crypto ({chain}) to: {addr}"

        case _:  # ワイルドカード (default / fallback)
            raise ValueError(f"Unknown payment type: {payment}")


def parse_command(tokens: list[str]) -> str:
    """シーケンス (リスト) のパターンマッチング"""
    match tokens:
        case ["quit" | "exit"]:
            return "Command: Shutting down..."
        case ["load", filename]:
            return f"Command: Loading file '{filename}'"
        case ["set", key, value]:
            return f"Command: Setting {key} = {value}"
        case ["batch", *commands]:  # 残りの要素をリストとしてキャプチャ
            return f"Command: Batch executing {len(commands)} commands: {commands}"
        case _:
            return f"Command: Unknown syntax: {tokens}"


# ============================================================================
# 2. ジェネレータ (遅延評価ストリーム)
# ============================================================================
def fibonacci(limit: int) -> Generator[int, None, None]:
    """メモリを消費せずに無限または大量の数列を遅延生成 (C# yield return 相当)"""
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1


def run() -> None:
    print("--- 1. Structural Pattern Matching (match ... case) ---")
    payments: list[Payment] = [
        CreditCard("1234-5678-9012-3456", "Alice"),
        Crypto("0x1234abcd5678", "Ethereum"),
        Crypto("bc1qxy2kgdygjrsqtz", "Bitcoin"),
    ]
    for p in payments:
        print("  " + process_payment(p))

    print("\n--- 2. Sequence Destructuring ---")
    print("  " + parse_command(["load", "config.yaml"]))
    print("  " + parse_command(["batch", "clean", "build", "test"]))

    print("\n--- 3. Comprehensions (LINQ / Rust Iterator Equivalent) ---")
    # TypedDict を型注釈することで、Mypy / Pylance が各要素の型 (str, int) を正確に認識する
    products: list[ProductDict] = [
        {"name": "MacBook Pro", "category": "Electronics", "price": 250000, "stock": 5},
        {"name": "Mechanical Keyboard", "category": "Electronics", "price": 18000, "stock": 0},
        {"name": "Rust in Action", "category": "Books", "price": 4200, "stock": 8},
        {"name": "Clean Code", "category": "Books", "price": 3800, "stock": 12},
    ]

    # リスト内包表記: 在庫あり Books の商品名を大文字にして取得 (C# .Where().Select())
    available_books: list[str] = [
        p["name"].upper()
        for p in products
        if p["category"] == "Books" and p["stock"] > 0
    ]
    print(f"Available Books: {available_books}")

    # 辞書内包表記: 商品名 -> 価格 のマップを作成
    price_map: dict[str, int] = {p["name"]: p["price"] for p in products if p["stock"] > 0}
    print(f"In-Stock Price Map: {price_map}")

    print("\n--- 4. Generators and Lazy Evaluation (yield) ---")
    fib_gen = fibonacci(8)
    print("Fibonacci (first 8 numbers):", list(fib_gen))

    # ジェネレータ式: メモリを確保せずに合計を計算 (sum の中で内包表記の [] を外すとジェネレータになる)
    total_inventory_value: int = sum(p["price"] * p["stock"] for p in products)
    print(f"Total Inventory Value: JPY {total_inventory_value:,}")

    print("\n--- 5. Walrus Operator (:=) ---")
    sample_text = "Python modern features are powerful"
    if (n := len(sample_text)) > 20:
        print(f"Text is long ({n} characters): '{sample_text[:20]}...'")


if __name__ == "__main__":
    run()
