# E1整理計画

- 作成日: 2026-07-28
- 基準コミット: `27adae7b658754626d097a233540edbc75af39c5`
- 基準対応表: [`code_correspondence.json`](./code_correspondence.json)
- 対象: 対応表でE1と判定された45ブロック
- 状態: 計画レビュー完了（第16巡で新規finding 0件）
- 非目的: 本計画PRでの本文、`scripts/`、`tests/`、対応表の修正

## 1. 目的

E1は、本文と対応実体の構造・動作が一致し、docstring、定義名、局所名などの
非本質的な差だけがある判定である。E1そのものは誤りではないが、差の理由が本文から
分からなければ、読者は本文と `scripts/` のどちらを基準にすべきか判断できない。

本計画は、現行E1 45件を次の3種類へ整理する。

1. 偶発的な名前・型注釈の差は、テスト済み実体と完全同期してE0へ移す
2. 1ブロック内の明示的なスタブや省略は、全定義を対応付けてE2へ移す
3. 段階的学習や読みやすさのために必要な差だけを、根拠付きのE1として残す

残すE1では、`scripts/` を実行可能な正本かつ完全なAPI説明として維持する。本文にだけ
ある教育的コメントのうち、単独で `scripts/` を読む人にも必要な前提、単位・形状、
境界条件、性能上の意図は、意味を保って `scripts/` にも反映する。一方、章の進行や
直前の説明に依存するコメントは本文に残し、スクリプトへ機械的に複製しない。

完了時には「理由を説明できないE1」が0件となり、残るE1は教育上の意図、対応実体、
検証方法をすべて追跡できる状態にする。

## 2. 基準状態

基準対応表の生成対象コミットは `943697e` である。その後のPRではレビュー文書と
CI設定だけが変更されており、本文、`scripts/`、`tests/` の対応対象集合は変わって
いない。基準コミット `27adae7` で対応表のブロック集合、ファイルハッシュ、E1集合を
監査し、E1 45件が現行ソースと一致することを確認した。

テスト件数は基準対応表に記録された値であり、この計画レビューで再実行した結果では
ない。各実装PRでは対象テストと全体テストを改めて実行する。

| 項目 | 実測値 |
|---|---:|
| 本文コードブロック | 529 |
| 配置必須 | 134 |
| E0 | 51 |
| E1 | 45 |
| E2 | 38 |
| E3 | 0 |
| E5 | 0 |
| EN | 395 |
| `scripts/ch*` の実ファイル | 176 |
| テスト結果 | 939 passed、11 skipped、0 failed |
| 構造検査 | 27 findings |
| 相互参照検査 | 0 findings |

E1の章別内訳は次のとおりである。

| 章 | 件数 |
|---|---:|
| ch01 | 3 |
| ch03 | 1 |
| ch08 | 6 |
| ch09 | 5 |
| ch10 | 3 |
| ch12 | 14 |
| ch13 | 3 |
| ch17 | 6 |
| ch21 | 4 |
| 合計 | 45 |

45件のうち35件はdocstringを除くASTが一致し、2件は定義名を伏せるとASTが一致する。
残る8件は、TDDの段階差、空入力の同値な分岐、型注釈、局所名、章をまたぐ再利用など
である。なお、対応関係は45ブロックに46件ある。`B-08-009` が2実体に結び付いている
ためだが、そのうち逆相補鎖テストへの関係は誤対応であり、実装時に削除する。

構造検査27件は既存の著者・注意ページの必須セクション判定8件と、太字内カッコ・
カギ括弧19件であり、E1作業とは別スコープである。実装PRではこの27件を基準値とし、
新規findingを発生させない。

## 3. 整理原則

### 3.1 収束先

| 整理型 | 条件 | 目標判定 |
|---|---|---|
| A. 完全同期 | 本文が単体で完結する完全例で、名前・型注釈・局所名だけが偶発的に異なる | E0 |
| B. 意図的差分 | 段階的学習、焦点化、簡潔なdocstringに教育上の理由がある | E1 |
| C. 明示的抜粋 | 1ブロック内にスタブ、省略、複数定義の一部だけの提示がある | E2 |
| D. 対応訂正 | 弱い候補、誤対応、複数定義の対応漏れがある | 正しい全実体を対応後、E0〜E2 |

E1を残す場合は、「ASTが同じ」だけでは根拠として不十分である。本文側の差が担う
教育上の役割、完全版を参照できる導線、正常系・境界値・例外・副作用の一致を確認する。
この動作一致はE0関係とE1関係に適用する。E2関係はスタブや意図的省略を含むため、
実体との戻り値一致を要求せず、省略境界、対応実体、実体テスト、本文の記述が実体と
矛盾しないことを確認する。E2親ブロック内でも、完成済み定義に対応する
`equivalence: E1` の3関係には関係単位で動作一致を要求する。

### 3.2 docstringと教育的コメント

`scripts/` のNumPy形式docstringは、引数、戻り値、例外、単位・形状を説明し、
APIドキュメント生成にも使えるため、本文の短いdocstringへ縮退させない。本文では
節の焦点を外さない範囲で短縮できるが、コードブロック直前または直後に「完全な
docstringを含む実装は `scripts/` にある」と相対リンク付きで明示する。

教育的コメントはE判定の正規化時に除かれるため、コメントだけの差はE1の原因に
ならない。それでも読者が本文と実体を往復したときの混乱を避けるため、文字列一致
ではなく、次の意味分類で同期する。

| 分類 | `scripts/` への反映 | 例 |
|---|---|---|
| 生物学・データ上の前提 | 必須 | Nの扱い、FASTQは1レコード4行、TPMの分母 |
| 単位・配列形状・境界条件 | 必須 | bp、行列の軸、ゼロ除算、閾値を含むか |
| 非自明な実装判断 | 必須 | 安定ソート、順序保持、並列処理のフォールバック |
| 性能上の意図 | 原則必須 | Pythonループを残す比較基準、ベクトル化の対象軸 |
| 章の進行や直前説明への参照 | 不要 | 「上で定義した関数を使う」「ここでは簡略化する」 |
| コードから自明な逐語説明 | 不要 | 「ファイルを開く」「値を返す」 |

既存docstringが同じ意味を十分に説明していても、処理行に結び付く判断理由が必要なら
インラインコメントを追加する。反対に、docstringと完全に重複するコメントは増やさない。

初回調査でのコメント同期候補は次のとおりである。実装時には差分後のコードを再確認し、
各IDの対応表に後述の `comment_sync` を記録する。

| 最終期待状態 | 件数 | 対象ID |
|---|---:|---|
| `added` | 4 | `B-03-019`、`B-09-024`、`B-12-007`、`B-13-003` |
| `satisfied_existing` | 27 | `B-01-003`、`B-01-004`、`B-08-006`、`B-08-009`、`B-09-003`、`B-09-005`、`B-09-007`、`B-09-020`、`B-10-024`、`B-10-028`、`B-10-031`、`B-12-001`、`B-12-003`、`B-12-004`、`B-12-005`、`B-12-006`、`B-12-015`、`B-13-002`、`B-13-004`、`B-17-016`、`B-17-029`、`B-17-030`、`B-17-032`、`B-17-039`、`B-21-004`、`B-21-012`、`B-21-014` |
| `body_only` | 1 | `B-08-019` |
| `not_applicable` | 13 | `B-01-001`、`B-08-001`、`B-08-002`、`B-08-003`、`B-12-008`、`B-12-009`、`B-12-010`、`B-12-014`、`B-12-016`、`B-12-017`、`B-12-018`、`B-17-038`、`B-21-007` |

この初回分類はコメント追加数のノルマではない。実装時に状態、source証拠種別、
意味分類、source/targetファイル、scope、entityのいずれかを下の規範表から変える必要が
生じた場合は停止条件に該当し、計画改定を先行する。コメント追加によってE0・E1の判定が
変わったとは記録しない。

`comment_sync` のsource候補は、コードブロック内の行コメントだけとする。関数・クラスの
docstringはE1差分そのものとして別に追跡するためsource候補に含めず、コードブロック外の
本文説明は `body_only` の根拠に限って使う。行コメントであっても、意図的なエラーや
章内の説明だけを注釈する場合は `body_only` にできる。`B-08-019` のmypy診断注釈は
この例であり、実行可能な正本へ移さない。ファイルパスを示すだけのコメントも教育的
コメントとは数えない。実体側では、同じ意味を持つ行コメント、entity内のdocstring、
モジュールdocstringまたは定義直前コメントを証拠にできる。この規則により、たとえば
`B-12-017` は本文docstringだけなので `not_applicable` であり、本文の行コメントを持つ
`B-12-015` は `satisfied_existing` となる。

意味分類は `biological_data_assumption`、`unit_shape_boundary`、
`implementation_decision`、`performance_intent`、`chapter_context`、`none` の
6値に固定する。次表を45 IDの規範アンカーとし、fixtureへ同じ値を転記する。
`scope/entity` は実体側のコメント証拠を解決する範囲であり、`—` はscopeとentityを
ともに `null` とする。source証拠の `line_comment` は行コメント、
`body_explanation` はコードブロック外の本文説明、`none` は対象証拠なしを表す。

