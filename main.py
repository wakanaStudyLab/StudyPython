"""
============================================================================
Modern Python (Python 3.10+) Crash Course - Main Runner
For Rust / C# / Go / Java Developers
============================================================================
"""

import io
import importlib
import multiprocessing
import sys

# Windows コンソールでの文字化け・エンコードエラー防止 (型絞り込みで Pylance 警告を解消)
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")


def print_banner(title: str) -> None:
    print("\n" + "=" * 64)
    print(f"  {title}")
    print("=" * 64 + "\n")


def print_section(title: str) -> None:
    print("\n" + "#" * 64)
    print(f"# {title}")
    print("#" * 64 + "\n")


def main() -> None:
    # Windows でのマルチプロセス (ProcessPoolExecutor) の安全起動サポート
    multiprocessing.freeze_support()

    print_banner(f"MODERN PYTHON CRASH COURSE (Running on Python {sys.version.split()[0]})")

    # 各モジュールの読み込みと実行
    types_mod = importlib.import_module("01_types_and_dataclasses")
    print_section("01: Type Hints, Dataclasses, and Reference Model")
    types_mod.run()

    pattern_mod = importlib.import_module("02_pattern_matching_and_control")
    print_section("02: Pattern Matching, Comprehensions, and Generators")
    pattern_mod.run()

    context_mod = importlib.import_module("03_context_and_decorators")
    print_section("03: Context Managers, Decorators, and Dunder Methods")
    context_mod.run()

    async_mod = importlib.import_module("04_async_and_concurrency")
    print_section("04: Async/Await (asyncio TaskGroup) and Concurrency")
    async_mod.run()

    print_banner("ALL PYTHON TUTORIAL MODULES COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
