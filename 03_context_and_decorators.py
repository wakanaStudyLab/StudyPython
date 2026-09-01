"""
============================================================================
Python 03: コンテキストマネージャ・デコレータ・特殊メソッド (Context, Decorators, Dunder)
============================================================================

【他言語経験者（Rust, C#, Go, Java）向け要点】
1. コンテキストマネージャ (`with` 文):
   - C#の `using`、Javaの `try-with-resources`、Goの `defer Close()`、Rustの `Drop` に相当。
   - ブロック開始時に `__enter__` が実行され、ブロック脱出時に例外発生有無にかかわらず `__exit__` が実行される。
   - `contextlib.contextmanager` を使えば、クラスを書かずに `yield` を使った関数で簡単に作れる。

2. デコレータ (`@decorator`):
   - 高階関数（関数を受け取って新しい関数を返す関数）のシンタックスシュガー。
   - C#の「属性 (Attribute) + AOP」や、Goのミドルウェアパターン `func(http.Handler) http.Handler` に相当。
   - ロギング、実行時間計測、認証チェック、キャッシュ (lru_cache) 等の実装基盤。
   - `functools.wraps` を付けることで、元の関数のメタデータ（名前やdocstring）を維持するのが必須作法。

3. 特殊メソッド (Dunder / Double Underscore Methods):
   - Pythonのオブジェクトモデルのフック（C++の演算子オーバーロードやRustのTrait実装に相当）。
   - `__repr__`: 開発者用文字列表現 (Rustの `Debug` / C#の `ToString()`)
   - `__len__`: `len(obj)` 呼び出し時に実行される
   - `__getitem__`: `obj[key]` の添字アクセスを可能にする
"""

from __future__ import annotations
import time
import functools
import types
from contextlib import contextmanager
from typing import Callable, Any, Generator


# ============================================================================
# 1. コンテキストマネージャの実装
# ============================================================================
# アプローチ A: クラスとして実装 (__enter__ / __exit__)
class DatabaseSession:
    def __init__(self, session_id: str):
        self.session_id = session_id

    def __enter__(self) -> DatabaseSession:
        print(f"  [DB] Connection established (__enter__): {self.session_id}")
        return self  # 'with ... as session' の session に渡されるオブジェクト

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        print(f"  [DB] Connection closed (__exit__): {self.session_id}")
        # None を返す (または何も return しない) ことで、ブロック内の例外を握りつぶさず正常に上位へ伝播させる
        # (※ True を返すと例外を握りつぶして抑制する動作になります)

    def query(self, sql: str) -> None:
        print(f"  [DB] Executing query ({self.session_id}): {sql}")


# アプローチ B: @contextmanager デコレータによる軽量実装
@contextmanager
def temporary_timer(label: str) -> Generator[None, None, None]:
    start = time.perf_counter()
    print(f"  > [{label}] Timer started")
    try:
        yield  # with ブロックの処理がここで実行される
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        print(f"  < [{label}] Timer finished: {elapsed:.2f} ms")


# ============================================================================
# 2. デコレータの実装
# ============================================================================
def timeit(func: Callable[..., Any]) -> Callable[..., Any]:
    """関数の実行時間を計測して出力するデコレータ"""
    @functools.wraps(func)  # 元の関数名やシグネチャを保持するために必須
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"  [@timeit] {func.__name__} execution time: {elapsed:.2f} ms")
        return result
    return wrapper


@timeit
def heavy_computation(n: int) -> int:
    """重い計算を行う関数"""
    total = sum(i * i for i in range(n))
    return total


# ============================================================================
# 3. 特殊メソッド (Dunder Methods) によるカスタムコレクション
# ============================================================================
class CustomDataset:
    def __init__(self, data: list[str]):
        self._data = list(data)

    def __len__(self) -> int:
        """len(dataset) で呼ばれる"""
        return len(self._data)

    def __getitem__(self, index: int) -> str:
        """dataset[0] や dataset[-1] で呼ばれる"""
        return self._data[index]

    def __repr__(self) -> str:
        """デバッグ出力用の文字列表現 (Rustの {:?})"""
        return f"CustomDataset(size={len(self._data)}, items={self._data})"


def run() -> None:
    print("--- 1. Context Manager (with statement / AutoCloseable) ---")
    with DatabaseSession("conn-pg-001") as session:
        session.query("SELECT * FROM orders")
    print("  Exited with-block (Cleaned up successfully)")

    print("\n--- 2. Lightweight Timer via @contextmanager ---")
    with temporary_timer("Heavy Loop"):
        _ = sum(x for x in range(500_000))

    print("\n--- 3. @timeit Decorator Behavior ---")
    res = heavy_computation(300_000)
    print(f"  Computation result: {res}")

    print("\n--- 4. Object Behavior via Dunder Methods ---")
    dataset = CustomDataset(["Python", "Rust", "Go", "C#", "C++"])
    print(f"  Dataset repr: {dataset}")
    print(f"  len(dataset): {len(dataset)}")
    print(f"  dataset[1]:   {dataset[1]}")
    print(f"  dataset[-1] (Negative indexing): {dataset[-1]}")


if __name__ == "__main__":
    run()