| ID | 状態 | source証拠 | 意味分類 | sourceファイル | targetファイル | scope/entity | 完了バッチ |
|---|---|---|---|---|---|---|---:|
| `B-01-001` | `not_applicable` | `none` | `none` | `chapters/01_design.md` | `scripts/ch01/gc_content.py` | — | 1 |
| `B-01-003` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/01_design.md` | `scripts/ch01/gc_content.py` | `entity/filter_sequences_by_gc` | 1 |
| `B-01-004` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/01_design.md` | `scripts/ch01/seq_filter.py` | `file/null` | 1 |
| `B-03-019` | `added` | `line_comment` | `implementation_decision` | `chapters/03_cs_basics.md` | `scripts/ch03/random_reproducibility.py` | `entity/subsample_with_seed` | 1 |
| `B-08-001` | `not_applicable` | `none` | `none` | `chapters/08_testing.md` | `tests/ch08/test_reverse_complement.py` | — | 2 |
| `B-08-002` | `not_applicable` | `none` | `none` | `chapters/08_testing.md` | `scripts/ch08/reverse_complement.py` | — | 2 |
| `B-08-003` | `not_applicable` | `none` | `none` | `chapters/08_testing.md` | `tests/ch08/test_reverse_complement.py` | — | 2 |
| `B-08-006` | `satisfied_existing` | `line_comment` | `biological_data_assumption` | `chapters/08_testing.md` | `tests/ch08/test_reverse_complement.py` | `entity/TestReverseComplement.test_palindrome` | 2 |
| `B-08-009` | `satisfied_existing` | `line_comment` | `biological_data_assumption` | `chapters/08_testing.md` | `tests/ch08/test_seq_stats.py` | `entity/TestGcContent.test_with_n` | 2 |
| `B-08-019` | `body_only` | `line_comment` | `chapter_context` | `chapters/08_testing.md` | `scripts/ch08/seq_stats.py` | — | 2 |
| `B-09-003` | `satisfied_existing` | `line_comment` | `unit_shape_boundary` | `chapters/09_debug.md` | `scripts/ch09/traceback_demo.py` | `entity/parse_gene_expression` | 2 |
| `B-09-005` | `satisfied_existing` | `line_comment` | `unit_shape_boundary` | `chapters/09_debug.md` | `scripts/ch09/traceback_demo.py` | `entity/lookup_gene_annotation` | 2 |
| `B-09-007` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/09_debug.md` | `scripts/ch09/debug_print_demo.py` | `entity/filter_sequences_logging_debug` | 2 |
| `B-09-020` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/09_debug.md` | `scripts/ch09/path_bugs.py` | `entity/resolve_data_path` | 2 |
| `B-09-024` | `added` | `line_comment` | `biological_data_assumption` | `chapters/09_debug.md` | `scripts/ch09/type_bugs.py` | `entity/safe_mean` | 2 |
| `B-10-024` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/10_deliverables.md` | `scripts/ch10/config_example.py` | `entity/load_config` | 2 |
| `B-10-028` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/10_deliverables.md` | `scripts/ch10/error_handling.py` | `entity/load_min_quality` | 2 |
| `B-10-031` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/10_deliverables.md` | `scripts/ch10/error_handling.py` | `entity/count_records_with_cleanup` | 2 |
| `B-12-001` | `satisfied_existing` | `line_comment` | `performance_intent` | `chapters/12_data_processing.md` | `scripts/ch12/plot_vectorize_bench.py` | `entity/gc_contents_slow` | 3 |
| `B-12-003` | `satisfied_existing` | `line_comment` | `performance_intent` | `chapters/12_data_processing.md` | `scripts/ch12/plot_vectorize_bench.py` | `entity/gc_content_per_seq` | 3 |
| `B-12-004` | `satisfied_existing` | `line_comment` | `performance_intent` | `chapters/12_data_processing.md` | `scripts/ch12/numpy_vectorize.py` | `entity/gc_content_vectorized` | 3 |
| `B-12-005` | `satisfied_existing` | `line_comment` | `unit_shape_boundary` | `chapters/12_data_processing.md` | `scripts/ch12/numpy_vectorize.py` | `entity/normalize_cpm` | 3 |
| `B-12-006` | `satisfied_existing` | `line_comment` | `unit_shape_boundary` | `chapters/12_data_processing.md` | `scripts/ch12/numpy_vectorize.py` | `entity/filter_by_quality` | 3 |
| `B-12-007` | `added` | `line_comment` | `biological_data_assumption` | `chapters/12_data_processing.md` | `scripts/ch12/pandas_bio_ops.py` | `entity/load_deg_results` | 3 |
| `B-12-008` | `not_applicable` | `none` | `none` | `chapters/12_data_processing.md` | `scripts/ch12/pandas_bio_ops.py` | — | 3 |
| `B-12-009` | `not_applicable` | `none` | `none` | `chapters/12_data_processing.md` | `scripts/ch12/pandas_bio_ops.py` | — | 3 |
| `B-12-010` | `not_applicable` | `none` | `none` | `chapters/12_data_processing.md` | `scripts/ch12/pandas_bio_ops.py` | — | 3 |
| `B-12-014` | `not_applicable` | `none` | `none` | `chapters/12_data_processing.md` | `scripts/ch12/scipy_stats_bio.py` | — | 3 |
| `B-12-015` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/12_data_processing.md` | `scripts/ch12/scipy_stats_bio.py` | `entity/correct_pvalues` | 3 |
| `B-12-016` | `not_applicable` | `none` | `none` | `chapters/12_data_processing.md` | `scripts/ch12/scipy_stats_bio.py` | — | 3 |
| `B-12-017` | `not_applicable` | `none` | `none` | `chapters/12_data_processing.md` | `scripts/ch12/scipy_stats_bio.py` | — | 3 |
| `B-12-018` | `not_applicable` | `none` | `none` | `chapters/12_data_processing.md` | `scripts/ch12/scipy_stats_bio.py` | — | 3 |
| `B-13-002` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/13_visualization.md` | `scripts/ch13/matplotlib_bindist.py` | `file/null` | 4 |
| `B-13-003` | `added` | `line_comment` | `implementation_decision` | `chapters/13_visualization.md` | `scripts/ch13/bio_plots.py` | `entity/volcano_plot` | 4 |
| `B-13-004` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/13_visualization.md` | `scripts/ch13/bio_plots.py` | `entity/expression_heatmap` | 4 |
| `B-17-016` | `satisfied_existing` | `line_comment` | `performance_intent` | `chapters/17_performance.md` | `scripts/ch17/profiling_demo.py` | `entity/normalize_tpm_slow` | 4 |
| `B-17-029` | `satisfied_existing` | `line_comment` | `performance_intent` | `chapters/17_performance.md` | `scripts/ch17/profiling_demo.py` | `entity/normalize_tpm_fast` | 4 |
| `B-17-030` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/17_performance.md` | `scripts/ch17/parallel_gc.py` | `entity/gc_content_parallel` | 4 |
| `B-17-032` | `satisfied_existing` | `line_comment` | `performance_intent` | `chapters/17_performance.md` | `scripts/ch17/generator_fastq.py` | `entity/process_pipeline` | 4 |
| `B-17-038` | `not_applicable` | `none` | `none` | `chapters/17_performance.md` | `scripts/ch17/file_format_bench.py` | — | 4 |
| `B-17-039` | `satisfied_existing` | `line_comment` | `biological_data_assumption` | `chapters/17_performance.md` | `scripts/ch02/fastq_gzip.py` | `entity/count_reads_in_gzip` | 4 |
| `B-21-004` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/21_collaboration.md` | `scripts/ch21/format_question.py` | `entity/collect_environment` | 5 |
| `B-21-007` | `not_applicable` | `none` | `none` | `chapters/21_collaboration.md` | `scripts/ch21/review_helper.py` | — | 5 |
| `B-21-012` | `satisfied_existing` | `line_comment` | `implementation_decision` | `chapters/21_collaboration.md` | `scripts/ch21/progress_report.py` | `entity/parse_git_log` | 5 |
| `B-21-014` | `satisfied_existing` | `line_comment` | `unit_shape_boundary` | `chapters/21_collaboration.md` | `scripts/ch21/analysis_intake.py` | `entity/validate_metadata` | 5 |

スキーマ4では基準45 IDごとに `comment_sync` を1件持たせ、次の4つの終端状態を
区別する。

- `added`: 実体へコメントを追加・調整した
- `satisfied_existing`: 既存コメントまたはdocstringが意味を充足している
- `body_only`: 章の進行や直前説明だけに属し、実体へ移さない
- `not_applicable`: 同期対象となる教育的コメントがない

バッチ0〜4の未着手IDには中間状態 `pending` を使う。`pending` レコードは
`block_id`、`status: pending`、`scheduled_batch`、`expected_terminal_status` の
4フィールドだけを持ち、理由、意味分類、位置、証拠ハッシュを禁止する。各バッチでは、
そのバッチまでの対象だけを終端状態へ遷移させる。終端済み/`pending` 数はバッチ0〜5で
0/45、4/41、18/27、32/13、41/4、45/0である。バッチ5で `pending` が1件でもあれば
非0終了する。

終端レコードには `block_id`、`status`、`reason`、意味分類を持たせる。`added` と
`satisfied_existing` は、本文側のコメント位置と、対応する実体のファイル・証拠scope・
行位置を1件以上必須とする。`body_only` は本文位置と本文だけに残す理由を必須とし、
実体位置を許さない。`not_applicable` は本文位置・実体位置を許さず、対象外理由を
必須とする。位置はsnapshotの該当行と後述のscope規則へ解決し、証拠テキストの
SHA-256も記録する。
実体証拠の `scope` は `entity` または `file` とする。`entity` はentity IDを必須とし、
行範囲がそのentity内にあることを検査する。`file` はentity IDを禁止し、モジュール
docstringまたは定義直前のコメントに限り、行範囲が対象ファイル内にあることを検査する。
`B-01-004` と `B-13-002` のモジュールdocstringは `scope: file` で追跡する。

固定fixtureは上の規範表と同じ最終45件の期待終端状態、source証拠種別、意味分類、
source/targetファイル、証拠scope、期待entity、完了予定バッチと、バッチごとの終端・
`pending` ID集合を保持する。行範囲とハッシュは、各IDの完了バッチで成果物へ初めて
記録する。fixtureの意味アンカーはバッチ1のsourceコミットで固定し、バッチ2〜5では
変更を禁止する。変更が必要なら停止して計画改定PRを先行する。独立監査は、各バッチの
終端・`pending` 集合に過不足がないこと、終端レコードの列挙値、必須位置、位置解決、
証拠ハッシュ、fixtureの意味アンカーを検査する。

バッチ0は現行スキーマ3の追跡済み対応表そのものではなく、そこから決定的に生成する
遷移基準状態とする。`build_e1_batch0_state.py` は基準ref
`27adae7b658754626d097a233540edbc75af39c5` の
`docs/review/code_correspondence.json` をGit treeから読み、スキーマ3、基準source
コミット、45 ID、E件数、46関係、placement 41/4を検査する。そのGit blob OIDと
正規化後SHA-256を記録し、`completed_batch: 0` と、規範表から生成した45件の
4フィールドだけの `pending` を持つ遷移状態を一時領域へ出力する。同じ入力とfixtureから
バイト単位で同じ出力になることをテストし、バッチ1の比較元には毎回この処理で再生成した
状態だけを使う。

`check_e1_transition.py` は、バッチ1ではこのバッチ0状態、バッチ2〜5では
`origin/main` にある直前PRの対応表を比較元にする。比較元の
`completed_batch == n - 1`、比較先の `completed_batch == n` を要求し、予定バッチ$n$の
IDだけが `pending` から規範表どおりの終端状態へ移ることを許す。それ以前に終端した
レコードは全フィールドのdeep equality、それ以後の `pending` レコードは4フィールドの
deep equalityを要求する。早期完了、遅延、終端から `pending` への逆戻り、終端状態間の
変更、余分な `pending` フィールド、既完了の理由・位置・ハッシュの書換えは非0終了とする。
この遷移検査をfinalizer前後、マージ後の一時worktree監査へ接続する。

証拠ハッシュは、snapshot中の記録済み開始行から終了行までを対象とする。改行をLFへ
統一し、各行の末尾空白だけを除き、末尾LFを1つ付けたUTF-8バイト列のSHA-256とする。
コメントのインデント、`#`、docstringの引用符と本文は保持する。成果物は状態だけでなく、
本文・実体ファイル、scope、entity、行範囲、正規化後ハッシュを記録する。たとえば
`B-10-031` の後始末、`B-13-004` の距離行列、`B-17-039` のFASTQ 4行構造は
`satisfied_existing` とし、本文コメントと実体コメントまたはdocstringの双方を証拠にする。

### 3.3 複数定義ブロック

本計画では、基準E1の45ブロック内にあるトップレベル定義を、完全実装、抜粋、スタブを
問わず、すべて対応表で追跡する。トップレベル定義とはPython ASTのModule直下の
関数・クラスであり、クラス内メソッドは包含するクラスの関係で追跡する。基準E1以外の
配置必須ブロックにある定義単位不足は本計画の対象外とし、別の再監査で扱う。

各関係には対象側の `target_file`、`target_entity`、
`target_entity_locations` だけでなく、本文側の `source_entity_id`、
`source_entity`、`source_entity_locations` も記録する。自動候補が保持している
`source_entity_id` を関係レコードへ引き継ぎ、overrideによる関係にも明示する。
独立監査では、source定義が当該ブロックに属すること、source・targetの位置が解決する
こと、各source定義がちょうど1関係に現れることを検査する。さらに、
`target_file_id + target_entity_locations[].id` も原則1回だけ現れることを検査し、
意図的な共有がある場合だけ `shared_target_reason` を必須とする。本計画の56関係には
共有例外を予定しない。実体が存在しない場合は配置規約に従って実体とテストを先に
作る。本計画の対象では実体がすでに存在するため、新規実体の作成は予定しない。

次の10ブロックには現行対応表の定義単位の不足または曖昧さがある。

- `B-01-004`: `SequenceRecord` だけでなく、3つの処理スタブを対応付ける
- `B-08-001`: `TestReverseComplement.test_simple_sequence` へ対応付ける
- `B-08-003`: 空入力と小文字の2メソッドへ個別に対応付ける
- `B-08-006`: `TestReverseComplement` クラスの抜粋として対応付ける
- `B-08-009`: GC含量の2メソッドへ個別に対応付け、逆相補鎖への誤対応を削除する
- `B-17-030`: `gc_content_single` と `gc_content_parallel` を対応付ける
- `B-17-032`: FASTQ読込と2つのフィルターを定義名付きで対応付ける
- `B-17-038`: `save_as_csv` と `save_as_parquet` を対応付ける
- `B-21-004`、`B-21-012`: 完全関数に続くスタブも対応付ける

`B-01-004`、`B-21-004`、`B-21-012` はスタブを含み、`B-08-006` は完成テスト
クラスの一部だけを示すため、ブロック全体をE2へ移す。残る6ブロックは定義単位の
関係を補ってE1を維持する。現行45ブロックの関係は46件であり、上記10ブロックの
11関係を21関係へ展開するため、完了時は56関係となる。集計軸を混同しないよう、次の
2指標を別々に記録する。

| 指標 | E0 | E1 | E2 | 合計 |
|---|---:|---:|---:|---:|
| `relations_by_parent_block_correspondence` | 4 | 43 | 9 | 56 |
| `relations_by_equivalence` | 4 | 46 | 6 | 56 |

