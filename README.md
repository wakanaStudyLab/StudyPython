# Modern Python Crash Course (For Rust, C#, Go, Java Developers)

Rust, C#, Go, Java などの静的型付け言語を習得済みのエンジニアが、**最短でモダンPython（Python 3.10+ / 3.11+ / 3.12+ / 3.14）をマスターするための実践リファレンス**です。

---

## 🚀 クイックスタート (実行方法)

```powershell
cd C:\Users\harun\programming\python\sample

# 実行
python main.py

# または付属スクリプトで実行
.\run.ps1
```

---

## 🗺️ 言語対比マッピング早見表 (Python vs Rust vs C# vs Go vs Java)

| 概念・機能 | Modern Python (3.10+) | Rust | C# | Go | Java |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **型アノテーション** | `x: int = 10` | `let x: i32 = 10;` | `int x = 10;` | `var x int = 10` | `int x = 10;` |
| **Nullable / Optional** | `str \| None` | `Option<String>` | `string?` | `*string` / `nil` | `Optional<String>` |
| **不変データ構造** | `@dataclass(frozen=True)`| `struct User` | `record User(...)` | `type User struct` | `record User(...)` |
| **値の同値性比較** | `a == b` (`__eq__`) | `a == b` | `a.Equals(b)` / `==` | `a == b` | `a.equals(b)` |
| **参照の一致比較** | `a is b` (ポインタ比較) | `std::ptr::eq` | `ReferenceEquals` | ポインタ比較 | `a == b` |
| **代数的データ型 (ADT)** | `TypeA \| TypeB` | `enum Name { A, B }`| `abstract record` | `interface` | `sealed interface` |
| **パターンマッチング** | `match val: case ...:` | `match val { ... }` | `val switch { ... }` | `switch val.(type)` | `switch (val) { case ... }` |
| **コレクション操作** | 内包表記 `[x for x in ...]` | `.iter().filter().map()` | LINQ `.Where().Select()` | slices / ループ | Stream `.filter().map()` |
| **リソース自動解放** | `with obj as f:` | `Drop` トレイト | `using (var f = ...)` | `defer f.Close()` | `try (var f = ...) { ... }` |
| **メタプログラミング** | **デコレータ** (`@deco`) | マクロ / トレイト | 属性 (Attribute) + AOP | ミドルウェア関数 | アノテーション + AOP |
| **非同期 Promise** | `async def` / `await` | `tokio async` | `async` / `await` | goroutine + channel | `CompletableFuture` / Virtual Threads |
| **構造化並行性** | `asyncio.TaskGroup` | `tokio::task::JoinSet` | `Task.WhenAll` | `errgroup.Group` | `StructuredTaskScope` |

---

## ⚠️ 他言語経験者が最もハマる Python の「罠」と作法

### 1. デフォルト引数に可変オブジェクト（リストや辞書）を渡してはいけない
- **理由**: Pythonのデフォルト引数は「関数定義時」に1度だけ評価され、ヒープ上にメモリが確保されます。
- そのため、すべての関数呼び出しで **同じリストの参照が共有** されてしまいます。
  ```python
  # ❌ 絶対にやってはいけない
  def append_to(element, target_list=[]):
      target_list.append(element)
      return target_list

  # ⭕ 正しいイディオム
  def append_to(element, target_list: list | None = None):
      if target_list is None:
          target_list = []
      target_list.append(element)
      return target_list
  ```

### 2. `None` の比較は必ず `is None` を使う
- `==` は `__eq__` 特殊メソッドを呼び出すため、カスタムクラスが `__eq__` を誤ってオーバーライドしている場合にバグになります。
- `is` は「同一のメモリ領域（ポインタ）を指しているか」を直接判定するため、最速かつ安全です。

### 3. GIL (Global Interpreter Lock) によるマルチスレッドの制約
- CPythonでは1プロセス内で同時に1つのスレッドしかPythonバイトコードを実行できません。
- **I/O待ち（Web API, DB, ファイル）**: `asyncio`（シングルスレッド非同期）が最も高速・省メモリ。
- **CPU計算（重い数値計算・画像処理）**: `threading` ではなく `multiprocessing` / `ProcessPoolExecutor` を使用してマルチコアを活用する。

