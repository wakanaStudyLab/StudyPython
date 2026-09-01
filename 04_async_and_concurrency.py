"""
============================================================================
Python 04: 並行・非同期・GILとTaskGroup (Concurrency & Asyncio)
============================================================================

【他言語経験者（Rust, C#, Go, Java）向け要点】
1. GIL (Global Interpreter Lock) の本質:
   - CPythonのメモリ管理（参照カウント）の安全性のため、1プロセス内で同時に
     1つのネイティブスレッドしかPythonバイトコードを実行できません。
   - 【使い分けの鉄則】:
     ① **I/Oバウンド（API通信、DB、ファイル）**: `asyncio` または `threading` / `ThreadPoolExecutor` が最適。
     ② **CPUバウンド（重い数値計算、画像処理）**: `multiprocessing` / `ProcessPoolExecutor` でマルチプロセス化してGILを完全回避。

2. `asyncio` と `async / await` (Python 3.5+):
   - C#の `async/await`、JSの `async/await`、Rustの `tokio` と同じシングルスレッド・イベントループ駆動モデル。
   - スレッド切り替えのオーバーヘッドがなく、数万の同時接続を省メモリで処理可能。

3. `asyncio.TaskGroup` (Python 3.11+ / 構造化並行性 Structured Concurrency):
   - Java 21 や Go の errgroup と同様に、「グループ内の1タスクが失敗したら、
     他のタスクも自動的にキャンセルして安全に例外を集約する」現代の標準イディオム。
   - 従来の `asyncio.gather()` よりも例外安全性が大幅に向上。
"""

from __future__ import annotations
import asyncio
import multiprocessing
import time
from typing import Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# ============================================================================
# 1. asyncio による非同期 I/O タスク
# ============================================================================
async def fetch_user_data(user_id: int) -> dict[str, Any]:
    print(f"  > [Fetch User {user_id}] Request started (Waiting for I/O)...")
    await asyncio.sleep(0.05)  # 非同期I/O（ネットワーク遅延）のシミュレーション
    print(f"  < [Fetch User {user_id}] Response received")
    return {"id": user_id, "name": f"User_{user_id}", "status": "active"}


async def fetch_order_data(user_id: int) -> list[str]:
    print(f"  > [Fetch Orders {user_id}] Request started (Waiting for I/O)...")
    await asyncio.sleep(0.08)
    print(f"  < [Fetch Orders {user_id}] Response received")
    return [f"Order_A_{user_id}", f"Order_B_{user_id}"]


async def demonstrate_task_group() -> None:
    print("--- 1. Structured Concurrency with asyncio.TaskGroup (Python 3.11+) ---")
    start = time.perf_counter()

    # TaskGroup を使うと、全タスクの完了を 'with' 脱出時に自動保証
    user_data: dict[str, Any] = {}
    orders: list[str] = []

    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_user_data(101))
        task2 = tg.create_task(fetch_order_data(101))
        task3 = tg.create_task(fetch_user_data(102))

    # ここに到達した時点で全タスクが完了済み
    user_data = task1.result()
    orders = task2.result()

    elapsed = (time.perf_counter() - start) * 1000
    print(f"  All tasks completed in: {elapsed:.2f} ms (executed concurrently)")
    print(f"  Fetched: User={user_data['name']}, Orders={orders}")


# ============================================================================
# 2. CPUバウンドなタスクと ProcessPoolExecutor (GIL回避)
# ============================================================================
def cpu_heavy_work(n: int) -> int:
    """GILの影響を受ける純粋なCPU計算"""
    return sum(i * i for i in range(n))


def demonstrate_executors() -> None:
    print("\n--- 2. ThreadPoolExecutor vs ProcessPoolExecutor (GIL Workarounds) ---")
    inputs = [2_000_000, 2_000_000, 2_000_000, 2_000_000]

    # I/OバウンドやC拡張（NumPy等）に向くスレッドプール
    with ThreadPoolExecutor(max_workers=4) as executor:
        start = time.perf_counter()
        results_thread = list(executor.map(cpu_heavy_work, inputs))
        elapsed_thread = (time.perf_counter() - start) * 1000
        print(f"  ThreadPool (Subject to GIL): {elapsed_thread:.2f} ms")

    # CPUバウンドでマルチコアを100%活用するプロセスプール
    with ProcessPoolExecutor(max_workers=4) as executor:
        start = time.perf_counter()
        results_process = list(executor.map(cpu_heavy_work, inputs))
        elapsed_process = (time.perf_counter() - start) * 1000
        print(f"  ProcessPool (Bypasses GIL / Multi-process): {elapsed_process:.2f} ms")


def run() -> None:
    # イベントループの起動 (エントリーポイント)
    asyncio.run(demonstrate_task_group())
    demonstrate_executors()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    run()