前者は各関係の親ブロックの最終判定、後者は関係自身の `equivalence` である。E2親
ブロック内には、完成済み定義へのE1関係3件と、スタブ・省略へのE2関係6件がある。
最終56関係のsource、target、`equivalence` と、バッチ0〜5の中間期待値は固定fixture
としてレビュー用テストに置く。

### 3.4 goldsetと監査スキーマ

`B-03-019` はE1からE0へ移るため、現行goldsetのE1標本には残せない。バッチ1で
`B-03-019` をgoldsetから外し、残存E1の `B-01-001` を追加する。E0標本は
`B-07-014` と `B-15-001`、E1標本は `B-01-001` と `B-12-004` とし、存在する各判定を
2標本に保つ。`review_metadata.goldset_change_history` に変更日、旧標本、新標本、
理由を記録し、生成テストと独立監査で標本数と実測一致を確認する。

source provenanceを追加するため、対応表スキーマを3から4へ上げる。`method` は本計画
`docs/review/2026-07-28_e1_remediation_plan.md` を指し、次の情報を成果物へ記録する。

- `remediation_scope`: 基準コミット、基準E1 45 IDの固定リスト、そのSHA-256、完了バッチ番号
- `source_snapshot_files`: snapshotへ含めた相対パスの固定リスト
- 56関係の2集計: 親ブロック判定別4/43/9、関係自身の判定別4/46/6
- `comment_sync`: 基準45 IDの終端または中間 `pending` 状態。終端時は理由、意味分類、本文・実体の位置と証拠ハッシュ、`pending` 時は4つの許可フィールドだけを記録する

snapshot対象は、番号付き本文、`scripts/ch*`、`tests/ch*`、
`scripts/review/`、`tests/review/`、本計画書とする。対応表JSON・Markdownなどの
生成物は再帰を避けるため含めない。
source側では `review_metadata.remediation_scope` に完了バッチ番号を保持し、生成時に
成果物トップレベルの `remediation_scope` へ正規化して記録する。

### 3.5 修正順

1. 対応する `scripts/` と `tests/` の実体、公開名、型、docstringを確認する
2. 実体名の変更やコメント追加が必要なら、`scripts/` を先に変更する
3. 対象テストを追加・修正して成功させる
4. 本文の完全例、型注釈、教育的コメント、完全版への導線を同期する
5. 本文差分と根拠を確認後、対応表overrideのハッシュ、関係、判定、証拠、完了バッチ番号を更新する。goldset履歴はバッチ1で更新する
6. 対象章テスト、全体テスト、Ruff、当該バッチのmypy、差分・source変更範囲検査を作業ツリーで成功させる
7. 実体、テスト、本文、override、変更したレビュー用ツールをソースコミットとして先にコミットする
8. finalizerでsource変更範囲と手順6の全ゲートをコミット済みtreeに対して再実行し、構造・相互参照検査、対応表の決定的生成、独立監査まで成功した場合だけ4生成物を後続コミットにする
9. 後続コミットの親がsourceコミットで、変更が許可した生成物だけであることをprovenance検査する
10. PR本文へsource・生成物コミットIDを固定形式で記録し、merge commitでマージ後、両IDが `origin/main` から到達可能で、PR本文の記録とも一致することを検査する。バッチ1〜4では次バッチ開始前、バッチ5ではE1作業の最終完了判定前に行う

本文だけの変更で済むのは、テスト済み実体へ完全同期する場合、完全版への導線を
加える場合、またはTDDの段階を明示する説明を加える場合に限る。

2段階コミットにより、対応表の `source_commit` は実体、テスト、本文、override、
レビュー用ツールを含むコミットを指す。生成器はsnapshot対象の作業ツリー内容がHEADの
Git treeと一致しなければ非0終了する。独立監査器は `source_commit` のGit objectが
存在する場合、そのtreeからsnapshotを再計算し、記録値と照合する。同時に現在の
作業ツリーsnapshotも照合する。各実装PRはGitHubの「Create a merge commit」で
マージし、sourceコミットと生成物コミットの双方を `main` から到達可能な履歴として
保存する。squash mergeまたはrebase mergeは2段階の親子関係を失うため、本計画の
完了条件を満たさない。リポジトリ設定でmerge commitを選べない場合は実装を開始せず、
保証範囲を「マージ前のPR内検証」と「マージ後の内容snapshot検証」に分ける計画改定を
先にレビューする。

`scripts/review/check_correspondence_provenance.py` を追加し、第2コミットの親がJSONの
`source_commit` と一致すること、変更ファイルが4生成物の部分集合だけであること、
対応表JSON・Markdownが必ず含まれることを検査する。`--main-ref` と
`--require-reachable` を指定したマージ後モードでは、source・生成物コミットの双方が
指定refの祖先であることも検査する。`--artifact-commit auto` では指定sourceの直接の
子から許可された生成物コミットを一意に発見し、0件または複数件なら失敗する。
`--expected-pr-json` と `--expected-pr-state OPEN|MERGED` を併用すると、
`gh pr view` のJSONと、PR本文中にちょうど1件ある
`<!-- e1-provenance: {"pr_number":…,"source_commit":"…","artifact_commit":"…"} -->`
を解析する。PR番号、期待状態、`headRefOid` とartifact ID、マーカーの両IDを照合する。
`MERGED` ではmerge commitの指定refからの到達可能性も必須とし、欠落・重複・
不正JSON・不一致を拒否する。
override変更後に旧JSONを監査すると
失敗する回帰テスト、未コミットsourceを含む生成が失敗するテスト、Git tree改変を
検出するテストを追加する。overrideの `block_sha256` だけを先に更新して生成器の検証を
回避してはならない。

## 4. 完了条件

1. 基準E1 45件が解消マトリクスに重複なく1回ずつ現れる
2. E0予定4件はコメント・空白を除くASTが完全一致し、コメントは意味分類に従って同期する
3. E2予定4件はブロック内の全定義を追跡し、省略境界、完全実体、実体テストへの導線が明示され、本文の記述が実体と矛盾しない
4. 残すE1 37件は、教育目的、差分、完全実体、検証結果を対応表で説明できる
5. 対象45ブロックのModule直下にある56定義に対応先があり、source・targetのID、名前、位置が解決する
6. 対象45ブロックの `comment_sync` が過不足なく4つの終端状態のいずれかとなり、`pending` が0件で、必要な教育的コメントが実体へ同期され、根拠・位置・証拠ハッシュを独立監査できる
7. `scripts/` の既存の完全なdocstringを削除・短縮しない
8. 実体を変更する場合は実体とテストを先に変更し、成功後に本文へ反映する
9. 再生成した対応表でE0 55、E1 37、E2 42、E3 0、E5 0、EN 395となる
10. 本文529ブロック、配置必須134件、EN 395件の件数保存則を満たす
11. 56関係の親ブロック判定別内訳が4/43/9、関係自身の判定別内訳が4/46/6で、固定fixtureと一致する
12. 各source定義と各target定義が原則1回だけ現れ、共有例外がある場合は理由が記録される
13. goldsetが存在する各判定2標本を保ち、`B-03-019` から `B-01-001` への変更履歴が記録される
14. スキーマ4の `source_snapshot_sha256` をHEADのGit treeと記録済み対象集合から再計算でき、未コミットsource、override改変、Git tree不一致を独立監査が検出する
15. 対象テストと全体テストが成功し、Ruffと対象Pythonの型検査が成功する
16. 構造検査の新規finding集合が0件で、相互参照検査も0件である
17. 本文から追加した `../scripts/` と `../tests/` のリンクが専用検査ですべて解決し、finding時に検査コマンドが非0終了する
18. 対応表の独立監査、2コミットのprovenance検査、基点からHEADまでの `git diff --check` が成功し、記録した両コミットIDがマージ後に `origin/main` から到達できる
19. 各実装PRのsource変更集合が固定fixtureの当該バッチ許可パスに含まれ、生成物コミット後に作業対象パスの未コミット差分がない。開始前からある対象外のuntrackedは変更・削除しない
20. `B-17-032` の呼出例が呼び出し元から受け取った `Path` を使い、固定ファイル名を含まない
21. スキーマ3からバッチ0状態を決定的に再生成でき、各バッチで予定IDだけが単調遷移し、既完了レコードが全フィールド一致する
22. PR作成後の読取・JSON・本文更新失敗から明示番号で再開でき、再開時に新しいPRを作成しない

予定する移動はE1からE0へ4件、E1からE2へ4件である。したがって予定最終内訳は
E0 55、E1 37、E2 42、E3 0、E5 0、EN 395、合計529となる。実装調査でより厳密な
判定が必要になった場合は、当該PRを止め、根拠、影響ID、件数保存則を本計画へ追記して
レビューしてから再開する。

## 5. 45件の解消マトリクス

### 5.1 ch01・ch03: 設計と再現性

| ID | 現在の差 | 教育・同期方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-01-001` | `gc_content` のdocstringだけが異なる | KISSの短い例としてE1を維持し、完全版への導線を付ける | `scripts/ch01/gc_content.py:gc_content` | E1 | 空配列、Nのみ、通常配列、大小文字 |
| `B-01-003` | `filter_sequences_by_gc` のdocstringだけが異なる | DRYの再利用意図は実体の既存コメントで充足しているため重複追加せず、完全版へ導く | `scripts/ch01/gc_content.py:filter_sequences_by_gc` | E1 | 閾値未満・一致・超過、Nを含む配列 |
| `B-01-004` | クラスだけが対応し、3処理はスタブで、実体のFASTA読込が自作パーサである | 4定義を個別対応し、実体を `Bio.SeqIO.parse` へ先行修正して明示的抜粋にする | `scripts/ch01/seq_filter.py` | E2 | SeqIO利用、parse、filter、formatの単体・統合テスト |
| `B-03-019` | 関数名とNumPy型注釈だけが異なる | 実体の公開名と正確な型へ完全同期し、乱数生成器の意図を同期する | `scripts/ch03/random_reproducibility.py:subsample_with_seed` | E0 | 同一seed、異なるseed、サイズ境界、不正サイズ |

### 5.2 ch08: TDDとテスト

| ID | 現在の差 | 教育・同期方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-08-001` | Red段階の単独テストとクラス内の完成テストが異なる | 実装前という時間軸を明示し、対応メソッドを記録して最終テストへ導く | `tests/ch08/test_reverse_complement.py:TestReverseComplement.test_simple_sequence` | E1 | 現行実体での成功、Redになる理由の説明整合性 |
| `B-08-002` | Green段階は最小実装、実体には空入力の早期returnがある | 同値性を境界値で確認し、Green段階であることを明示する | `scripts/ch08/reverse_complement.py:reverse_complement` | E1 | 空、小文字、無効塩基、通常配列 |
| `B-08-003` | Refactor前の2単独テストとクラス内テストが異なる | テスト追加の段階を明示し、2対応メソッドを記録する | `tests/ch08/test_reverse_complement.py` | E1 | 空、小文字、既存正常系 |
| `B-08-006` | 本文クラスは完成テストクラスの一部で、回文assertも1件省略する | クラスの省略境界と完全版への導線を明示する | `tests/ch08/test_reverse_complement.py:TestReverseComplement` | E2 | simple、palindrome、empty、完全版の追加ケース |
| `B-08-009` | GC含量テストに逆相補鎖への誤対応があり、Nの正確な期待値assertを省略する | 誤対応を削除し、`2 / 5` のassertを本文へ同期して2メソッドを記録する | `tests/ch08/test_seq_stats.py` | E1 | Nを含む配列の正確値、1塩基、空配列 |
| `B-08-019` | mypy説明用関数と実体のdocstringだけが異なる | 型エラーの焦点を保ち、完全版への導線を付ける | `scripts/ch08/seq_stats.py:gc_content` | E1 | 本文スニペットの期待mypy診断、通常・空配列 |

### 5.3 ch09・ch10: デバッグと成果物

