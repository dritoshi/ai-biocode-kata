# 3章・4章 CSV/浮動小数点 修正計画

## Summary

本計画は、[03_cs_basics.md](/Users/itoshi/Projects/writing/ai-biocode-kata/chapters/03_cs_basics.md) と [04_data_formats.md](/Users/itoshi/Projects/writing/ai-biocode-kata/chapters/04_data_formats.md) にある「CSV round-trip による精度劣化」の説明を、**現代の Python の実際の挙動**と**本来伝えたかった実務上の注意点**に合わせて修正するための実装計画である。

修正方針は次の通りとする。

- 「Python 標準ライブラリ内の単純な CSV round-trip で精度劣化が蓄積する」という主張は撤回する
- 本来の論点を、「**Excel や表示用フォーマット、有限桁のテキスト出力、他ツールを介した丸め**で値が変わる」に置き直す
- 4章の短いコード例は、初心者がその場で理解できるよう**標準ライブラリだけで完結する形**へ寄せる
- 付属スクリプト `scripts/ch04/*` は、概念導入ではなく「完全実装」「再利用版」として後ろに回す

21章の `p値` 表記は、ユーザー判断に従いこの修正計画には含めない。

## Findings

事前確認で得られた事実は以下の通り。

- この環境の `python3` は `Python 3.14.3`
- 現行の `scripts/ch04/tsv_csv_handling.py` にある `csv_roundtrip_precision()` は、`csv.writer` → `csv.reader` → `float()` だけを使っている
- 同関数の方式では、`3.141592653589793`、`0.1 + 0.2`、`1e-300` などを繰り返し round-trip しても値は変化しない
- Python 公式の *What’s New in Python 3.1* には、「新しい浮動小数点文字列表現」が導入されたとある。したがって、少なくとも現代の Python では、既定の float 文字列表現を前提にした単純 round-trip を精度劣化の代表例にするのは不適切である
- 一方で、`format(x, ".6f")`、`printf` 系フォーマット、`pandas.to_csv(float_format=...)`、Excel 保存など、**有限桁に丸めたテキスト表現**を挟むと精度損失は再現できる
- 4章の以下の例は、短い説明用コードにもかかわらず `scripts/ch04` の helper import を前提にしている
  - `from scripts.ch04.tsv_csv_handling import read_expression_tsv, write_expression_csv`
  - `from scripts.ch04.tsv_csv_handling import csv_roundtrip_precision`
  - `from scripts.ch04.messy_to_tidy import ...`
  - `from scripts.ch04.tidy_data_demo import ...`

## Key Changes

### 1. 3章の説明を「Python内部の問題」から「テキスト化・外部ツールの問題」へ修正する

- [03_cs_basics.md](/Users/itoshi/Projects/writing/ai-biocode-kata/chapters/03_cs_basics.md) の `CSV round-trip による丸め誤差の蓄積` 節は、主張の中心を次のように置き換える
  - **現代の Python 標準ライブラリ既定挙動では、単純な float の CSV round-trip は通常は保持される**
  - **精度損失が問題になるのは、表示用に桁数を丸める、他ツールで保存し直す、他言語・表計算ソフトを介する、といった経路である**
- 節タイトルは必要に応じて次のどちらかへ変更する
  - `テキスト化と他ツールを介した丸め誤差`
  - `CSV/テキスト出力に伴う丸め誤差`
- 現行の「多段パイプラインで Python 同士が CSV を受け渡すと各段で微小な劣化が蓄積する」という叙述は削除する
- 代わりに、Excel・表示用 CSV・`float_format` 指定・報告用 TSV のような**有限桁出力**を通した場合の誤差混入経路を説明する
- Python 公式資料に基づき、「少なくとも Python 3.1 以降の既定 float 表示では round-trip-safe な表現が採用されている」という注記を入れる
- 3章の結論は維持する
  - 中間データにバイナリ形式を使う理由は依然として有効
  - ただし、その理由は「Python 自体が毎回壊すから」ではなく、「有限桁テキスト化や他ツール介在時の再現性リスクを避けるため」に書き換える

### 2. 4章の短い CSV/TSV 例は標準ライブラリだけで完結させる

- [04_data_formats.md](/Users/itoshi/Projects/writing/ai-biocode-kata/chapters/04_data_formats.md) の `TSV / CSV` 導入部では、`scripts.ch04.tsv_csv_handling` の import をやめる
- `csv` と `pathlib` を使った最小例へ置き換える
  - TSV の `DictReader` 読み込み
  - CSV の `DictWriter` 書き出し
- 目的は「TSV と CSV の基本操作を理解させること」なので、ここでは付属 helper に依存しない
- helper は削除しなくてよいが、本文では「完全実装は `scripts/ch04/tsv_csv_handling.py` にある」と後置きで紹介する

### 3. 4章の `csv_roundtrip_precision` 例は削除し、有限桁丸めの例へ差し替える

