# 未完了修正 実装計画

作成日: 2026-03-26
状態: 実装完了
対象: `MANUAL-0006` 〜 `MANUAL-0009`

## 目的

`docs/review` 統合後に残っている 4 件の未完了項目を、今回は「方針決定で閉じる」のではなく、実装とテスト追加で解消する。

前提は次のとおりである。

- `MANUAL-0007` と `MANUAL-0008` は、間接カバーで済ませず個別テストを追加する
- `MANUAL-0009` は、教育用デモ扱いで除外せず `argparse` 版 CLI の個別テストを追加する
- `MANUAL-0006` は、`BiopythonDeprecationWarning` を受容せず解消する

## 対象項目

- `MANUAL-0006` [tests/ch10/test_error_handling.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch10/test_error_handling.py)
- `MANUAL-0007` [scripts/ch05/mylib/core.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/core.py)
- `MANUAL-0008` [scripts/ch05/mylib/utils.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/utils.py)
- `MANUAL-0009` [scripts/ch11/cli_argparse.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch11/cli_argparse.py)

## 実装方針

### 1. `BiopythonDeprecationWarning` の解消

対象:
- [error_handling.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch10/error_handling.py)
- [test_error_handling.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch10/test_error_handling.py)

現状:
- `validate_fasta()` は `SeqIO.parse(..., "fasta")` を直接呼んでいる
- `test_no_sequences` の入力 `"this is not a fasta file\n"` は、Biopython 側では「先頭コメント」と解釈され、将来 `ValueError` 化予定の `BiopythonDeprecationWarning` を出す

修正案:
- `SeqIO.parse()` を呼ぶ前に、FASTA として最低限必要な構造を先に検証する
- 具体的には「空でない先頭実質行が `>` で始まるか」を確認し、満たさなければ `ValueError("配列が含まれていません")` を自前で送出する
- これにより、Biopython の deprecated なコメント解釈に依存せず、現在の教育的なエラーメッセージも維持できる

テスト追加・修正:
- `test_no_sequences` を維持しつつ warning が出ないことを確認する
- 先頭に空行だけあるケースをどう扱うかを明示し、その仕様に対応するテストを追加する
- 既存の正常系テストはそのまま通ることを確認する

### 2. `mylib.core` の個別テスト追加

対象:
- [core.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/core.py)

追加先:
- `tests/ch05/test_mylib_core.py` を新設する

方針:
- 既存の [test_module_demo.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch05/test_module_demo.py) にある間接・混在テストは残す
- そのうえで、`core.py` の責務だけを対象にした個別テストへ分離する

最低限入れるケース:
- `gc_content()`
  - 全 GC
  - 全 AT
  - 混在
  - 空文字
  - 小文字入力
- `reverse_complement()`
  - 通常ケース
  - 回文配列
  - 未知塩基を `N` に落とすケース
  - 空文字
  - 小文字入力

狙い:
- `module_demo` の import テストとは独立に、「配列処理ロジック自体」が壊れていないことを示す

### 3. `mylib.utils` の個別テスト追加

対象:
- [utils.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/utils.py)

追加先:
- `tests/ch05/test_mylib_utils.py` を新設する

最低限入れるケース:
- 妥当な配列では `(True, [])` を返す
- 不正文字を含む配列では `(False, [...])` を返す
- 同じ不正文字が複数回出ても 1 回だけ報告される
- 不正文字の報告順が初出順である
- 空文字
- 小文字配列

狙い:
- `validate_sequence()` の戻り値仕様を、`module_demo` とは別ファイルで固定する

### 4. `argparse` 版 CLI の個別テスト追加

対象:
- [cli_argparse.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch11/cli_argparse.py)

追加先:
- `tests/ch11/test_cli_argparse.py` を新設する

方針:
- `parse_args()` の引数仕様テストと、`main()` の入出力テストを分ける
- `argparse.FileType` が parse 時点でファイルハンドルを開くため、テスト内で明示的に close するか一時ファイルを使って完結させる

最低限入れるケース:
- `parse_args()`
  - デフォルト値
  - `--min-gc`, `--max-gc`
  - `-v/--verbose`
  - `--version`
- `main()`
  - 入力ファイルから読み、出力ファイルへ書ける
  - GC 範囲でフィルタされる
  - 全通過
  - 全除外
  - `--verbose` 指定でも正常終了する

狙い:
- 既存の [test_cli_click.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch11/test_cli_click.py) と同等の観点を `argparse` 版にも持たせる
- 教材として「Click だけがテストされている」状態を解消する

## 実装順

1. `MANUAL-0006` を先に解消する
2. `tests/ch05/test_mylib_core.py` を追加する
3. `tests/ch05/test_mylib_utils.py` を追加する
4. `tests/ch11/test_cli_argparse.py` を追加する
5. 全体テストを実行する
6. `docs/review/master_issue_log.csv` と [pending_review_items.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_review_items.md) を更新して残件を閉じる

## 検証計画

最低限の確認:

- `./.venv/bin/pytest -q tests/ch10/test_error_handling.py`
- `./.venv/bin/pytest -q tests/ch05`
- `./.venv/bin/pytest -q tests/ch11`

最終確認:

- `./.venv/bin/pytest -q`

受け入れ条件:

- `BiopythonDeprecationWarning` が再発しない
- `core.py`, `utils.py`, `cli_argparse.py` に個別テストファイルが存在する
- 既存テストを壊さない
- `docs/review` 上の未完了修正 4 件を閉じられる状態になる

## リスクと注意点

- `validate_fasta()` の事前検証を厳しくしすぎると、これまで暗黙に通っていた入力を弾く可能性がある
- `argparse.FileType` のテストではファイルハンドル管理を雑にすると Windows 系環境で不安定になりやすい
- `module_demo` 側の既存テストと重複は生じるが、今回は「責務ごとの独立テストを持つ」ことを優先する

## 実装後に更新する文書

- [master_issue_log.csv](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/master_issue_log.csv)
- [pending_review_items.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_review_items.md)
- 必要なら [README.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/README.md)