| ID | 現在の差 | 教育・同期方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-09-003` | `parse_gene_expression` のdocstringだけが異なる | トレースバックの焦点を保ち、入力形式と例外条件を実体にも明示する | `scripts/ch09/traceback_demo.py:parse_gene_expression` | E1 | 正常行、列不足、数値変換失敗 |
| `B-09-005` | `lookup_gene_annotation` のdocstringだけが異なる | 例外連鎖の焦点を保ち、検索失敗の意味を同期する | `scripts/ch09/traceback_demo.py:lookup_gene_annotation` | E1 | 存在キー、不在キー、例外メッセージ |
| `B-09-007` | ログによるデバッグ例のdocstringだけが異なる | DEBUGログの判断点を実体コメントにも残し、完全版へ導く | `scripts/ch09/debug_print_demo.py:filter_sequences_logging_debug` | E1 | DEBUG有効・無効、閾値境界 |
| `B-09-020` | パス解決例のdocstringだけが異なる | `~` 展開と存在確認の順序を実体にも明示する | `scripts/ch09/path_bugs.py:resolve_data_path` | E1 | `~`、相対・絶対、欠落パス |
| `B-09-024` | `safe_mean` のdocstringだけが異なる | `None` とNaNの役割を実体にも明示し、完全版へ導く | `scripts/ch09/type_bugs.py:safe_mean` | E1 | 空、`None`、NaN、通常値 |
| `B-10-024` | `load_config` のdocstringだけが異なる | 設定読込の焦点を保ち、戻り値と例外の完全版へ導く | `scripts/ch10/config_example.py:load_config` | E1 | 正常YAML、空、構文エラー、欠落 |
| `B-10-028` | `load_min_quality` のdocstringだけが異なる | `from exc` による例外連鎖の意図は実体の既存コメントで充足しているため、重複追加せず完全版へ導く | `scripts/ch10/error_handling.py:load_min_quality` | E1 | 正常な数値文字列、変換不能文字列での `BiofilterError`、`__cause__` が `ValueError` |
| `B-10-031` | cleanup例のdocstringだけが異なる | `finally` の焦点を保ち、資源解放の保証を実体にも明示する | `scripts/ch10/error_handling.py:count_records_with_cleanup` | E1 | 正常、途中例外、close呼出し |

### 5.4 ch12: 数値・表形式データ処理

| ID | 現在の差 | 教育・同期方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-12-001` | 本文名とprivateなベンチマーク関数名が異なり、実体に直接テストがなく `print()` ログがある | loggingへ直して実体を `gc_contents_slow` へ改名し、直接テスト後に本文へ同期する | `scripts/ch12/plot_vectorize_bench.py:_gc_per_base_loop` | E0 | 値、空入力、ベンチマーク呼出し、ログ |
| `B-12-003` | 本文名とprivateなNumPy関数名が異なり、実体の局所型と直接テストがない | 実体を `gc_content_per_seq` へ改名し局所型を補って直接テスト後、本文へ同期する | `scripts/ch12/plot_vectorize_bench.py:_gc_per_seq_numpy` | E0 | 軸、形状、値、空入力、dtype、ベンチマーク呼出し、mypy |
| `B-12-004` | docstringが異なり、実体の局所配列に型注釈がない | 局所型を実体と本文へ同期し、ベクトル化の既存コメントを維持する | `scripts/ch12/numpy_vectorize.py:gc_content_vectorized` | E1 | 等長・不等長、空リスト、空文字列混在、大小文字、N、shape `(n,)`、`float64`、mypy |
| `B-12-005` | `normalize_cpm` のdocstringだけが異なる | 列和とゼロ除算を示す既存コメントを維持する | `scripts/ch12/numpy_vectorize.py:normalize_cpm` | E1 | 列和、ゼロ列、形状、dtype |
| `B-12-006` | `filter_by_quality` のdocstringだけが異なる | マスクの軸と閾値包含を実体にも明示する | `scripts/ch12/numpy_vectorize.py:filter_by_quality` | E1 | 閾値未満・一致・超過、空配列 |
| `B-12-007` | `load_deg_results` のdocstringだけが異なる | 必須列とNA型の説明を完全版へ集約し、本文から導く | `scripts/ch12/pandas_bio_ops.py:load_deg_results` | E1 | 必須列、欠落列、NA、dtype |
| `B-12-008` | `filter_significant_genes` のdocstringだけが異なる | 複合マスクと閾値包含を実体にも明示する | `scripts/ch12/pandas_bio_ops.py:filter_significant_genes` | E1 | p値・効果量の各境界、NA |
| `B-12-009` | `merge_with_metadata` のdocstringだけが異なる | 結合キーと行保持の前提を実体にも明示する | `scripts/ch12/pandas_bio_ops.py:merge_with_metadata` | E1 | 一致・不一致・重複キー |
| `B-12-010` | `summarize_by_category` のdocstringだけが異なる | 集約列とカテゴリ欠損の扱いを実体にも明示する | `scripts/ch12/pandas_bio_ops.py:summarize_by_category` | E1 | 複数群、単一群、NAカテゴリ |
| `B-12-014` | `compare_expression` のdocstringだけが異なる | 検定の入力仮定と戻り値を完全版へ集約する | `scripts/ch12/scipy_stats_bio.py:compare_expression` | E1 | 正常、短い群、定数群、NaN |
| `B-12-015` | docstringが異なり、実体の結果配列に型注釈がない | 局所型を実体と本文へ同期し、BH法の既存コメントを維持する | `scripts/ch12/scipy_stats_bio.py:correct_pvalues` | E1 | 未整列、同値、0・1、空入力、mypy |
| `B-12-016` | `correct_pvalues_scipy` のdocstringだけが異なる | ライブラリ版の入出力対応を完全版へ集約する | `scripts/ch12/scipy_stats_bio.py:correct_pvalues_scipy` | E1 | 自作版との一致、0・1、空入力 |
| `B-12-017` | `distance_matrix_naive` のdocstringだけが異なる | 二重ループを比較基準として残す理由を実体にも明示する | `scripts/ch12/scipy_stats_bio.py:distance_matrix_naive` | E1 | 対称性、対角0、単一行、空入力 |
| `B-12-018` | `expression_distance_matrix` のdocstringだけが異なる | 距離関数と行方向の意味を実体にも明示する | `scripts/ch12/scipy_stats_bio.py:expression_distance_matrix` | E1 | naive版との一致、形状、単一行 |

### 5.5 ch13・ch17: 可視化と性能

| ID | 現在の差 | 教育・同期方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-13-002` | `gc_histogram` のdocstringだけが異なる | 描画APIの焦点を保ち、軸・戻り値の完全版へ導く | `scripts/ch13/matplotlib_bindist.py:gc_histogram` | E1 | Axes再利用、bin数、空入力、ラベル |
| `B-13-003` | `volcano_plot` のdocstringだけが異なる | `np.select` の分類条件と閾値を実体にも明示する | `scripts/ch13/bio_plots.py:volcano_plot` | E1 | 上昇・下降・非有意、閾値、Axes |
| `B-13-004` | `expression_heatmap` のdocstringだけが異なる | 行列の軸とクラスタリング条件を実体にも明示する | `scripts/ch13/bio_plots.py:expression_heatmap` | E1 | 行列形状、ラベル、空入力、戻り値 |
| `B-17-016` | `normalize_tpm_slow` のdocstringだけが異なる | RPKとTPM分母を示す既存コメントを維持する | `scripts/ch17/profiling_demo.py:normalize_tpm_slow` | E1 | 合計、長さ0、空入力、fast版との一致 |
| `B-17-029` | `normalize_tpm_fast` のdocstringだけが異なる | ブロードキャストの軸を示す既存コメントを維持する | `scripts/ch17/profiling_demo.py:normalize_tpm_fast` | E1 | slow版との一致、形状、長さ0 |
| `B-17-030` | 並列関数の対応がなく、単体関数だけを追跡している | 2関数を個別対応し、順序保持とフォールバックの既存コメントを維持する | `scripts/ch17/parallel_gc.py` | E1 | 並列・逐次一致、順序、空入力、例外 |
| `B-17-032` | 3関数の定義名と2関数の型注釈がなく、本文だけ空品質値でゼロ除算し、呼出例が `Path("reads.fastq")` を固定している | 空品質値ガードのテストを実体へ追加後、本文へガードと型を同期して3関数を個別対応する。呼出例は新規定義を増やさず、呼び出し元から受け取った `path: Path` を使う抜粋へ変更する | `scripts/ch17/generator_fastq.py` | E1 | 正常・途中切れFASTQ、空品質値、長さ・品質境界、遅延評価、固定パス不在 |
| `B-17-038` | Parquet保存関数の対応がなく、CSVだけを追跡している | 2関数を個別対応し、比較する形式と索引条件を同期する | `scripts/ch17/file_format_bench.py` | E1 | CSV・Parquet再読込、index、型、欠損 |
| `B-17-039` | 本文だけ別名で、ch02の実体を再実装している | ch02の公開名・実装へ完全同期し、章横断の再利用を明示する | `scripts/ch02/fastq_gzip.py:count_reads_in_gzip` | E0 | gzip正常系、空、4行未満、複数レコード |

### 5.6 ch21: 協働支援

| ID | 現在の差 | 教育・同期方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-21-004` | `collect_environment` だけが対応し、質問整形はスタブである | 2定義を個別対応し、省略境界を明示する | `scripts/ch21/format_question.py` | E2 | 環境収集、質問整形、未導入パッケージ |
| `B-21-007` | `check_type_hints` のdocstringだけが異なる | レビュー観点の焦点を保ち、完全版へ導く | `scripts/ch21/review_helper.py:check_type_hints` | E1 | 型あり・なし、インデント、混在 |
| `B-21-012` | `parse_git_log` だけが対応し、報告生成はスタブである | 2定義を個別対応し、省略境界を明示する | `scripts/ch21/progress_report.py` | E2 | 正常行、空行、不正行、報告生成 |
| `B-21-014` | `validate_metadata` のdocstringだけが異なる | 検証条件とエラー集約の意図を実体にも明示する | `scripts/ch21/analysis_intake.py:validate_metadata` | E1 | 空、列欠落、空セル、複数エラー |

## 6. 実装バッチ

1バッチにつき1ブランチ・1PRとし、前のPRがマージされた後に次を開始する。各PRでは
対象IDの修正、テスト、本文同期、対応表再生成を同じ変更単位に含める。
`remediation_scope.completed_batch` を0から5へ1ずつ進め、固定fixtureの当該バッチ期待値
と照合する。最終56関係の全件一致はバッチ5で必須とし、途中バッチでは完了済みIDを
最終関係、未完了IDを直前状態として検証する。

| 順序 | ブランチ案 | 対象 | 件数 | E1推移 | 主な作業 |
|---|---|---|---:|---:|---|
| 1 | `revise/e1-ch01-ch03` | ch01、ch03 | 4 | 45→43 | SeqIO化、スタブ対応、再現性関数、監査スキーマ4、goldset再層化、検査ゲート |
| 2 | `revise/e1-ch08-ch10` | ch08、ch09、ch10 | 14 | 43→42 | TDD段階と抜粋の区別、誤対応削除、コメント同期 |
| 3 | `revise/e1-ch12` | ch12 | 14 | 42→40 | 直接テスト新設、private関数2件の改名、logging化 |
| 4 | `revise/e1-ch13-ch17` | ch13、ch17 | 9 | 40→39 | 複数定義対応、空品質値、章横断再利用 |
| 5 | `revise/e1-ch21` | ch21 | 4 | 39→37 | スタブ境界と複数定義対応 |

### 6.1 各バッチの開始条件

- `main` が直前PRのマージコミットを含む
- GitHubで「Create a merge commit」を選択でき、前PR本文に記録したsource・生成物コミットが `origin/main` から到達できる
- 作業ツリーに対象外の未コミット変更がない
- 対応表を一時領域へ再生成・監査し、前バッチの予定件数と一致する
- 前バッチのCIがすべて成功している

### 6.2 各バッチの停止条件

次の場合は本文や実体の変更を続けず、計画の改定PRを先に作る。

- 対象ブロックの配置判定が固定fixtureの基準値と異なる。基準値は41件が `required_scripts`、`B-08-001`、`B-08-003`、`B-08-006`、`B-08-009` の4件が `required_tests` である
- 予定したE0、E1、E2では観測可能な動作差を説明できない
- 公開関数の改名が章外の利用者や互換性へ影響する
- コメント同期のためにAPI、計算式、例外仕様の変更が必要になる
- `comment_sync` の実測状態が§3.2の最終期待状態と異なる
- 対応表の総数、配置必須数、EN数が件数保存則から外れる
- 対象外の構造findingまたは相互参照findingが増える

### 6.3 新設・拡張する直接テスト