- `from scripts.ch04.tsv_csv_handling import csv_roundtrip_precision` の例は削除する
- 代替として、本文内に次の性質を持つ短い自立コードを置く
  - `math.pi` などの値を `format(x, ".6f")` のように有限桁で文字列化
  - その文字列を CSV に保存して読み戻す
  - 元の値との差を表示する
- 例の framing は「CSV そのものが悪い」ではなく、「**表示用に丸めたテキストとして保存すると元の精度は戻らない**」にする
- 直後に、次の一文を必ず入れる
  - 「現代の Python 標準ライブラリ既定挙動では、単純な float の CSV round-trip だけで通常はこの問題は起きない」

### 4. `scripts/ch04` の役割を「必須依存」から「付属実装」へ整理する

- `scripts/ch04/tsv_csv_handling.py`
  - `read_expression_tsv()` と `write_expression_csv()` は維持してよい
  - `csv_roundtrip_precision()` は削除する
  - モジュールドックストリングも「精度劣化を実演する」から、基本的な TSV/CSV 入出力ヘルパーへ修正する
- `scripts/ch04/messy_to_tidy.py`
  - 実装は stdlib-only なので維持する
  - 4章本文では「本書付属の再利用版 helper を使う簡潔版」であることを明記する
- `scripts/ch04/tidy_data_demo.py`
  - pandas ベースの実務例として維持する
  - 4章本文では、概念理解の主例ではなく「wide/long 変換の完全実装例」として扱う

### 5. 4章の helper import を段階的に整理する

- 4章前半の短い説明コードでは `from scripts.ch04...` を使わない
- 4章後半で helper import を残す場合は、直前に次の情報を明記する
  - 本書リポジトリの付属スクリプトであること
  - ここでは概念説明を簡潔にするため helper を使っていること
  - そのまま単独コピーでは動かず、リポジトリ前提であること
- とくに `messy_to_tidy` と `tidy_data_demo` のブロックは、**コピペ即実行例**ではなく**付属実装の利用例**として明示する

### 6. `roadmap.md` の重複記述も同期する

- [roadmap.md](/Users/itoshi/Projects/writing/ai-biocode-kata/chapters/roadmap.md) に `§3-2 round-trip問題` を前提にした記述が残っている
- 3章の修正後、`roadmap.md` の該当箇所も次の趣旨へ同期する
  - `round-trip 問題` ではなく、`有限桁のテキスト化や他ツールを介した再現性リスク`
  - 中間データを `.npy` / `.npz` / `.parquet` に寄せる理由は維持する

### 7. テストとレビュー台帳を整合させる

- [tests/ch04/test_tsv_csv_handling.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch04/test_tsv_csv_handling.py) から `csv_roundtrip_precision()` 関連のテストを削除する
- `read_expression_tsv()` / `write_expression_csv()` のテストは維持する
- 必要なら、新しい helper を作らずに章本文だけで実演する
- 章の手動レビュー台帳には、`3章/4章の CSV と精度説明を再設計した` 旨を記録する

## Test Plan

- `python3 --version` の確認結果を踏まえ、3章本文が「現代の Python 既定挙動」を正しく表現していること
- 3章に「Python 標準ライブラリ内の単純 CSV round-trip が通常の原因」と読める文章が残っていないこと
- 4章前半の `TSV / CSV` 導入例に `from scripts.ch04...` が残っていないこと
- 4章の有限桁丸め例が、標準ライブラリだけで意味のある再現を示していること
- `scripts/ch04/tsv_csv_handling.py` から `csv_roundtrip_precision()` が消えた場合、関連テストも消えていること
- `rg "csv_roundtrip_precision|from scripts\\.ch04"` で、残存箇所が意図した場所だけになっていること
- `check_structure.py` を再実行して、構造規約 0 件を維持すること
- 必要なら `pytest tests/ch04` と `pytest tests/ch03` を実行し、説明変更に伴う helper/テスト削除で失敗が出ないことを確認すること

## Assumptions

- 今回の修正では、21章の `p値` 表記は触らない
- 「Python 標準ライブラリで問題が起きない」ことは明記する
- ただし「すべての Python バージョン・すべての処理系で常に同じ」とは一般化せず、**少なくとも現代の Python 既定挙動では**という書き方を基本にする
- 4章のコード例は、教育目的が優先であり、短い例は自立性を、長い例は付属スクリプト参照を優先する
- helper import を完全禁止にはしないが、初心者が「そのまま貼って動く」と誤解しうる短い例からは外す

## Reference Notes

- Python 公式: *What’s New In Python 3.1*  
  https://docs.python.org/ja/3.13/whatsnew/3.1.html
- ローカル確認: `python3 --version` は `Python 3.14.3`
- ローカル確認: 現行 `csv_roundtrip_precision()` 相当処理では `3.141592653589793`、`0.30000000000000004`、`1e-300` は変化しない