### 4. すべての変数は「参照（ヒープへのポインタ）」
- `list2 = list1` と書くと、ポインタがコピーされるだけで同じリストを参照します。
- 独立したコピーを作りたい場合は `list2 = list1.copy()` または `copy.deepcopy()` を使います。

---

## 📁 提供サンプルコードの解説

| ファイル | テーマ | 主な学習内容 |
| :--- | :--- | :--- |
| [`01_types_and_dataclasses.py`](file:///C:/Users/harun/programming/python/sample/01_types_and_dataclasses.py) | **型ヒント & Dataclass** | `int \| str` (Union), `@dataclass(frozen=True)`, `is` vs `==`, 可変デフォルト引数の罠 |
| [`02_pattern_matching_and_control.py`](file:///C:/Users/harun/programming/python/sample/02_pattern_matching_and_control.py) | **パターンマッチング & 内包表記** | Python 3.10+ `match ... case`, ガード節 `if`, リスト/辞書内包表記, `yield` ジェネレータ, `:=` (Walrus) |
| [`03_context_and_decorators.py`](file:///C:/Users/harun/programming/python/sample/03_context_and_decorators.py) | **with文 & デコレータ** | `__enter__` / `__exit__`, `@contextmanager`, `@timeit` デコレータ, `functools.wraps`, Dunderメソッド |
| [`04_async_and_concurrency.py`](file:///C:/Users/harun/programming/python/sample/04_async_and_concurrency.py) | **並行・非同期・GIL対策** | Python 3.11+ `asyncio.TaskGroup` (構造化並行性), `ThreadPoolExecutor` vs `ProcessPoolExecutor` (GIL回避) |
| [`05_lambdas_and_closures.py`](file:///C:/Users/harun/programming/python/sample/05_lambdas_and_closures.py) | **ラムダ式 & クロージャ** | 単一式の制約、遅延バインディングの罠 (`i=i`), `__closure__` / cell, `nonlocal`, `operator` モジュール |
| [`main.py`](file:///C:/Users/harun/programming/python/sample/main.py) | **統合エントリーポイント** | 全モジュールを一括実行するランナー |

> 📖 **Python ラムダ式 & クロージャの完全理解ガイド**:  
> なぜ代入してはいけないのか（PEP 8）、ループ変数キャプチャの落とし穴と解決策、バイトコードレベルの `cell` オブジェクトの仕組みまで完全網羅した解説は [**`LAMBDA.md`**](file:///C:/Users/harun/programming/python/sample/LAMBDA.md) を参照してください。

---

## 🛠️ モダン Python のパッケージマネージャー: `uv` (Rust製・超高速)

現在、Pythonエコシステムでは従来の `pip` や `poetry` に代わり、Rustで開発された爆速ツール **`uv`** がデファクトスタンダードになりつつあります（本マシンにもインストール済み）。

```bash
# プロジェクトの初期化
uv init my_project

# 依存パッケージの高速追加 (pip install の数百倍高速)
uv add fastapi uvicorn

# 仮想環境内でスクリプトを実行
uv run python main.py
```

---

## ⚙️ VS Code での Python 開発設定ガイド (`launch.json` & `settings.json`)

VS Code で Python コードを快適に「実行」「F5 デバッグ」「型チェック」「コード補完」するための設定マニュアルです。

---

### 1. `launch.json` の書き方とプロパティ解説 (デバッグ起動設定)

`.vscode/launch.json` は、VS Code の「実行とデバッグ」パネル（`Ctrl + Shift + D`）や **`F5`** キーを押したときのデバッグ動作を定義するファイルです。

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            // ① 【デフォルト】現在アクティブに開いているタブの Python ファイルを単体実行
            // (01_... や 02_... を開いて F5 を押すとそのファイルだけが即座に動きます)
            "name": "▶ Python: Current File",
            "type": "debugpy",                 // 最新の標準デバッガー
            "request": "launch",
            "program": "${file}",              // 現在開いているファイル
            "console": "integratedTerminal",   // 統合ターミナル (input() 受付可能)
            "cwd": "${fileDirname}",           // 開いているファイルのディレクトリで実行
            "justMyCode": true                 // true: 自分のコードのみ停止
        },
        {
            // ② 統合ランナー (main.py) を実行して全モジュールを一括検証
            "name": "▶ Python: Run main.py (All Modules)",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "justMyCode": true
        },
        {
            // ③ 標準ライブラリやサードパーティ製ライブラリの内部までステップイン
            "name": "▶ Python: Current File (Deep Step-In)",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${fileDirname}",
            "justMyCode": false                // false: ライブラリの中まで F11 で入る
        },
        {
            // ④ コマンドライン引数 (sys.argv) や環境変数を渡す構成例
            "name": "▶ Python: Run with Args & Env",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "args": ["--mode", "fast", "--count", "5"], // 引数
            "env": {                                     // 環境変数
                "PYTHONUTF8": "1",
                "ENV_MODE": "development"
            },
            // "envFile": "${workspaceFolder}/.env",
            "justMyCode": true
        }
    ]
}
```

#### 🔑 主要プロパティ一覧表

| プロパティ | 役割 | 指定例 / 選択肢 |
| :--- | :--- | :--- |
| `type` | デバッガーの種類 | `"debugpy"` (必須・最新標準) |
| `request` | 実行モード | `"launch"` (起動してデバッグ) / `"attach"` (外部プロセス接続) |
| `program` | 実行するファイル | `${workspaceFolder}/main.py` (固定) / `${file}` (現在開いているファイル) |
| `args` | コマンドライン引数 | `["--host", "0.0.0.0", "--port", "8000"]` |
| `env` | 環境変数の設定 | `{"PYTHONUTF8": "1", "DEBUG": "True"}` |
| `envFile` | 環境変数ファイルのパス | `"${workspaceFolder}/.env"` |
| `console` | 出力先コンソール | `"integratedTerminal"` (標準) / `"internalConsole"` (デバッグコンソール) |
| `justMyCode` | 外部ライブラリへの侵入可否 | `true` (自分のコードのみ) / `false` (標準ライブラリ内部もステップイン) |
| `cwd` | 作業ディレクトリ | `"${workspaceFolder}"` (プロジェクトルート) / `"${fileDirname}"` |

---

### 2. `settings.json` の書き方とプロパティ解説 (ワークスペース設定)

`.vscode/settings.json` は、型チェック（Pyright/Pylance）、自動補完、保存時フォーマットなどをプロジェクト単位で制御するファイルです。

```json
{
    // =========================================================================
    // 1. 静的型チェック (Pylance / Pyright)
    // =========================================================================
    // 型チェックの厳格度 ("off" / "basic" / "standard" / "strict")
    // Rust / C# / Go / Java 経験者には "basic" または "standard" が最適
    "python.analysis.typeCheckingMode": "basic",

    // モジュールを打ったときに自動で 'import ...' を挿入する
    "python.analysis.autoImportCompletions": true,

    // 未使用のインポートを薄暗く表示
    "python.analysis.diagnosticSeverityOverrides": {
        "reportUnusedImport": "warning",
        "reportUnusedVariable": "information"
    },

    // =========================================================================
    // 2. Python インタープリター (仮想環境) の指定
    // =========================================================================
    // プロジェクトローカルの仮想環境 (.venv) を自動認識させる
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",

    // =========================================================================
    // 3. ファイルエンコーディング & 保存時アクション
    // =========================================================================
    "files.encoding": "utf8",
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true
}
```

#### 🔑 型チェックモード (`typeCheckingMode`) の違い

* **`"off"`**: 型ヒントの構文エラーのみ通知（型不一致は無視）。
* **`"basic"`** (推奨): 明らかな型の不一致（`int` に `str` を渡すなど）を警告。適度な柔軟性。
* **`"standard"`**: より厳格な型推論チェック。
* **`"strict"`**: Rustのコンパイラ並みにすべての変数・関数に完全な型アノテーションを要求（`Any` を許容しない）。