| バッチ | テスト | 対象 |
|---|---|---|
| 1 | `tests/ch01/test_seq_filter.py` を拡張 | `parse_fasta_string` が `Bio.SeqIO` を使い、複数行配列、空行、空入力を扱う |
| 1 | `tests/review/test_check_xref.py` を新設または同等テストを追加 | `../scripts/` と `../tests/` の実在・欠落を検出する |
| 1 | `tests/review/test_check_structure.py` を新設または同等テストを追加 | 基準JSONとの `file/type/message` 集合差を取り、新規finding時の非0終了を検証する |
| 1 | `scripts/review/finalize_e1_artifacts.py`、`scripts/review/build_e1_batch0_state.py`、`scripts/review/check_e1_transition.py`、`scripts/review/check_e1_source_scope.py`、`scripts/review/run_e1_batch_gates.py`、`scripts/review/check_e1_merged_state.py`、`scripts/review/create_e1_pr.py` と各テストを新設 | スキーマ3から決定的なバッチ0遷移状態を作り、前後バッチの単調遷移を検査する。バッチ別対象pytest・mypyのコマンドを一元管理し、source範囲、対象・全体pytest、Ruff、差分、文書検査、生成・監査の全成功後だけ4生成物をstage・commitする。PR helperは非mainブランチをpushし、remote OID一致後だけ明示headでPRを作成し、返却URLから番号を固定する。headの読み取り検査後だけPR本文へ固定マーカーを1件設定する。マージ後は一時worktreeの内容を独立監査する。各ゲート失敗時のHEAD・index・作業ツリー不変を一時Gitリポジトリで検証する |
| 1 | `tests/review/fixtures/e1_expected_relations.json` を新設 | 最終56関係のsource・target・2判定と45件のコメント終端状態・意味アンカー、バッチ0〜5の完了ID・E件数・関係件数・終端/`pending` ID・基準placement、バッチ1〜5の完全列挙したsource許可パスを固定する |
| 1 | `tests/review/test_code_correspondence.py` と監査テストを拡張 | スキーマ4、完了バッチ別scope、goldset各2件、完了済みIDのsource・target対応、中間期待値、45 IDの基準placement完全一致、Git treeとoverrideを含むsnapshotを検証する。placement総数を保った相互入替も失敗させる |
| 1 | `tests/review/test_correspondence_provenance.py` を新設 | 未コミットsourceでの生成失敗、Git tree改変検出、第2コミットの親と変更パス制限、artifact自動発見の0件・複数件、マージ後の両コミット到達可能性、PR JSONの番号・OPEN/MERGED状態・head・merge commit、本文マーカーの欠落・重複・不正・ID不一致を検証する |
| 1 | `tests/review/test_e1_transition.py` を新設 | スキーマ3からのバッチ0生成の決定性、バッチ1〜5の許可遷移、既完了レコードのdeep equalityを検証する。早期完了、遅延、逆戻り、終端変更、余分なpendingフィールド、既完了証拠の書換えを失敗させる |
| 1 | `tests/review/test_create_e1_pr.py` を新設 | `main`・detached HEADの拒否、push、remote head OID、明示head付き `gh pr create` の順序、`prepared` 状態、返却URL解析、明示番号のOPEN・base・head事前検査、PR本文の他の記述を保持した固定マーカー設定、既存マーカーの重複・不正を検証する。push失敗・remote OID不一致時はPR作成を呼ばず、番号・head不一致時は本文更新を呼ばない。作成失敗後の完全一致検索0件・1件・複数件、`gh pr view`、JSON解析、本文更新の各失敗後に再開してもPRが増えないことを固定する |
| 1 | `tests/review/test_e1_merged_state.py` を新設 | `origin/main` 相当の一時worktreeでバッチ0〜5の独立監査・fixture一致を検証し、競合解消によるsource改変、E件数・関係・コメント同期・goldset・snapshotの不一致を検出する |
| 2 | `tests/review/test_mypy_examples.py` を新設または同等テストを追加 | `B-08-019` の本文スニペットを一時ファイルでmypyに渡し、非0終了と期待診断を検証する |
| 3 | `tests/ch12/test_plot_vectorize_bench.py` を新設 | 改名する2関数の値、空入力、dtype、ベンチマーク呼出し、logging |
| 4 | `tests/ch17/test_generator_fastq.py` を拡張 | 品質値が空のレコードを例外なく除外する |
| 4 | `tests/review/test_e1_policy_examples.py` を新設または同等テストを追加 | `B-17-032` の呼出例に固定パスがなく、呼び出し元の `path: Path` を使うことをASTで検証する |

fixtureの `batches.<n>.allowed_source_paths` はglobやディレクトリ単位ではなく、本文、
実体、テスト、override、レビュー用ツールを相対ファイルパスで完全列挙する。
`check_e1_source_scope.py` は `baseline_ref..source_commit` の変更集合がこの集合の部分集合
であること、コミット済みsource treeと作業ツリーの追跡対象が一致すること、source対象
ルート内に新規untrackedがないことを検査し、違反時は非0終了する。開始前からある
対象外の `sandbox/` などは検査対象へ含めず、変更・削除しない。

`audit_code_correspondence.py` は各バッチで、固定45 IDのplacementがfixtureの
41件 `required_scripts`・4件 `required_tests` とID単位で完全一致することを検査し、
不一致なら非0終了する。合計件数だけは用いない。finalizerはこの独立監査を
生成物反映前の必須ゲートとして呼び、`check_e1_merged_state.py` も一時worktreeで
同じ完全一致を再検査する。

artifactリンク検査は最初の実装バッチで `scripts/review/check_xref.py` へ追加し、
以後のバッチで共通ゲートとして使う。章・節・図の既存検査を弱めず、
`../scripts/` と `../tests/` の通常ファイルおよびディレクトリリンクを検証する。
findingが1件以上ならJSONを書いた後に非0終了させる。追跡済み検査JSONはソース
コミット後に更新し、対応表と同じ第2コミットへ含める。

構造検査には `--baseline` を追加し、基点JSONとの `file/type/message` の集合差を
検査する。行番号は本文の加筆で移動するため安定キーから除外する。新規集合が1件以上
ならJSONを書いた後に非0終了させる。既存findingの解消は許容するため、総数27への
完全一致だけをゲートにはしない。

### 6.4 各PRのマージ条件

sourceコミットと生成物コミットの親子関係をマージ後も監査可能にするため、5つの
実装PRはGitHubの「Create a merge commit」でマージする。squash mergeとrebase mergeは
選択しない。各PRのマージ直後に両コミットが `origin/main` から到達可能で、merge後の
内容が当該バッチfixtureと一致することを検査する。選択可能なマージ方式が変わった場合は、
そのPRをマージせず計画改定へ戻る。
finalizerはsource・生成物コミットIDをJSONで出力する。`create_e1_pr.py` は非mainの
現在ブランチをpushし、remote head OIDが生成物コミットと一致した場合だけ
明示headで `gh pr create` を呼ぶ。作成前の `prepared` 状態と返却URLから得たPR番号を
状態ファイルへ保存し、後続失敗時は同じ番号の `resume` モードで再開する。明示番号の
読み取り専用JSONがOPENでbase・head・`headRefOid` が期待値と一致した後だけ、PR本文の
「provenance」欄へ番号と両IDを上記のHTMLコメント形式で1回記録する。マージ前に
provenance検査器でも同じJSONを再検査する。マージ後の機械検査では、明示的に
引き継いだPR番号、対応表のsource ID、Git履歴から一意に発見した生成物ID、PRの
head・merge commit・本文マーカーを照合する。

### 6.5 マージ後の共通検査

各PR作成時に、PR番号を作業記録とユーザーへの引き継ぎへ明記する。各バッチのマージ後に
その番号を `E1_PR_NUMBER` として§7.6を実行する。バッチ1〜4は次バッチの開始条件、バッチ5は
E1解消全体の最終完了条件である。したがって、バッチ5のPRがマージされただけでは
本計画を完了扱いにしない。

## 7. 検証手順

### 7.1 バッチ開始時の一時監査

バッチ2〜5では、対応表に記録された前PRのsourceコミットを使い、merge commit後も
sourceと一意に発見した生成物コミットの双方が `origin/main` から到達可能であることを
先に検査する。バッチ1ではこの部分を省略する。

```bash
set -euo pipefail
git fetch origin main
e1_previous_source_commit=$(
  jq -er '.source_commit' docs/review/code_correspondence.json
)
python3 scripts/review/check_correspondence_provenance.py \
  --source-commit "$e1_previous_source_commit" \
  --artifact-commit auto \
  --main-ref origin/main \
  --require-reachable
```

続いて追跡済み対応表を上書きせず、基準テスト結果を再利用して一時領域へ生成する。

```bash
set -euo pipefail
e1_review_dir=$(mktemp -d /private/tmp/ai-biocode-kata-e1.XXXXXX)
.venv/bin/python scripts/review/build_code_correspondence.py \
  --root . \
  --output "$e1_review_dir/code_correspondence.json" \
  --report "$e1_review_dir/code_correspondence.md" \
  --reuse-test-results docs/review/code_correspondence.json \
  --check-determinism
.venv/bin/python scripts/review/audit_code_correspondence.py \
  --root . \
  --input "$e1_review_dir/code_correspondence.json" \
  --report "$e1_review_dir/code_correspondence.md"
```

### 7.2 対象テスト

各バッチでは対象章のテストを先に実行する。ch17の章横断再利用ではch02も含める。
バッチ1で新設する共通ランナーは、固定fixtureと同じ1〜5の対応表から該当する
1コマンドだけを選び、未該当バッチや空の対象を非0終了にする。

```bash
set -euo pipefail
e1_batch=$(
  jq -er '.review_metadata.remediation_scope.completed_batch' \
    scripts/review/code_correspondence_overrides.json
)
python3 scripts/review/run_e1_batch_gates.py \
  --batch "$e1_batch" \
  --gate target-pytest
```

### 7.3 全体・静的検査

```bash
set -euo pipefail
.venv/bin/pytest -q -p no:cacheprovider
.venv/bin/ruff check scripts tests
e1_batch=$(
  jq -er '.review_metadata.remediation_scope.completed_batch' \
    scripts/review/code_correspondence_overrides.json
)
python3 scripts/review/run_e1_batch_gates.py \
  --batch "$e1_batch" \
  --gate mypy
.venv/bin/mypy --follow-imports=skip --ignore-missing-imports \
  scripts/review tests/review
git fetch origin main
e1_base=$(git merge-base HEAD origin/main)
python3 scripts/review/check_e1_source_scope.py \
  --batch "$e1_batch" \
  --baseline-ref "$e1_base" \
  --worktree
git diff --check "$e1_base"
git diff --name-only "$e1_base"
git status --short
```

共通ランナーが選ぶ章別mypyは、ch01・ch03、ch08〜ch10、ch02・ch13・ch17、ch21では成功し、
ch12だけ3 errorsである。ch12の3件は `B-12-003`、`B-12-004`、`B-12-015` の
局所配列型であり、同バッチで実体と本文を同期して0件にする。新しい除外を追加して
成功扱いにしない。変更するレビュー用ツール・テストも全バッチで型検査する。
基準状態では、バッチ1で拡張する `check_structure.py` と `check_xref.py` に局所変数の
型注釈不足が各1件あるため、機能拡張時に型を補い、以後0件を維持する。除外で隠さない。
ランナーの単体テストでは、各バッチが選ぶpytest・mypyの引数、未知のバッチ・gateの
拒否、子プロセスの非0終了伝播を固定する。

### 7.4 対応表と文書検査

```bash
set -euo pipefail
git fetch origin main
e1_base=$(git merge-base HEAD origin/main)
e1_source_commit=$(git rev-parse HEAD)
e1_batch=$(
  jq -er '.review_metadata.remediation_scope.completed_batch' \
    scripts/review/code_correspondence_overrides.json
)
python3 scripts/review/finalize_e1_artifacts.py \
  --batch "$e1_batch" \
  --baseline-ref "$e1_base" \
  --transition-baseline-ref 27adae7b658754626d097a233540edbc75af39c5 \
  --previous-ref origin/main \
  --source-commit "$e1_source_commit"
python3 scripts/review/check_e1_transition.py \
  --batch "$e1_batch" \
  --transition-baseline-ref 27adae7b658754626d097a233540edbc75af39c5 \
  --previous-ref origin/main \
  --current docs/review/code_correspondence.json
python3 scripts/review/check_correspondence_provenance.py \
  --source-commit "$e1_source_commit" \
  --artifact-commit HEAD
```

`check_xref.py` はバッチ1で拡張したartifactリンク検査を含む。対応表生成コマンドは
実体、テスト、本文、overrideをソースコミットにした後だけ追跡済み出力へ実行する。
`check_structure.py` と `check_xref.py` も同じソースコミットを対象に実行し、4生成物
`code_correspondence.json`、`code_correspondence.md`、`structure_check.json`、
`xref_check.json` の変更だけを第2コミットへ含める。生成前の作業ツリーで実行する
場合は、すべて一時出力を指定する。構造検査は基点の `structure_check.json` と
`file/type/message` 集合を比較し、新規findingがない場合だけ成功する。生成器は
snapshot対象が `e1_source_commit` のGit treeと一致しなければ失敗する。provenance
検査は、第2コミットの変更が上記4生成物の部分集合だけであり、対応表JSON・Markdownを
必ず含むことを確認する。内容が不変の検査JSONは第2コミットに現れなくてよい。

`finalize_e1_artifacts.py` は、HEADとsourceコミットの一致、バッチ別source許可範囲、
共通ランナーによる対象章pytest、全体pytest、Ruff、共通ランナーによる当該バッチのmypy、
レビュー用ツール・テストのmypy、基点からsourceまでの
`git diff --check`、構造検査、相互参照検査、対応表の決定的生成、前バッチからの単調遷移、
独立監査をこの順に実行する。バッチ1の比較元は固定基準refから再生成したバッチ0状態、
バッチ2〜5は `previous-ref` のスキーマ4対応表とする。検査JSONと対応表は一時領域へ
生成・監査し、いずれかが非0ならHEAD、index、追跡済み作業ツリーを変えずに停止する。
すべて成功した場合だけ一時生成物を4つの追跡先へ反映し、再度 `git diff --check` と
許可生成物以外の差分不在を検査してからstageし、
`docs: refresh E1 correspondence artifacts` としてコミットする。sourceコミットは
Git treeをsnapshotの基準にするため事前に作る唯一のコミットであり、手順6の全ゲート
成功後に限って作成する。finalizerは同じゲートをコミット済みtreeで再実行する。

一時Gitリポジトリを使う統合テストでは、source範囲、対象・全体pytest、Ruff、各バッチと
レビュー用コードのmypy、差分、構造、相互参照、生成、独立監査の各失敗を注入し、いずれの場合もHEAD、
index、追跡済み作業ツリーが不変であることを確認する。

### 7.5 PR作成・マージ前のprovenance検査

finalizer成功後、変更内容・根拠・検証結果を含むPR本文ファイルを準備する。
`create_e1_pr.py` は `create` と `resume` の2モードを持つ。`create` は、現在ブランチが
引数 `--head` と一致し、`main` でもdetached HEADでもないことを先に検査する。続いて
`git push --set-upstream origin HEAD` を実行し、
`git ls-remote --heads origin refs/heads/<head>` のOIDが `artifact_commit` と一致した
場合だけ、`gh pr create --head <head>` を呼ぶ。push失敗またはremote OID不一致なら、
`gh pr create` を呼ばず非0終了する。

PR作成前に、base、head、source・artifactコミットと `status: prepared` を
`--state-file` へ排他的かつatomicに保存する。状態ファイルがすでに存在する場合、
`create` はまず保存済みbase・head・artifact OIDを使う完全一致検索を行い、PRを
盲目的に再作成しない。一致するOPEN PRが1件ならその番号を保存して `resume` へ進み、
0件なら作成を再試行し、複数件または検索失敗なら状態を保持したまま停止する。
現在ブランチからの推測は使わない。
PR作成後は返されたURLから番号を解析し、他の外部呼出しより前に番号を標準エラーへ
出力して、同じ状態ファイルを `status: created` とPR番号付きでatomic更新する。URL解析・
更新に失敗しても `prepared` が残り、次回の完全一致検索または出力済み番号を指定する
`resume --pr-number <番号>` で復旧する。`create` は保存後に `resume` と同じ処理を
続けるため、後続処理が失敗しても状態ファイルとPR番号が残る。

`resume` は状態ファイルの番号、または `prepared` から復旧するときの明示
`--pr-number` だけを使い、pushも `gh pr create` も呼ばない。
明示番号で取得したJSONの `number`、OPEN状態、`baseRefName`、`headRefName`、
`headRefOid == artifact_commit` を本文更新前に検査する。一致した場合だけ既存本文を
保持して固定マーカーを1件追加する。マーカーがすでに同じ内容なら成功として扱い、
欠落時だけ追加し、不一致・重複時は本文を変更せず失敗する。`gh pr view` 失敗、
JSON不正、本文更新失敗でも状態ファイルを残し、再度 `resume` できる。出力したPR番号は
ユーザーへのマージ依頼にも明記し、マージ後の `E1_PR_NUMBER` へそのまま引き継ぐ。

```bash
set -euo pipefail
: "${E1_PR_TITLE:?PRタイトルを指定する}"
: "${E1_PR_BODY_FILE:?変更内容・根拠・検証結果を含む本文ファイルを指定する}"
e1_head_branch=$(git symbolic-ref --quiet --short HEAD)
test "$e1_head_branch" != main
e1_source_commit=$(
  jq -er '.source_commit' docs/review/code_correspondence.json
)
e1_artifact_commit=$(git rev-parse HEAD)
e1_batch=$(
  jq -er '.remediation_scope.completed_batch' docs/review/code_correspondence.json
)
e1_pr_state_file=".git/e1-pr-batch-${e1_batch}.json"
if ! python3 scripts/review/create_e1_pr.py \
    create \
    --base main \
    --head "$e1_head_branch" \
    --title "$E1_PR_TITLE" \
    --body-file "$E1_PR_BODY_FILE" \
    --source-commit "$e1_source_commit" \
    --artifact-commit "$e1_artifact_commit" \
    --state-file "$e1_pr_state_file"
then
  jq -e '.pr_number' "$e1_pr_state_file" >/dev/null
  python3 scripts/review/create_e1_pr.py \
    resume \
    --body-file "$E1_PR_BODY_FILE" \
    --state-file "$e1_pr_state_file"
fi
E1_PR_NUMBER=$(jq -er '.pr_number' "$e1_pr_state_file")
e1_pr_json=$(
  gh pr view "$E1_PR_NUMBER" \
    --json number,state,body,baseRefName,headRefName,headRefOid,mergeCommit
)
python3 scripts/review/check_correspondence_provenance.py \
  --source-commit "$e1_source_commit" \
  --artifact-commit "$e1_artifact_commit" \
  --expected-pr-json "$e1_pr_json" \
  --expected-pr-state OPEN
```

### 7.6 マージ後の到達可能性・内容検査

各バッチのmerge commit作成後、追跡済み対応表を `origin/main` のtreeから読み、
そこに記録されたsourceコミットと、Git履歴から一意に見つかる生成物コミットの双方を
検査する。作業ブランチ上の古い対応表は参照しない。`E1_PR_NUMBER` はPR作成時に
記録・引き継いだ値を明示的に指定し、現在のブランチからPRを推測しない。

```bash
set -euo pipefail
: "${E1_PR_NUMBER:?PR作成時に記録した番号を指定する}"
git fetch origin main
e1_merged_source_commit=$(
  git show origin/main:docs/review/code_correspondence.json |
    jq -er '.source_commit'
)
e1_pr_json=$(
  gh pr view "$E1_PR_NUMBER" \
    --json number,state,body,baseRefName,headRefName,headRefOid,mergeCommit
)
python3 scripts/review/check_correspondence_provenance.py \
  --source-commit "$e1_merged_source_commit" \
  --artifact-commit auto \
  --main-ref origin/main \
  --require-reachable \
  --expected-pr-json "$e1_pr_json" \
  --expected-pr-state MERGED

e1_merge_commit=$(printf '%s\n' "$e1_pr_json" | jq -er '.mergeCommit.oid')
e1_previous_main=$(git rev-parse "${e1_merge_commit}^1")
e1_batch=$(
  git show origin/main:docs/review/code_correspondence.json |
    jq -er '.remediation_scope.completed_batch'
)
e1_merged_dir=$(mktemp -d /private/tmp/ai-biocode-kata-e1-merged.XXXXXX)
git worktree add --detach "$e1_merged_dir/repo" origin/main
trap 'git worktree remove --force "$e1_merged_dir/repo"' EXIT
.venv/bin/python \
  "$e1_merged_dir/repo/scripts/review/check_e1_merged_state.py" \
  --root "$e1_merged_dir/repo" \
  --batch "$e1_batch" \
  --transition-baseline-ref 27adae7b658754626d097a233540edbc75af39c5 \
  --previous-ref "$e1_previous_main" \
  --expected-ref origin/main
```

`check_e1_merged_state.py` は一時worktreeのHEADが `origin/main` と一致することを確認し、
そのtreeだけを対象に対応表の独立監査と当該バッチfixture照合を行う。PRのmerge commitの
第1親を直前mainとして、バッチ0または直前スキーマ4成果物からの単調遷移と既完了
レコードのdeep equalityも再検査する。バッチ1〜4では `completed_batch`、中間E件数、
関係集合・2集計、完了ID、45 IDの基準placement完全一致、コメント同期確定ID、goldset、
snapshotを検査する。バッチ5ではさらに基準45 ID、最終E件数55/37/42/0/0/395、
56関係の全件と2集計、45件の `comment_sync` を検査する。競合解消や後続変更で
source snapshotが変わった場合も失敗する。

バッチ1〜4はこの成功後に次のブランチを作る。バッチ5はこの成功後にだけE1作業を
完了とする。

再生成後は、少なくとも次を独立監査する。

- 基準45 IDの集合差が空である
- 各IDの目標判定と実測判定が一致する
- 固定した45 IDのModule直下56定義についてsource・target ID、名前、位置が解決し、各source・target定義が原則1回だけ現れる
- 56関係の親ブロック判定別内訳が4/43/9、関係自身の判定別内訳が4/46/6でfixtureと一致する
- goldsetが各判定2標本で、E1標本が `B-01-001` と `B-12-004` である
- スキーマ4、method、scope、snapshot対象リストが記録され、Git tree、未コミットsource、override改変を監査できる
- E0 + E1 + E2 = 134、EN = 395、全体 = 529である
- E3、E4、E5が0件である
- E1 37件の証拠に教育目的と完全実体への導線が記録されている
- 変更対象の実体テストが成功し、テスト結果が対応表に反映されている
- E0・E1関係は、同じ入力で本文コードと実体の戻り値、例外、副作用が一致する
- E2関係は、省略境界、対応実体、実体テストが解決し、本文の説明が実体と矛盾しない
- E2親ブロック内の `equivalence: E1` 3関係は、関係単位で動作が一致する
- `B-17-032` の呼出例に固定パスがなく、新規定義を増やさず最終56関係を維持する

## 8. リスクと対策

### 8.1 E0のために説明力を落とす

本文の短いdocstringへ実体を合わせると、APIドキュメントと単独利用時の説明力が
低下する。E0の数を増やすこと自体を目的にせず、豊富なdocstringを維持する。

### 8.2 コメントの二重管理

同じ文章を逐語的に複製すると、将来どちらかだけが更新される。同期対象は意味分類で
決め、章依存の説明は本文、実装判断は実体という役割を明確にする。

### 8.3 TDDの時間軸を壊す

ch08を完成実体へ完全同期すると、Red、Green、Refactorの段階が見えなくなる。段階例は
E1として残し、各段階の目的と最終実体への導線を明示する。

### 8.4 private関数の改名による見落とし

ch12の2関数はprivate名だが、ベンチマーク、テスト、文書から参照される可能性がある。
`rg` で全参照を列挙し、実体とテストを先に改名してから本文を同期する。

### 8.5 ブロック判定と関係判定の混同

複数定義ブロックでは、一部がE1でもスタブがあればブロック全体はE2となる。関係単位の
証拠を残したうえで、ブロック判定は最も大きな省略を反映する。

## 9. 計画レビュー記録

計画のレビューは、対象集合、分類方針、実装可能性、検証可能性、独立監査の順に行う。
findingには重要度、影響ID、修正内容を記録し、修正後は前巡とは異なる観点で再レビュー
する。新規findingが0件になるまで計画を確定しない。

### 第1巡: 対象集合と件数保存則

基準対応表との集合一致、重複、目標判定の算術、実施単位の件数推移をレビューした。

- 解消マトリクスは45件、重複0件で、基準対応表のE1集合と完全一致した
- 目標内訳はE0 4件、E1 38件、E2 3件で、合計45件であった
- 実施単位は4 + 14 + 14 + 9 + 4 = 45で、E1の予定推移と一致した

| ID | finding | 対応 |
|---|---|---|
| P1 | E1の定義にコメント差を含めていたが、対応表ではコメントはE0判定時から除外される | E1の定義からコメントを外し、コメント同期は判定と独立した読者支援であると明記 |
| P2 | 定義単位の不足を「5ブロック」としたが、列挙は6ブロックであった | 6ブロックへ訂正し、後続の自己訂正文を削除 |
| P3 | E0予定の完了条件がコメントの文字列一致を要求し、意味ベースの同期原則と矛盾した | E0はコメント・空白を除くAST完全一致、コメントは意味分類による同期へ訂正 |
| P4 | 教育的コメントを45件と数えていたが、45はブロック数でありコメント数ではない | 「対象45ブロックに含まれるコメント」へ訂正 |

4 findingsを反映した。次巡では、45件の本文前後と実体を教育目的、完全版への導線、
コメントの意味分類、TDDの時間軸という観点でレビューする。

### 第2巡: 教育目的とコメント同期

全45件について本文コード、実体の定義、docstring、コメントを比較し、TDDの時間軸、
コメントの重複、実体APIの責務とテスト項目をレビューした。

| ID | finding | 対応 |
|---|---|---|
| P5 | `B-08-001` のRed段階を現行リポジトリで失敗させるようにも読めたが、現行実体は完成済みである | 現行テストは成功を確認し、Redは実装前という時間軸と失敗理由の説明整合性を確認する形へ訂正 |
| P6 | `B-17-032` に「4行単位」の検証を要求したが、実体は行を自作解析せず `Bio.SeqIO` でレコードを遅延取得する | 正常・途中切れFASTQ、フィルター境界、遅延評価の検証へ訂正 |
| P7 | `B-21-007` に構文エラー検証を要求したが、実体は構文解析器ではなく追加行の簡易パターン検査である | 型あり・なし、インデント、混在という実際の責務へ訂正 |
| P8 | どの教育的コメントを追加し、どれを既存説明で充足するかが監査できなかった | 初回候補を追加4件、既存充足7件、追加なし34件に分類し、各実装PRで処置を記録する規則を追加 |

4 findingsを反映した。次巡では、実装順、既存参照への影響、テストコマンド、対応表生成の
コミット順、各PRの独立性をレビューする。

### 第3巡: 実装順序とテスト可能性

実体の全参照、既存テスト、ローカル実行環境、生成器の引数、対応表のコミット記録を
レビューした。Ruff、章別mypy、`tests/review/` を実行して基準状態も確認した。

- Ruffは成功した
- `tests/review/` は63 passedであった
- 章別mypyはch12以外で成功し、ch12には対象関数内の既存3 errorsがあった

| ID | finding | 対応 |
|---|---|---|
| P9 | 相互参照検査を実在しない `check_cross_references.py` と記載していた | 実在する `scripts/review/check_xref.py` へ訂正 |
| P10 | 汎用レビュー生成だけを記載し、対応表の決定的生成と独立監査コマンドがなかった | `build_code_correspondence.py --check-determinism` と `audit_code_correspondence.py` の完全なコマンドを追加 |
| P11 | リポジトリ全体のmypy成功を求めたが、現行で29 errorsがあり、そのうちch12の対象関数内に3 errorsがあった | CIと同じimport条件で変更章を検査し、ch12の3局所型を実体・本文へ同期して解消する計画へ変更 |
| P12 | ソース未コミットのまま対応表を生成すると `source_commit` が実内容より古くなる | ソースコミット後に対応表を生成する2段階コミットとsnapshot hashの扱いを追加 |
| P13 | overrideの本文ハッシュと根拠を更新する順序がなく、ハッシュだけの機械更新を許し得た | 本文差分をレビューしてからハッシュ、関係、判定、証拠を同時更新する順序を追加 |
| P14 | pytestがリポジトリへキャッシュを生成し得た | 全コマンドへ `-p no:cacheprovider` を追加 |

6 findingsを反映した。次巡では、基準対応表を読まない独立レビュアーに、分類、件数、
技術的実現性、規約適合、検証の不足を指摘させる。

### 第4巡: 独立レビュー

読み取り専用の独立レビュアーが、規約、基準対応表、全45件の本文・実体・テスト、
生成器・検査器を照合した。ID集合、章別件数、既存パスの実在性は一致したが、
9 findingsがあった。

| ID | finding | 対応 |
|---|---|---|
| P15 | `B-01-004` の完全実体が禁止事項である自作FASTAパーサを使っていた | `Bio.SeqIO.parse` へscripts先行で直し、直接テスト後にE2対応を確定する計画へ変更 |
| P16 | `B-08-006` は完成テストクラスの一部だけを示すためE1ではなくE2である | E2へ変更し、目標内訳と全バッチ推移をE0 55・E1 37・E2 42へ再計算 |
| P17 | `B-08-009` はNを含む配列の正確な期待値assertを省略していた | `2 / 5` のassertを本文へ同期してE1を維持する計画へ変更 |
| P18 | `B-17-032` は空品質値で本文だけゼロ除算し、現状は動作同一でなかった | 空品質値テストを実体へ追加後、ガードと型を本文へ同期する計画へ変更 |
| P19 | E0予定の `B-12-001`、`B-12-003` に直接テストがなかった | `tests/ch12/test_plot_vectorize_bench.py` の新設と検証項目を追加 |
| P20 | 定義単位の不足に、`target_entity` がnullのch08の4ブロックが含まれていなかった | 対象を10ブロックへ広げ、関数・クラス・メソッド単位の対応を追加 |
| P21 | 開始時再生成が追跡済み成果物を上書きし、単独 `git diff --check` はコミット済みPR差分を見ない | 開始時は一時出力、最終時は基点からHEADまでの差分・名前・状態を検査する手順へ変更 |
| P22 | ch12の変更対象実体に禁止された `print()` ログが残っていた | loggingへ先行変更し、ログを直接テストする計画へ追加 |
| P23 | 完全版への `../scripts/`・`../tests/` リンクを現行相互参照検査が見ない | バッチ1で検査器とレビュー用テストを拡張し、以後の共通ゲートに設定 |
| P24 | mypyのプレースホルダーがシェルで実行不能で、全体29 errorsの基準と記載コマンドが対応しなかった | バッチ別の実行可能な5コマンドへ置換し、変動する全体件数を削除 |
| P25 | E1関係数を47件としていたが実測は46件だった | 46件へ訂正 |

独立レビューの報告は9 findingsだが、複数論点を追跡可能にするためP16〜P18を3行に
分割し、レビュー記録上はP15〜P25の11項目として反映した。次巡では修正済み計画を
新しいセッションで最初から監査する。

### 第5巡: fresh audit

新しい読み取り専用セッションで、45 ID集合と分類、定義単位の対応、生成・監査ツール、
検証コマンドを最初から再確認した。ID集合、目標4/37/4、最終55/37/42、
バッチ45→43→42→40→39→37、基準E1関係46件は一致したが、5 findingsがあった。

| ID | finding | 対応 |
|---|---|---|
| P26 | `source_snapshot_sha256` の対象に、判定を決めるoverrideが含まれず、overrideだけが古くても監査が通り得た | 生成器と監査器のsnapshot対象へoverrideと対象集合を追加し、override改変で旧JSON監査が失敗する回帰テストを追加 |
| P27 | 関係レコードがtarget定義だけを残し、source定義の対応漏れ・重複を独立監査できなかった | source ID・名前・位置を成果物へ保持し、各source定義の1対1対応、最終56関係と4/43/9の関係内訳を完了条件へ追加 |
| P28 | artifactリンク検査がfinding時も終了コード0で、新設テストと追跡済みJSONがバッチ・コミット手順へ接続されていなかった | 非0終了、バッチ1での`tests/review/`実行、4生成物を第2コミットへ含める手順を追加 |
| P29 | `B-12-004` の「2次元・空軸」は `list[str] -> shape (n,)` の実APIと一致しなかった | 等長・不等長、空リスト、空文字列混在、大小文字、N、shape、dtypeの検証へ置換 |
| P30 | `B-08-019` の期待mypyエラーは本文にしかなく、章別mypyコマンドでは検証できなかった | 本文スニペットを一時ファイルでmypyへ渡し、非0終了と診断内容を確認するレビュー用テストをバッチ2へ追加 |

5 findingsを反映した。次巡では、修正後の計画を別のfreshセッションで再監査し、
新規finding 0件を確認する。

### 第6巡: fresh audit

さらに別の読み取り専用セッションで、45 ID集合、トップレベル定義数、goldset、
relationの2集計、Git provenance、構造検査ゲートを再確認した。45 ID、目標4/37/4、
最終55/37/42、バッチ推移、P28〜P30は一致したが、5 findingsがあった。

| ID | finding | 対応 |
|---|---|---|
| P31 | E0へ移る `B-03-019` がgoldsetのE1標本に残り、単純変更では各判定2標本の監査も壊れる | E1標本を `B-01-001` と `B-12-004` へ再層化し、変更履歴とテストをバッチ1へ追加 |
| P32 | 定義単位追跡の原則が全配置必須134件にも読め、非対象の不足5ブロックまで波及し得た | 基準E1 45ブロックのModule直下だけへ限定し、固定scopeを成果物へ記録。source・target双方の一意性を監査 |
| P33 | 親ブロック判定別4/43/9と、関係自身の判定別内訳が混同されていた | 2指標を4/43/9と4/46/6に分離し、56関係の固定fixtureを追加 |
| P34 | sourceコミットと作業ツリーsnapshotが独立で、未コミットsourceを含む生成や第2コミットへの混入を機械的に拒否できなかった | スキーマ4、Git tree照合、拡張snapshot、method/scope、2コミットprovenance検査と回帰テストを追加 |
| P35 | 構造検査が総数27だけを見ており、既存1件解消と新規1件追加を区別できなかった | `file/type/message` の基準集合差と非0終了を `--baseline` とレビュー用テストへ追加 |

5 findingsを反映した。次巡では、スキーマ4と2段階コミットの不変条件を含めて、
別のfreshセッションで再監査する。

### 第7巡: fresh audit

別の読み取り専用セッションで、45 ID、56定義、2種類の関係集計、E2の検証可能性、
失敗ゲート、マージ後のprovenance、対象コードの禁止事項を再確認した。45 ID、
目標4/37/4、最終55/37/42、バッチ推移、関係集計4/43/9と4/46/6は一致したが、
4 findingsがあった。

| ID | finding | 対応 |
|---|---|---|
| P36 | E2のスタブ・省略関係にも戻り値、例外、副作用の完全一致を無条件に要求し、達成不能だった | 動作一致をE0・E1関係へ限定し、E2は省略境界、対応実体、実体テスト、説明の非矛盾を検証する。E2親内のE1関係3件は関係単位で動作一致を要求する |
| P37 | 構造・相互参照検査が非0でも、貼り付けたコマンド列が生成物のstage・commitまで継続し得た | 全実行ブロックへ `set -euo pipefail` を追加し、全ゲート成功後だけstage・commitするfinalizerと失敗時のHEAD・index不変を確認する統合テストをバッチ1へ追加 |
| P38 | squash/rebase merge後はsource・生成物コミットの親子関係を履歴から証明できなかった | 5実装PRのマージ方式を「Create a merge commit」に限定し、両コミットの到達可能性を次バッチ開始条件と完了条件へ追加 |
| P39 | `B-17-032` の呼出例に禁止された固定パス `Path("reads.fastq")` が残る計画だった | 呼び出し元の `path: Path` を使う抜粋へ変更し、AST検査を追加する。新規定義は増やさず56関係を維持 |

4 findingsを反映した。次巡では、E2の関係別検証、finalizerの停止保証、merge commit条件、
固定パス除去を含む計画全体を別のfreshセッションで再監査する。

### 第8巡: fresh audit

別の読み取り専用セッションでP36〜P39の解消状況、45 ID、56定義、関係数とE件数の
バッチ推移を再確認した。P36とP39は解消され、45 IDと全件数も一致したが、P37・P38の
機械的接続を含む3 findingsがあった。

| ID | finding | 対応 |
|---|---|---|
| P40 | finalizerが文書・対応表ゲートだけを実行し、pytest、Ruff、mypy、差分検査の失敗前に生成物コミットを作れた | finalizerへ対象・全体pytest、Ruff、バッチ別mypy、source・生成後diff検査を統合し、全ゲート成功後だけ一時生成物を反映・commitする。sourceコミットは事前ゲート後に作る唯一の例外と明記 |
| P41 | merge commit条件はあっても、マージ後にsource・生成物コミットの到達可能性を検査する実行手順がなかった | provenance checkerへ `--main-ref`、`--require-reachable`、一意なartifact自動発見を追加し、バッチ2〜5の開始コマンド、finalizer出力、PR本文記録へ接続 |
| P42 | `git diff --name-only` と `git status` は表示だけで、バッチ外source変更を非0終了にできなかった | fixtureへバッチ別許可ファイルを完全列挙し、作業ツリーと `baseline_ref..source_commit` を検査する `check_e1_source_scope.py` をfinalizer・直接テスト・完了条件へ接続 |

3 findingsを反映した。次巡では、全ゲート前commit禁止、artifact自動発見と到達可能性、
バッチ別source許可集合の非0ゲートを別のfreshセッションで再監査する。

### 第9巡: fresh audit

別の読み取り専用セッションでP40〜P42の解消状況、45 ID、56関係、E件数と
provenanceの終端条件を再確認した。P40とP42、不変条件は解消・一致したが、
最終バッチのマージ後検査に1 findingがあった。同時に実行手順を手作業で追跡し、
バッチ別コマンド選択と基点refに2 findingsを確認した。

| ID | finding | 対応 |
|---|---|---|
| P43 | 到達可能性検査が次バッチ開始時だけで、次バッチのないバッチ5を検査できなかった | 各バッチ共通の§7.6を追加し、バッチ5ではその成功をE1作業の最終完了条件にした。PR本文の固定マーカーとも機械照合し、自動発見0件・複数件・ID不一致の回帰テストを追加した |
| P44 | §7.2・§7.3のコードブロックが5バッチ分を逐次実行し、未作成テストや未修正ch12 mypyで当該バッチ外でも停止した | バッチ番号から対象pytestとmypyを1コマンドずつ選ぶ `run_e1_batch_gates.py` を計画し、直接実行とfinalizerで共用する。対応表、未知値、非0伝播を単体テストで固定した |
| P45 | 差分基点がローカル `main` であり、fetch後も古いrefを使う可能性があった | `git fetch origin main` 後の `origin/main` とのmerge-baseへ統一した |

3 findingsを反映した。次巡では、共通バッチランナー、各PR直後の到達可能性・PR本文照合、
`origin/main` 基点を別のfreshセッションで再監査する。

### 第10巡: fresh audit

別の読み取り専用セッションでP43〜P45、45 ID、56定義、教育的コメント同期、
バッチ別ゲート、各PRのマージ後状態を再確認した。45 ID、目標4/37/4、最終件数、
関係の2集計、P44・P45は一致したが、停止条件とマージ後・コメント監査に
4 findingsがあった。

| ID | finding | 対応 |
|---|---|---|
| P46 | 停止条件が全対象を `required_scripts` と仮定し、基準から `required_tests` のテスト例4件をバッチ2で必ず拒否した | fixtureへ基準placementを固定し、41件の `required_scripts` と4件の `required_tests` から変化した場合だけ停止する条件へ訂正 |
| P47 | 教育的コメント同期の状態・根拠・位置を記録するスキーマと非0ゲートがなかった | 45 IDの `comment_sync` に4状態、理由、意味分類、本文・実体位置、証拠ハッシュを追加し、バッチ別確定集合と最終45件をfixture・独立監査へ接続 |
| P48 | マージ後はコミット到達可能性だけを検査し、`origin/main` の実内容と当該バッチ期待値を検査できなかった | `origin/main` の一時worktreeで独立監査、E件数、関係、コメント同期、goldset、snapshotを検査する `check_e1_merged_state.py` と回帰テストを追加 |
| P49 | 引数なしの `gh pr view` が現在のブランチへ依存し、当該artifactのPRとmerge commitを固定できなかった | PR作成時の番号を `E1_PR_NUMBER` で明示的に引き継ぎ、PR JSONの番号、OPEN/MERGED状態、head、merge commit、本文マーカーをartifact・`origin/main` と機械照合 |

4 findingsを反映した。次巡では、基準placement、45件のコメント監査、
一時worktreeのマージ後内容監査、明示PR番号とhead・merge commitの結合を
別のfreshセッションで再監査する。

### 第11巡: fresh audit

別の読み取り専用セッションでP46〜P49、45件のコメント実測、placement、
一時worktree監査、PR provenanceのデータ流を再確認した。P48、45 ID、56定義、
目標件数、全体939 passed・11 skippedは一致したが、事前分類、PR更新順、
placementゲートに3 findingsがあった。

| ID | finding | 対応 |
|---|---|---|
| P50 | 既出11件以外を `body_only` / `not_applicable` に限定し、実体で充足済みの `B-10-031`、`B-13-004`、`B-17-039` などを誤分類した | 実装前に45 IDすべてを4状態へ列挙し、4/25/6/10件として固定した。本文・実体の行範囲と正規化後SHA-256の計算法も明記し、期待変更時は計画改定へ戻す |
| P51 | 現在ブランチから推測したPR番号で本文を更新し、head不一致を更新後にしか検出できなかった | `create_e1_pr.py` が `gh pr create` のURLから番号を固定し、明示番号のOPEN・head一致を読み取り確認した後だけマーカーを設定する。head不一致時の本文不変テストを追加 |
| P52 | 41+4のplacementをfixtureへ置くだけで、独立監査・finalizer・マージ後検査の非0ゲートへ明示接続していなかった | 45 IDのplacement完全一致を3ゲートへ接続し、総数を保った相互入替でも失敗する回帰テストを追加 |

3 findingsを反映した。次巡では、45 IDの固定コメント状態とハッシュ正規化、
PR作成URLから本文更新前検査までの順序、placementの3段階ゲートを
別のfreshセッションで再監査する。

### 第12巡: fresh audit

別の読み取り専用セッションでP50〜P52、45件のコメント実測、証拠scope、
中間バッチ表現、PR更新順、placementゲートを再確認した。P51、P52、45 ID、
56定義、件数、各PRの終端条件は一致したが、コメント同期に2 findingsがあった。

| ID | finding | 対応 |
|---|---|---|
| P53 | 45 IDすべてに終端状態を要求しながら、バッチ1〜4では未着手IDの最終位置・ハッシュを記録できず、中間成果物の表現が自己矛盾した | 中間専用 `pending` を追加し、バッチ1〜5の終端/`pending` 数を4/41、18/27、32/13、41/4、45/0と固定した。`pending` では位置・ハッシュを禁止し、最終意味アンカーと各完了時の実測証拠を分離した |
| P54 | `B-01-003` は既存DRYコメントで充足済みなのに `added` とし、モジュールdocstring・定義直前コメントをentity証拠として解決できなかった | `B-01-003` を `satisfied_existing` へ移し、実測再分類を3/28/1/13件へ更新した。証拠scopeに `entity` / `file` を設け、ファイルscopeの範囲・禁止条件を定義した |

2 findingsを反映した。次巡では、中間 `pending` の厳密な遷移と最終0件、
3/28/1/13件の意味分類、entity/file証拠scopeを別のfreshセッションで再監査する。

### 第13巡: fresh audit

別の読み取り専用セッションでP53〜P54、45件のコメント実測、バッチ0〜5の
中間表現、PR作成経路を再確認した。45 ID、placement 41/4、3/28/1/13件、
現行46関係と最終56関係、最終E件数は一致したが、3 findingsがあった。

| ID | finding | 対応 |
|---|---|---|
| P55 | `pending` が持つフィールドとバッチ0の45 ID表現が未定義だった | `pending` を `block_id`、固定status、予定バッチ、期待終端状態の4フィールドへ固定し、バッチ0〜5の終端/`pending` 数を0/45、4/41、18/27、32/13、41/4、45/0と明記した |
| P56 | docstringをsourceコメント証拠へ含めるかが未定義で、意味アンカーを独立再現できなかった | source候補を行コメントへ限定し、本文説明は `body_only` だけ、docstringとパス表示コメントは対象外と定義した。45 IDの状態、証拠種別、意味分類、source/target、scope/entity、予定バッチを規範表へ固定し、バッチ2〜5でfixtureの変更を禁止した |
| P57 | PR作成前のpushとremote head OID検査がなく、誤ったremote headでPRを作る余地があった | PR helperで非main・非detachedを検査し、push、remote OID一致、明示headでのPR作成を順に行う。push失敗・OID不一致時にPR作成を呼ばない回帰テストも追加した |

3 findingsを反映した。次巡では、バッチ0を含む `pending` の厳密なスキーマ、
45行の意味アンカー、pushからPR作成・本文更新までの副作用順序を
別のfreshセッションで再監査する。

### 第14巡: fresh audit

別の読み取り専用セッションでP55〜P57、45行のsource・target証拠、
バッチ0〜5の保存則、PR helperの失敗経路を再確認した。45 ID、placement 41/4、
56定義、関係46→56、最終E件数は一致したが、3 findingsがあった。

| ID | finding | 対応 |
|---|---|---|
| P58 | `pending` の4フィールドは定義されたが、スキーマ3からのバッチ0初期化と既完了レコードの単調遷移を監査できなかった | 基準refのスキーマ3からバッチ0遷移状態を決定的に生成し、予定IDだけの遷移と既完了レコードのdeep equalityをfinalizer前後・マージ後に検査する。早期・遅延・逆戻り・証拠書換えなどの回帰テストを追加した |
| P59 | `B-08-019` の証拠種別、`B-09-024` の既存充足、`B-10-028` の意味分類が実測と不一致だった | `B-08-019` を `line_comment/body_only`、`B-09-024` をNaN説明追加の `added`、`B-10-028` を `implementation_decision` へ修正し、最終状態内訳を4/27/1/13件へ更新した |
| P60 | PR作成後の読取・JSON・本文更新失敗から再開できず、再実行でPRを重複作成する余地があった | PR作成前の `prepared` 状態と作成番号を状態ファイルへ保存し、明示番号の `resume` モードを追加した。作成・読取・JSON・本文更新の各失敗と、再開時にPR作成を呼ばない回帰テストを追加した |

3 findingsを反映した。次巡では、バッチ0からの単調遷移、4/27/1/13件の
意味アンカー、PR状態ファイルと `resume` の全失敗経路を別のfreshセッションで
再監査する。

### 第15巡: fresh audit

別の読み取り専用セッションでP58〜P60、45行の規範表、バッチ保存則、
PR helperの失敗復旧性を再確認した。45 ID、placement 41/4、56定義、
関係46→56、最終E件数、4/27/1/13件の内訳は一致したが、1 findingがあった。

| ID | finding | 対応 |
|---|---|---|
| P61 | `B-10-028` を既存コメントで充足済みとしている一方、解消マトリクスが存在しない「既定値」仕様の追加を指示していた | 教育・同期方針を既存の `from exc` コメントで充足済みとして重複追加しない内容へ修正し、必須検証を正常変換、`BiofilterError`、`__cause__` の `ValueError` に限定した |

1 findingを反映した。次巡では、P61の規範表との整合、バッチ保存則、
PR helperの失敗復旧性を別のfreshセッションで再監査する。

### 第16巡（最終巡）: fresh audit

別の読み取り専用セッションでP61、45行の規範表、バッチ0〜5の件数・単調遷移、
教育的コメントの同期方針、PR helperの失敗復旧性を再確認した。

- 状態: 新規finding 0件
- 45 IDは基準対応表のE1集合と一致し、重複0件
- コメント終端状態は4/27/1/13件、placementは41/4件で一致
- 終端/`pending` は0/45→4/41→18/27→32/13→41/4→45/0で一致
- `B-10-028` は本文・実体の `from exc` コメントと15件の既存テストに整合
- PR helperは `prepared`、完全一致検索、PR番号保存、`resume`、再作成禁止の
  失敗復旧経路と回帰テスト計画が一貫している

以上により、P1〜P61を反映したE1整理計画のレビューを完了する。
