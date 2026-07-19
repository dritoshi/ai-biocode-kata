# 章別 指摘一覧 — 2026年7月19日レビュー

[統合レビュー報告](./2026-07-19_update_review.md) の詳細版。統合報告は重要度順に再構成し要約しているため、**個別指摘の一部が省かれている**。本ファイルは章別に全指摘を記録する。修正作業時はこちらを参照すること。

- **確信度**: CONFIRMED（一次情報・実行で裏取り済み）／ LIKELY（強い根拠あり）／ UNCERTAIN（要確認）
- 検証環境: Python 3.14.6 / numpy 2.4.6 / pandas 3.0.3 / polars 1.41.0 / matplotlib 3.10.9 / seaborn 0.13.2 / biopython 1.87 / scipy 1.17.1 / click 8.4.1 / rich 15.0.0 / pytest 9.0.3 / ruff 0.15.14
- **本書のファイルは一切変更していない。**

---

## §0 `00_ai_agent.md`（23件）

### 引用の誤り

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 725-727 | 引用[17] arXiv:2604.03515 は "Inside the Scaffold: A Source-Code Taxonomy of Coding Agent Architectures"（Rombaut）で**13スキャフォールドの分類学的調査**。「42%→78%」「6モデルで1.3ポイント差」は論文に存在せず、要約は "This paper presents a source-code-level architectural taxonomy…" とのみ述べる。**差し替え候補: Terminal-Bench 2.1 公式板（同じ Fable 5 で Claude Code 83.8% vs Terminus 2 80.4%）** |
| CONFIRMED | 988 | [16] Terminal-Bench の著者が「Wijk, Phan, Berglund」→ 正しくは **Merrill, M. A., Shaw, A. G., Carlini, N., et al.**（計85名）。arXiv に "ICLR 2026" の会議情報なし、投稿は2026-01-17 |
| CONFIRMED | 996 | [24] 第一著者「Huang, Y.」→ **Xi, Y.**（Yunjia Xi, Jianghao Lin, Yongzhao Xiao, …） |
| CONFIRMED | 997 | [25] 第一著者「Xu, R.」→ **Zhang, W.**（Wenlin Zhang, Xiaopeng Li, …） |
| CONFIRMED | `ch00.bib:30` | SWE-agent の URL が arXiv:2401.05566（= Hubinger "Sleeper Agents"）→ 正しくは **arXiv:2405.15793**。本文リスト976行は正しく、bib だけ誤り |
| CONFIRMED | 976 | 参考文献[4]（SWE-agent）が**本文から一度も引用されていない**（完全な欠番。本文は 1,2,3,5〜32 を使用） |
| CONFIRMED | 991 | [19] BioCoder の書誌が「*Bioinformatics*, 40(4), 2024」→ 正しくは **40(Supplement_1), i266–i276**（ISMB 2024 特集号）。40(4) は存在しない号 |
| LIKELY | 721 | BioCoder で「GPT-4でも約60%」→ 論文抄録は "50% versus up to 25%" で**約50%**。60%を残すなら条件（Pass@1/Pass@5）を明記 |
| CONFIRMED | 736 | Ouyang et al. の 75.76% は **CodeContests のみ**の値。原典は "75.76%, 51.00%, and 47.56% for CodeContests, APPS, and HumanEval"。「5回実行」も原典で確認できず。**修正案: 「データセットにより47.6%〜75.8%」と範囲で記述** |
| LIKELY | 317 | Gemini Deep Research の「多段検索を**RLで訓練**した」が引用元[23]に記載なし。「最大60分」は正しい |
| LIKELY | 715 | 「**Anthropic の内部評価では**…13%向上」→ [30] では「13% lift」は**パートナー企業の証言**。Anthropic の一次記述は「複雑なマルチステップ workflow で **+14%**」。CursorBench 58%→70% は正しいが **Cursor 社のベンチマーク** |

### 技術的な事実誤り

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 522, 526 | Codex CLI の hooks を「2026年3月時点で `under development`」と記述 → **正式機能化済み**。`features.hooks` が boolean で文書化されている。§8-3 に波及 |
| LIKELY | 663 | Codex の推論強度に **"None" は存在しない**。許容値は `minimal`/`low`/`medium`/`high`/`xhigh`。UI 表記は Low/Medium/High/Extra High/**Max/Ultra**（上位2段が欠落） |
| LIKELY | 675 | 「Haiku 4.5, effort = low」→ **Haiku 4.5 は effort 非対応**。本書自身が658行で「Adaptive に未対応」と書いており実質的に矛盾 |
| LIKELY | 664 | effort の変更が「`/model` で」→ 専用コマンド **`/effort`** が存在。`Alt+T`/`Option+T` は「拡張思考のオン/オフ」で effort とは別軸。同じ行に並べると混同を招く |
| UNCERTAIN | 69, 73 | `--full-auto` を「`-a on-request --sandbox workspace-write` の別名」と説明。現行ドキュメントに `--full-auto` の記載自体がなく裏付け不能（旧版は `on-failure` だった可能性）。**なお別調査で `--full-auto` は公式に非推奨化と判明** |
| UNCERTAIN | 231, 523 | Codex のスキル呼び出し `$skill-name` / `$create-plan` の実在を確認できず（skills ページが404）。**別調査で配置は `.agents/skills/<name>/SKILL.md` と判明** |

### 陳腐化

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 643-648, 673-687 | モデルラインナップが2世代古い。**Opus 4.7 / Sonnet 4.6 は公式に "Legacy models" へ移動**、GPT-5.5 も "previous-generation" 表記 |
| CONFIRMED | 1001 | [29] の URL が **Opus 4.8 のページを返す**。本文7箇所（600, 658, 668, 694, 736, 742, 808）がこれに依拠しており読者が検証できない |
| CONFIRMED | 55, 973-979, 1004 | 主要な公式 URL がすべて 301/308 リダイレクト（`docs.anthropic.com` → `code.claude.com` / `platform.claude.com`、`developers.openai.com/codex/models` → `learn.chatgpt.com/docs/models`） |
| LIKELY | 523 | Claude Code のカスタムコマンドは **skills に統合済み**。`.claude/commands/*.md` は後方互換で動作するが現行推奨は `.claude/skills/<name>/SKILL.md` |
| LIKELY | 532 | TogoMCP「20以上のDB」→ 公式は **"over 30"**。TogoID の 65+ と DBCLS 開発・SPARQL は正しい |

### 内部矛盾・コード

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 940-942 | 演習0-4 が「§0-4 で**学んだ** Writer/Reviewer パターン」と書くが、§0-4（536-579）に該当語が**一度も出てこない**。同節は「実装後のセルフレビュー」「別人格レビュー」「テスト生成」の3構成 |
| CONFIRMED | 173-186 | Viterbi 抜粋で `seq = sequence.upper()` が落ちており `NameError`（引数は `sequence`、本体は `seq` 参照）。実体 `scripts/ch00/hmm_gene_predict.py:72` には存在 |
| UNCERTAIN | 709-713, 717 | SWE-bench 表の出典未記載。「LiveCodeBench で Gemini 3 Pro が 91.7%」は**引用番号が付いていない**（前後の[31]は OpenAI 発表で出典として不適切）。**別調査で Artificial Analysis の自社測定と判明** |

### 検証の結果「正しい」と確認できたもの（修正不要）

ORF 279個 / HMM後 19個の出力例（付属スクリプト実行で完全一致、先頭候補 start=336/end=2799/frame=+1、タンパク質配列は *thrA* と一致）、遷移確率 0.997/0.003/0.98/0.02、thrL=66bp、*E. coli* 約4.6Mbp・約4,300遺伝子、Anthropic マルチエージェント研究の 90.2%、effort 5段階と Opus 4.7 の公式推奨、Opus 4.7 の API 制約（`budget_tokens`/`temperature` が400、トークナイザ最大1.35倍）、`Ctrl+G` での計画編集、`Esc Esc`/`/rewind`/`/plan`/`/compact`/`/resume`/`/model`/`/init`/`/permissions`/`Shift+Tab`、インストールコマンド4種、Terminal-Bench 2.0 = 89問、SWE-bench Verified = 500問、Gemini DR 最大60分、MIT Missing Semester 2026年版の "Agentic Coding" 講義（第7回・2026-01-21）。

---

## §1 `01_design.md`（4件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 284 | スプリントを「1〜2週間の固定期間」と定義 → 引用元 Scrum Guide（2020年11月版）は "fixed length events of **one month or less**"。1〜2週間は実務慣行であり定義ではない |
| CONFIRMED | 154 | 引用[6]が Wikipedia にリンクしているが、文献リストの[6]は Martin *Clean Code*（URLなし）。番号とリンク先が別物。また SRP の一次文献は *Agile Software Development, Principles, Patterns, and Practices*(2003) で *Clean Code*(2008) は解説書 |
| LIKELY | 60 | DRY の要約から **"authoritative"（正典となる）** が脱落。原文は "single, unambiguous, authoritative representation"。DRY を「重複排除だけの原則」と誤読させる |
| LIKELY | 190 | 引用番号が初出順でない（[2]→[3]→[4]→[5]→[6]→[1]→[7]…。[1] McIlroy は190行が初出） |

**健全な点**: [1]-[12] すべて本文で使用され、欠番・重複・未使用なし。

---

## §2 `02_terminal.md`（9件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 458-463, 499 | **GFF3 と GTF の取り違え**。`gene_id "ENSG00000012048"` は GTF（GFF2系）の記法。GFF3 の第9列は `tag=value` 形式で、仕様書は「属性値は引用符で囲む必要はなく、囲むべきでもない」と明記。**修正案: 見出し・コメント・L499 の指示例を「GTF」に。正規表現 `r'gene_id "([^"]+)"'` は GTF に対して正しいのでそのまま使える** |
| CONFIRMED | 493, 428-440 | 「grep/sed のパターンをそのまま Python に持ち込める」は誤り。実測: BRE では `+` `?` が**リテラル**（`grep 'AT+G'` は `ATG` にマッチしない）、`\d` は **BSD sed で機能しない**（`[0-9]+` なら可）。メタ文字表は PCRE/Python 方言 |
| CONFIRMED | 821-835, 805-806 | 参考文献[1]〜[8]が**本文で一度も引用されていない**（本文の引用は[9] L521 と[10] L531 のみ）。さらに **L805-806 が「本章の参考文献[1]/[2]で引用」と書いており事実に反する**。[8] seqtk は章内に語自体が出てこない |
| CONFIRMED | 839, `ch02.bib:75` | fd の作者「Peterka, D.」→ **Peter, David**（GitHub `sharkdp` の本名） |
| CONFIRMED | 521 | ripgrep が「再帰検索が **10〜50倍** 高速」→ 引用元のベンチマークは単一ファイルで約**1.9倍**、再帰検索は git grep とほぼ同等（rg 0.334秒 vs git grep 0.345秒）。実運用の差は主に `.gitignore` による探索対象の絞り込み（本書もL521後半で正しく指摘） |
| CONFIRMED | 503 | 指示例の正規表現 `r"(?<=\\t)([^\\t]+)(?=\\t)"` が **`\\t`（バックスラッシュ+t の2文字）でタブにマッチしない**。実測で無変換。`\t` なら `'a\tb_modified\tc'` と正しく置換 |
| LIKELY | 438, 440 | Python の `\d` `\w` は既定で **Unicode 対応**。`re.match(r'\d', '５')`（全角5）は**マッチする**。`re.ASCII` を付けて初めて `None`。「`[0-9]`と同等」は不正確 |
| LIKELY | 837 | [9] の URL が 302 で `https://burntsushi.net/ripgrep/` へ転送。`ch02.bib:69` も同様 |
| UNCERTAIN | 521, 531 | 「Codex CLI も ripgrep に依存（未インストールだと起動時エラー）」「fd は Claude Code でも推奨」が裏取りできず |

**正しいと確認できたもの**: L169 の `zcat` の GNU/BSD 差異（実測で `can't stat: g.txt.gz (g.txt.gz.Z)` と失敗を再現）、L159 `gzip -k`、L413 の `extract_column(column=1)` = `cut -f2` の対応、L454/461/484/490 の正規表現の出力。

---

## §3 `03_cs_basics.md`（10件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 389 | 「NaN はあらゆる比較演算が `False`」→ **`!=` は `True`**。しかも**4行上の L385 で本書自身が `print(nan != nan)  # → True` と正しく示しており章内で直接矛盾**。読者が `if x != x:` によるNaN検出（有効なイディオム）を誤りと判断してしまう |
| CONFIRMED | 742 | まとめ表「sum()で0.1を10回足すと1.0にならない」が本文 L299-300 と矛盾。実測（3.14.6）: 逐次加算 → `0.9999999999999999`、`sum([0.1]*10)` → **`1.0`**、`math.fsum` → `1.0`。**修正案: 「逐次加算で」に変えれば全バージョンで成立** |
| CONFIRMED | 127 | Counter の出力例に **`'CGA': 2` が欠落**し順序も異なる。実際は `Counter({'CGA': 2, 'GAT': 2, 'ATC': 2, 'TCG': 2, 'ATG': 1, 'TGC': 1, 'GCG': 1})`（7種類しかないので全部書ける） |
| CONFIRMED | 718 | `Sequence`/`Iterable`/`Callable` を `typing` から取ると案内 → **PEP 585 により3.9以降非推奨**、`collections.abc` が正しい。L679/L690 で新記法を教えているのにここだけ旧案内で不整合。L730 の「mypy --strict で警告が出ないように」とも噛み合わない |
| CONFIRMED | 415, 834 | Unicode 16.0 を参照 → 最新は **17.0.0（2025年）**。年次リリースのため `https://www.unicode.org/versions/latest/` を使う手もある |
| LIKELY | 26-27, 66 | set/dict の `O(1)` が**平均計算量**である旨の注記がない（最悪は `O(n)`）。L24 の list 末尾追加も償却計算量 |
| LIKELY | 469, 489 | (a)「完全に再現できる」→ `default_rng`(Generator) は NumPy バージョン間のストリーム安定性が保証されない。(b)「`np.random.seed` は**非推奨**」→ 実測で **DeprecationWarning は出ない**（NumPy 2.4.6）。公式表現は "legacy" |
| LIKELY | 260-261 | `a + np.int32(1)` のオーバーフロー例。値は正しいが NumPy 2.4.6 では **`RuntimeWarning: overflow encountered in scalar add` も発生**。「NumPy が警告で教えてくれる」ことは有用な情報 |
| LIKELY | 237 | BAM(.bai)/tabix(.tbi) を「二分探索ベース」→ 実際は **UCSC 由来のビニング方式（階層的binインデックス）＋リニアインデックス**。計算量のオーダー感は誤りではない |
| LIKELY | 666, 122 | mypy --strict を通らない型ヒント。L666 `-> "pd.DataFrame"` は `pandas` 未import（`Name "pd" is not defined`）、L122 `-> Counter` は型引数なしで `disallow_any_generics` に抵触 |
| UNCERTAIN | 813 | Compeau & Pevzner の「3rd ed., 2015」→ 第2版が2015年、第3版が2018年の可能性。公式サイトに版情報なく確定できず |

**正しいと確認できたもの**: L282 の 0.1 の2進表現、L319-330 の CSV 丸め例（出力まで一致）、L369 `math.isclose()` の相対許容誤差 1e-9、L186-196 の bisect 例、L38-50 の計算量の数値（`≈17`、`≈1.7×10⁶`、`10¹⁰`、「約6億倍」）、L404 Q30 = 10⁻³、引用[1]-[18] の全数対応。

---

## §4 `04_data_formats.md`（12件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 346-347, 357 | **全角文字に関する Python の挙動が3箇所とも逆**。実測: 引数なし `split()` は U+3000 で**分割する**（`"a　b".split()` → `['a','b']`）、`int("１２３")` → **`123`**、`int("　100")` → **`100`（例外なし）**。**コラムの結論「サイレントに失敗する」は正しいので、根拠を実挙動に合わせると主張は強化される。** `awk` 側の記述は正しい（U+3000 で分割されないことを実測） |
| CONFIRMED | 224-227 | `[project.dependencies]` テーブル形式は **PEP 621 違反**（`uvx validate-pyproject` → `must be array`）。Poetry の書き方。**§6:159-169 の同じ例は正しい配列形式**で、しかも §6:160 が「§4 でも登場」とリンクしており章間矛盾 |
| CONFIRMED | 11 | Forbes 調査の「60%」を**回答者の割合と誤読**。実際は「**作業時間に占める割合**」（"Data scientists spend 60% of their time on cleaning"）。80% は 60%＋19%（データ収集）の合計。57% は正しい |
| CONFIRMED | 259 | RIKEN クローンID の指数が誤り。`2310009E13` = $2310009 \times 10^{13}$ = **$2.31 \times 10^{19}$**（実測 `float('2310009E13')` → `2.310009e+19`）。表示例 `2.31E+13` は論文の粗い表記の踏襲だが、本書が独自に付けた数式解釈が算術的に誤り |
| CONFIRMED | 82 | OpenStreetMap を CC-BY-SA の例に → **2012年9月に ODbL へ移行済み**。CC-BY-SA なのは OSM の Wiki のみ。ODbL はデータベース向けコピーレフトとして紹介価値あり |
| CONFIRMED | 700 | 「ヒトの遺伝子の約95%が選択的スプライシング」→ 出典（Pan et al. 2008）は "approximately 95% of **multiexon** genes"。**「多エクソン遺伝子の」が脱落**。加えて本文に引用が付いていない |
| CONFIRMED | 891, 893 | 参考文献[13] SAM/BAM 仕様・[14] Kent et al. が**本文から一度も引用されていない**（本文は 1–12, 15–19 を使用） |
| CONFIRMED | `ch04.bib` | [18] Creative Commons・[19] DOI Handbook の **BibTeX エントリが欠落**（bib は20件だが該当なし） |
| LIKELY | 54 | DOI プレフィクスを「**登録機関**を示す」→ 実際は**登録者（出版社等）**。登録機関(RA)は Crossref/DataCite/JaLC。本文自身が「Nature系列（10.1038）」と例示しており括弧内と矛盾 |
| LIKELY | 211, 724, 728 | GENCODE **v44**（2023年7月）を「典型的な選択肢」→ 現行は **Release 50**（GRCh38.p14）で3世代前 |
| LIKELY | 364, 407 | `grep -P` は GNU 拡張で **macOS 標準 grep では動作しない**（実測 `invalid option -- P`）。読者に macOS 利用者が多い前提では要注記 |
| UNCERTAIN | 56 | 「IDF が **2000年から**運用」→ IDF 設立1998年、本格運用2000年、ISO 26324 標準化2012年の混同の可能性。doi.org に設立年の記載なく確定不能 |
| UNCERTAIN | 121 | RFC 4180 を **TSV の典拠**にしている。RFC 4180 は CSV 専用。TSV には IANA の `text/tab-separated-values` 登録がある |

**★ 正しいと確認できたもの（本書の中核）**: **座標系の記述は全項目が正確** — BED/BAM/Python = 0-based half-open、GFF/VCF/SAM/R = 1-based closed、`chr1 9 10`（BED）＝`chr1 10 10`（GFF）、pysam の `reference_start + 1` 変換、pyranges / pybedtools / Biopython SeqFeature の座標系。`scripts/ch04/coordinate_convert.py` の実装も本文と整合。ほか TSV→CSV 変換、float 丸め例、NFD/NFC、NFKC、`melt`/`pivot_table`、`messy_to_tidy`（assert 通過）、gzip/bgzf/zstd の特性、`.fai`/`.bai`/`.tbi`、30x WGS FASTQ 非圧縮100GB超、Ziemann 2016 の「約20%」、HGNC の MARCH1→MARCHF1 等。

---

## §5 `05_software_components.md`（8件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 560 | Claude Code の MCP スコープが「`project`/`user`/`global`」→ 現行は **`local`（既定）/`project`/`user`**。公式は「`user`: Older versions called this scope `global`」と明記。**既定の `local` が抜けており `-s` 省略時の挙動が伝わらない** |
| CONFIRMED | 566, 569 | `@modelcontextprotocol/server-github` は **npm で deprecated**（"Package no longer supported."、最終版2025.4.8）。公式は `github/github-mcp-server` へ移管、リモートHTTP（`https://api.githubcopilot.com/mcp/`）推奨。L548 の PostgreSQL MCP も同様 |
| CONFIRMED | 317, 369 | **`conda info <パッケージ名>` は存在しないコマンド**（位置引数を取らない）。正しくは `conda search --info <pkg>` |
| CONFIRMED | 171, 179 | `python -m` の `sys.path[0]` を `''` と記述 → **Python 3.11（bpo-33053）でカレントの絶対パスに変更**。`''` のままなのは対話実行・`python -c`・`python -`。実測で確認 |
| CONFIRMED | 682 | 参考文献[4] Levine *Linkers and Loaders* が**本文未引用**（「さらに学びたい読者へ」に番号なしで登場するのみ） |
| LIKELY | 460 | `PARSERS: dict[str, Callable]` で **`Callable` が未 import** → コピペで `NameError`。`from collections.abc import Callable` の追加が必要 |
| LIKELY | 358-359 | `pip show pandas` の出力例 `Requires: numpy, python-dateutil, pytz, tzdata` → **pandas 3.0 では `pytz` が依存から外れ**、`tzdata` は Windows/emscripten 限定の条件付き依存（実測） |
| UNCERTAIN | 3-4 | 『五輪書』の引用元が「水之巻」→「奥」を論じるのは風之巻の「他流に奥表と云事」。一次資料で裏取りできず |

**正しいと確認できたもの**: Bio.SeqIO の ImportError 実例（Biopython 1.87 で実行しメッセージ一致）、`pipdeptree -p` / `--warn silence` の実在、相対 import の説明（`from ..module_demo import ...`）、`__init__.py` の内容、静的/動的リンクと `.a`/`.so`/`.dylib`、`LD_LIBRARY_PATH`/`DYLD_LIBRARY_PATH`/rpath、SIP の注意、Codex CLI の `codex mcp add/list/remove`（ソース `codex-rs/cli/src/mcp_cmd.rs` で確認）。

---

## §6 `06_dev_environment.md`（7件）

| 確信度 | 行 | 内容 |
|---|---|---|
| **CONFIRMED** | **334, 341-350** | **`-c bioconda -c conda-forge` のチャネル順が逆**（4コマンドすべて）。conda は先に書いたチャネルが高優先度。Bioconda 公式は「bioconda は conda-forge に強く依存するため **conda-forge が最高優先度**」と明記。**本書自身が L316 と L310-311 の `.condarc` 例で conda-forge を先頭に置いており章内矛盾。** L330 の「記述順が優先順位になる」という説明を活かすなら、順序を直したうえで理由も補う |
| CONFIRMED | 177, 312 | `environment.yml` と `~/.condarc` の両例に **`- defaults` が含まれる**。(1) Bioconda は2024年8月に推奨から削除、(2) `defaults` は Anaconda のリポジトリで本書自身が L92/L303 で警告している有償ライセンス対象、(3) 本書推奨の Miniforge3 は既定で conda-forge のみで `defaults` を意図的に含めない設計 |
| CONFIRMED | 43 | pyenv の解決順が「`.python-version` → `PYENV_VERSION` → グローバル」→ **`PYENV_VERSION` が最優先**、次にカレント（および親）の `.python-version`、最後にグローバル。上位2つが逆 |
| CONFIRMED | 328, 413 | 「Bioconda は **8,000以上**のツールを提供する[9]」→ 引用元 Grüning et al. 2018 は **"over 3,000"**。数値自体は現状と一致するので、**出典を Bioconda 公式サイト（参照日付き）に付け替え、[9] は設計思想の根拠として残す** |
| CONFIRMED | 369-380 | PyTorch を「**conda推奨**」→ **公式 Anaconda チャネルへの公開を終了**（2.5系が最後）。現行の公式ガイドは pip のみ。`pytorch-cuda=12.1` も維持されず、pip の `cu121` も現行提供（11.8/12.6/12.8）から外れる。**修正時は L257 の「conda と pip の混在を避ける」原則との関係を1文添えるとよい** |
| LIKELY | 92 | 「Anacondaのライセンス変更（**商用利用の有償化**）」→ 現行は「**従業員・契約者200名以上の組織**は有償 Business ライセンス」で、基準は商用/非商用ではなく**組織規模**。学術・非営利には免除規定があるが、**200名超の大学・研究所の研究者は「非商用」でも対象になりうる** |
| LIKELY | 30-31, 182 | `pyenv install 3.11.9` / `3.12.4`（2024年）、`samtools=1.19`（2023年12月）が古い。「最新を明示する」という本章の主張と齟齬 |

**正しいと確認できたもの**: Mambaforge 非推奨「2024年半ば」（Miniforge README が "deprecated as of July 2024"）、uv 一式（`curl -LsSf https://astral.sh/uv/install.sh | sh`、`uv python install`/`init`/`add`/`run`/`sync`/`lock`、「pip互換で10〜100倍高速」）、conda-lock のコマンド、venv の仕組み（PATH 先頭書き換え → `sys.prefix != sys.base_prefix`）、`scripts/ch06/check_environment.py` との整合。

---

## §7 `07_git.md`（5件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 609, `ch07.bib:150` | Blischak 論文が「*PLOS Comput Biol*, **11(1)**, e1004668, **2015**」→ 正しくは **12(1), 2016**（2016-01-19公開）。年・巻とも誤り。bib のキーも `blischak2016git` へ |
| CONFIRMED | `ch07.bib:118` | Keep a Changelog の著者「**Langlois**, Olivier」→ **Lacan, Olivier**（公式に "created and maintained by Olivier Lacan"） |
| CONFIRMED | 604 | 参考文献[1] Pro Git・[2] Git Documentation が**本文未引用**。しかも **604行が「本章の参考文献[1]で引用」と書いており事実に反する** |
| CONFIRMED | 443, 451 | 引用番号の出現順が逆転（443行で[17]、451行で[16]、453行で[18]、以降[14][15][13]） |
| CONFIRMED | 150-157 | diff のハンク `@@ -12,7 +12,7 @@` と説明「12行目から7行」に対し、表示本体は**5行**（文脈2＋変更1＋文脈2）。同じ変更を git に生成させると `@@ -12,6 +12,6 @@` |
| CONFIRMED | 280, `scripts/ch07/ci_minimal.yml` | `actions/checkout@v4` / `actions/setup-python@v5` → 現行は **checkout@v7 / setup-python@v6**。**本リポジトリ自身は既に `checkout@v6` へ移行済み**で書籍と不整合 |

**正しいと確認できたもの**: GitHub LFS 無償枠（Free/Pro 10 GiB、Team/Enterprise Cloud 250 GiB）、Zenodo の 50GB・100ファイル／申請で 200GB、`git switch`/`restore` の推奨（Git 2.55 の man に EXPERIMENTAL 表記なし）、Pro Git 第10章 "Git Internals"、SemVer の 0.y.z の扱い、CITATION.cff 例の ORCID チェックディジット。

---

## §8 `08_testing.md`（7件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 573-584 | **Claude Code hooks の設定 JSON が構造的に無効**。(1) matcher 直下に `command` は置けず `hooks` 配列 → `{"type":"command","command":...}` のネストが必須、(2) **`$FILEPATH` という環境変数は存在しない**（パスは stdin の JSON `tool_input.file_path` で受け取る）。**修正案: `{"hooks":{"PostToolUse":[{"matcher":"Edit\|Write","hooks":[{"type":"command","command":"ruff check --fix"}]}]}}`。パスが必要なら `jq -r '.tool_input.file_path'`** |
| CONFIRMED | 385-396 | ruff の指摘コード注釈が実出力と不一致。(1) `E501` は発火しない（当該行は20文字）、(2) `+` は算術演算子なので **E225 ではなく E226**、しかも **E226 は preview モード限定**で本書の設定では検出されない、(3) F401 は `os` だけでなく `sys`・`json` にも出る。本書設定での実出力は `D100, I001, F401×3, N802, D103` |
| CONFIRMED | 467-481 | pre-commit の rev が古く（ruff `v0.8.6` → 現行 **0.15.x**、mypy `v1.14.1`）、**`ruff` フックIDは現在 legacy alias** で正式IDは **`ruff-check`** |
| CONFIRMED | 634, 637, 681, 683, 798 | GitHub Actions が `checkout@v4` / `setup-python@v5`（演習8-4のヒントも同様）→ 現行 v7/v6 |
| CONFIRMED | 6 | 「Python公式チュートリアル §4.7 関数定義」→ 現行は **§4.8**（4.5 に「ループの `else` 節」が独立して繰り下がり）。4.7 は「`match` 文」。URL アンカー `#defining-functions` は正しい |
| CONFIRMED | 660 | 「Actions画面の**「Run tests」**ステップで確認できる」→ 直前620-657のワークフローに該当ステップは無い。正しくは **`pytest によるテスト`** |
| LIKELY | 192-198 | `filter_sequences_by_gc` は `scripts/ch01/` にしかなく `scripts/ch08/` に無い。import も示されずコピーで動かない。142-152 の AAA 例も `import pytest` と `gc_content` の import が欠落 |
| LIKELY | 238-242 | 「N は GC にも AT にもカウントしない想定」→ 実体 `scripts/ch08/seq_stats.py` は**分母に N を含む**（2/5 = 0.4）。`tests/ch08` 側は正しく書いており本文だけ食い違う |
| CONFIRMED | 688 | CI マトリクスが Python 3.10/3.11/3.12。本リポジトリの venv は **3.14.6** |

---

## §9 `09_debug.md`（6件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 274, 661-673, 695 | **pandas の `SettingWithCopyWarning` は pandas 3.0 で廃止**。本リポジトリの lock 版 3.0.3 で `pd.errors.SettingWithCopyWarning` が**存在しない**（実測）。現行は `ChainedAssignmentError` で、挙動も「曖昧」ではなく**確定的に何も起きない**（元 DataFrame 不変）。`.loc[]` を使う結論は据え置きでよい。§9-2 の warnings 表も要差し替え |
| CONFIRMED | 643-645 | `a = 257; b = 257; a is b  # False` → **.py ファイルでは `True`**（CPython は同一コードオブジェクト内の定数を共有）。`False` になるのは対話 REPL 等で文が別々にコンパイルされる場合のみ。実測: スクリプト `True` / REPL `False`。「小さい整数はキャッシュされる」の説明自体は正しい |
| CONFIRMED | 49, 239 | `scripts/ch09` の行番号が不一致。`text = path.read_text()` は traceback_demo.py の **26行目**（本文30）、`gc_ratios.append(gc_ratio)` は pdb_demo.py の **28行目**（本文13）。さらに **pdb_demo.py に `breakpoint()` が1つも無く**、本文209-219 のコードが実体に存在しない |
| CONFIRMED | 231 | pdb コマンド表の `print(expr)` / `p expr` の対応が誤り。**pdb に `print` コマンドは存在せず**（`do_print` 無し、実測）、`p` は略形ではなくコマンドそのもの。**修正案: `p expr` / `pp expr`（pp は整形表示）** |
| CONFIRMED | 421, 806, `ch09.bib:53` | [8] UCSC の**タイトルが誤り**。「FAQ: Coordinate Transforms」→ FAQformat.html の実タイトルは **"Frequently Asked Questions: Data File Formats"**。さらに本文の「座標系の混乱は最大のバグ源」という主張を**このページは述べていない**（BED/GFF の座標定義を各々記載するのみ） |
| CONFIRMED | — | 参考文献[2] traceback・[6] Agans・[7] Zeller が**本文未引用**（[6][7] は「さらに学びたい読者へ」に番号なしで登場） |
| UNCERTAIN | 473 | `UnicodeDecodeError` のメッセージが途中で切れている。実際は末尾に理由（`: invalid continuation byte`）が必ず付く |

---

## §10 `10_deliverables.md`（7件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 77-90, 1011-1023 | pyproject.toml 例に **`[build-system]` がない**。引用元 PyPA ガイドは "The `[build-system]` table **should always be present**" と明記。さらに**演習10-4 が `[build-system] requires = ["hatchling"]` の意味を問うのに、その説明が全19章のどこにも存在しない**。実害は限定的（pip の PEP 517 レガシーフォールバックで `pip install .` は成功する）が、バックエンドが暗黙になり移植性・再現性が落ちる |
| CONFIRMED | 604 | 「パラメータは設定ファイル（YAML/TOML）で外部化する[6](12factor.net)」→ 12factor の Config は**環境変数**を推奨し、設定ファイル方式は "it's easy to mistakenly check in a config file to the repo" と**弱点として明示**。669行（秘密情報を環境変数で管理）での[6]引用は正しい |
| CONFIRMED | 353-355, 1071-1075 | 引用[8] GitHub Pages・[9] Streamlit Community Cloud・[10] Hugging Face Spaces が **`references/ch10.bib` に存在しない**（bib は8エントリのみ）。PDF/EPUB ビルド時に文献が欠落 |
| LIKELY | 152 | 「Bioconda に**1万以上**のパッケージ[2]」→ 公式は "over **8000**"。かつ[2]は2018年論文で「1万以上」の出典にならない |
| LIKELY | 108 | wheel を「**コンパイル済み**配布物」→ 正式には "Built Distribution"（**ビルド済み**）。pure Python の wheel はコンパイルを含まず、本章の例（my-tool）もまさに pure Python |
| LIKELY | 763-810 | 本文の `validate_fasta` と実体 `scripts/ch10/error_handling.py` が乖離。実体は `_load_effective_fasta_text()` で先頭行が `>` かを先に検査し `StringIO` 経由でパースする（コメントに「Biopython の deprecated なコメント解釈に依存しないよう」と明記）。本文版は同じ検証強度を持たない |
| LIKELY | 1059, 353 | [2] Bioconda が *Nature Methods* **15(7)**, 475–476 だが**号 `(7)` が欠落**（本文リスト・ch10.bib とも）。353行の GitHub Pages「無料」は**パブリックリポジトリの場合**で、プライベートからの公開は Pro/Team/Enterprise が必要（UNCERTAIN） |

**記載漏れ（誤りではない）**: 終了コード（`sys.exit`、0/1/2 の慣習、click が usage error に 2 を返す点）、`raise from` / `finally` / コンテキストマネージャ、POSIX/GNU のオプション慣習（`--` によるオプション終端）。

---

## §11 `11_cli.md`（12件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 709-717 | **`RichHandler` が stdout に出力**（`console` 未指定でグローバル Console = stdout を使う。実測で `handler.console.file is sys.stdout` → `True`）。本章が繰り返す「結果はstdout、それ以外はstderr」（L779）に真っ向から反する。**実体 `scripts/ch11/logging_setup.py:47-53` は `console=Console(stderr=True)` を正しく渡しており、本文への縮約時に決定的な引数だけ落ちている** |
| CONFIRMED | 323-327 | `samtools view -b input.sam \| samtools sort \| samtools index -` が**成果物ゼロ**。実測（samtools 1.23.1）で生成されるのは **`-.bai` という名前のファイル1つだけで BAM 本体は保存されない**。「優れた設計の実例」として提示されているため誤解が大きい。**修正案: `samtools view -b input.sam \| samtools sort -o sorted.bam && samtools index sorted.bam`** |
| CONFIRMED | 538-555 | スニペットが `sys` / `min_gc` / `gc_content` の3つ未定義で `NameError`。さらに `@cli.command()` + `def filter_sequences` から click 8.x が生成するサブコマンド名は **`filter-sequences`**（`filter` は `No such command`）。実体は `@cli.command(name="filter")` + `def filter_cmd` で正しく回避 |
| CONFIRMED | 55-63 | `argparse.FileType` は **Python 3.14 で非推奨**（公式に "Deprecated since version 3.14"、docstring も `Deprecated factory`）。**本リポジトリは 3.14.6 で動作し、`scripts/ch11/cli_argparse.py` は既に `type=Path` へ移行済みで本文だけが取り残されている** |
| CONFIRMED | 377-382 | Codex のスキル保存場所が「プロジェクトルートに `SKILL.md`」→ 正しくは **`$REPO_ROOT/.agents/skills/<name>/SKILL.md`**（ほか `$CWD/.agents/skills`、`$HOME/.agents/skills`、`/etc/codex/skills`）。呼び出し記法 `$skill-name` は正しい。Claude Code 側も現行は skills 統合済み |
| CONFIRMED | 469 | コメント「**wc コマンド**で `>` の行数を数えて**推定**」に対しコードは `grep -c "^>"`。ツール名不一致、かつ `grep -c` は正確に数えるので「推定」も不正確 |
| CONFIRMED | 622-635 | `logging.getLogger()` に addHandler するだけで **`setLevel()` がなく、ルート既定の WARNING により INFO/DEBUG が出ない**（実測）。直前598-608で「INFO=処理の進行状況」と教えた直後 |
| CONFIRMED | 884 | 参考文献[10] Raymond *The Art of UNIX Programming* が**本文未引用**（本文は[1]-[9]と[11]）。851行の「さらに学びたい読者へ」に番号なしで登場 |
| LIKELY | 508-516 | rich.Progress スニペットで **`Console` が未 import** → 単体実行で `NameError`（実測） |
| LIKELY | 659, 672 | 「[§10-4]の**3層構造**でログレベルを制御」→ §10-4（`10_deliverables.md:662`）と §11-1（256行）の3層は「CLI引数 > **設定ファイル** > デフォルト値」。ここで示す実装に設定ファイル層はなく、`--log-level` と `--verbose` はどちらもCLI引数。683行の「3層構造の原則に従っている」も成立しない |
| LIKELY | `scripts/ch11/cli_click.py:45-46`, `seqtool.py:69,146-147,198-199` | `click.utils.LazyFile` 型ヒントが誤り。`click.File` は `-`（本書の既定値）で実ストリームを返す（実測 `_io.TextIOWrapper`、`isinstance(..., LazyFile)` → `False`）。`LazyFile` になるのは書き込みモードで実ファイル名指定時のみ。**修正案: `typing.TextIO` または `IO[str]`** |
| LIKELY | 331, 880-882 | seqkit に引用がない（Shen et al., *PLoS ONE* 2016 が存在）。[8][9] の文献リストが DOI でなく PubMed URL（`references/ch11.bib` には正しい DOI `10.1093/bioinformatics/btp352` / `btq033` が入っており、リストだけ不整合） |

**正しいと確認できたもの**: click の `FloatRange` エラーメッセージ（click 8.4.1 で文字列完全一致）、tqdm のデフォルト stderr 出力、tqdm のアラビア語由来、ログレベル数値表、`getattr(logging, level.upper())` パターン、Typer 版コード（`Path | None` + `Annotated` も 0.25.1 で動作）、`bwa mem -x ont2d` / `minimap2 -x map-hifi`。

---

## §12 `12_data_processing.md`（5件）

| 確信度 | 行 | 内容 |
|---|---|---|
| **CONFIRMED** | **46-65** | **「高速化」として示すベクトル化版が比較対象より13倍遅い**。実測（50,000配列×150bp）: ループ版 **10.3 ms** / 「ベクトル化」版 **135.3 ms** / 真のベクトル化版 8.3 ms。原因は (a) `str.count()` が既にC実装でPythonループのオーバーヘッドは1配列1回、(b) 150要素の小配列に `.upper()`/`.encode()`/`np.frombuffer`/比較2回/OR/`.sum()` の固定コスト。`scripts/ch12/numpy_vectorize.py:6-31` も同一実装。**修正案: 比較対象を「1塩基ずつのネストループ版」にするか、全配列一括処理（`np.frombuffer("".join(seqs).encode()).reshape(n, L)`）へ。あわせて「文字列組み込みメソッドは既にC実装なのでNumPy化の効果は小さい」という判断基準を本文に加えるとレビュー力に直結する** |
| CONFIRMED | 40 | ベンチマーク図 `figures/ch12_vectorize_bench.png`（"speedup: 72x"）が**本文と別のコードを測定**。`scripts/ch12/plot_vectorize_bench.py:28-41` は「1塩基ずつのネストPythonループ」vs「事前構築済み `(10000,150)` 整数配列への `np.mean((sequences==2)\|(sequences==3), axis=1)`」で、どちらも本文に登場せず文字列→バイト変換のコストも含まない。実測で図の条件は再現（91倍）、本文の2関数は0.08倍 |
| CONFIRMED | 244-259 | Polars の lazy 例が **`ColumnNotFoundError`**。`scan_csv("deg_results.csv")` のカラムは L142-148 で `gene, baseMean, log2FoldChange, pvalue, padj` と定義されており `direction` 列が存在しない。pandas 版（L227-233）は `.assign(direction=...)` で作っているが Polars 版だけ列生成が落ちている。**修正案: `.with_columns(direction=pl.when(pl.col("log2FoldChange") > 0).then(pl.lit("up")).otherwise(pl.lit("down")))` を挿入（L275 の対応表が `with_columns` を「列追加」として挙げているのでその実演にもなる）** |
| CONFIRMED | 3 | エピグラフが Wickham の原文と異なる。原文は **"Like families, tidy datasets are all alike but every messy dataset is messy in its own way."**（*JSS* 59(10), 2014, §2冒頭）。冒頭の "Like families," が脱落し、"alike" の後に原文にないカンマ。引用符付きで出典明示のため逐語引用として扱われる |
| CONFIRMED | 627-645 | 参考文献[1] Harris NumPy論文・[2] NumPy Docs・[3] pandas Docs・[4] McKinney・[7] SciPy Docs が**本文未引用**（本文は[5][6][8][9]のみ）。さらに **L618 が「本章の参考文献[1]で引用」と書いており自己矛盾** |
| LIKELY | `scripts/ch12/numpy_vectorize.py:62` | docstring「**ファンシーインデックス**（ブーリアンマスク）を使い」→ 本文 L105/L114 は両者を明示的に区別している（整数位置配列＝ファンシーインデックス、真偽値配列＝マスク）。**修正案: 「ブーリアンマスクを使い」** |

**正しいと確認できたもの**: メソッドチェーン例、`.query()` の `@変数`+`abs()`、CPMブロードキャスト、`false_discovery_control(method="bh")` と手動BH実装の一致（最大差 2.2e-16）、`pdist(metric="correlation")` = 1−ピアソン相関、`pd.merge` の既定 `how="inner"`、pandas→Polars 対応表。

---

## §13 `13_visualization.md`（12件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 11 | 引用番号とリンク先が**入れ替わっている**（2組）。文献リストは [1]=Matplotlib Docs / [2]=Hunter 2007 / [3]=seaborn Docs / [4]=Waskom 2021 だが、本文は `Matplotlib[1](DOI)[2](matplotlib.org)`、`Seaborn[3](DOI)[4](seaborn.pydata.org)`。**修正案: 本文を `Matplotlib[1](matplotlib.org)[2](DOI)`、`Seaborn[3](seaborn.pydata.org)[4](DOI)` に**。書誌情報自体は Crossref で正確 |
| CONFIRMED | 389 | 「`dpi` はラスタ形式でのみ意味を持ち、**ベクタ形式では無視される**」は誤り。PDF/SVG バックエンドは dpi を**埋め込みラスタ要素の解像度**に使う。実測: `imshow` を含むPDF 55,864B(dpi=50) → 116,022B(dpi=600)、SVG 86,603B → 269,571B、`rasterized=True` の散布図PDF 12,323B → 140,359B（**11倍**）。**ヒートマップや数万点の散布図をPDF入稿する場面はバイオインフォで一般的で、dpi=100 のままだと投稿規定を満たさない** |
| CONFIRMED | 320 | dynamite plot 回避の主張を **Rougier et al. 2014[8] に誤帰属**。同論文の10ルールに棒グラフ・平均値表示の項目はなく、棒グラフへの言及は Rule 7 の軸リスケールのみ。**正しい出典: Weissgerber TL, et al. "Beyond bar and line graphs: time for a new data presentation paradigm". *PLoS Biology*, 13(4), e1002128, 2015. DOI 10.1371/journal.pbio.1002128**（"many different data distributions can lead to the same bar or line graph"）。`ch13.bib` にエントリ追加が必要 |
| CONFIRMED | 80-91 | import ブロックに **`from pathlib import Path` が欠落**しているのに `output_path: Path \| None = None` を使用 → **Python 3.13以前は定義時にアノテーションが評価されるため `NameError` で関数定義自体が失敗**。実測: 3.12 → NameError、3.14 → PEP 649 の遅延評価で偶然通る。実体 `scripts/ch13/bio_plots.py:7` には存在 |
| CONFIRMED | 483, 473 | **`deepTools bamCoverage` というコマンドは存在しない**。deepTools は `bamCoverage`/`plotHeatmap` 等を個別の実行ファイルとしてインストールし、サブコマンド方式のディスパッチャはない（`deeptools` 実行ファイルの中身は `--version` のみのツール一覧表示用）。加えて実行ファイル名は小文字 `deeptools` で `deepTools` は command not found。**修正案: 先頭の `deepTools ` を削除するだけでよい（オプションはすべて正しい）** |
| CONFIRMED | 159-193 | **距離行列を `clustermap()` にそのまま渡すのは誤用**。`clustermap()` は入力を観測値行列として扱い行間のユークリッド距離を計算するため、距離行列を渡すと「距離の距離」でクラスタリングされる。scipy が `ClusterWarning: The symmetric non-negative hollow observation matrix looks suspiciously like an uncondensed distance matrix` を出す（**本リポジトリの pytest 実行時に出ている警告の正体**）。実測で clustermap が使う値（1.3324, 1.3879, …）と本来の相関距離（0.9364, 0.9772, …）が別物であることを確認。`figures/ch13_expression_heatmap.png` も同経路。**修正案: `linkage(squareform(dm, checks=False), method="average")` を計算して `row_linkage`/`col_linkage` に渡すか、発現量行列そのものを `metric="correlation"` で渡す。警告が出る理由を本文で説明すればレビューの良い題材になる** |
| CONFIRMED | `ch13.bib:87,99` | 実在しない著者名。deepTools2 は `Bhatt, Vivek`（→ **Bhardwaj, Vivek**）、`Lucks, Friederike`（→ **Dündar, Friederike**）が誤りで、`Arenber, Konstantin A.` と `Raffan, Frank` は著者ではなく、**Kilpert・Richter・Heyne が欠落**。pyGenomeTracks も `Bhatt, Vivek` が誤りで **Backofen, Rolf** が欠落。巻・号・ページ・年・DOI は正しい（PMID 27079975 / 32745185） |
| CONFIRMED | 593 | [7] Tufte 書籍の URL が 301 で書籍一覧ページへ転送。**修正案: `https://www.edwardtufte.com/book/the-visual-display-of-quantitative-information/`** |
| LIKELY | 324 | 色覚多様性「日本人男性の約5%、**世界的には約8%**」→ Crameri 2020 の該当箇所は "worldwide 0.5% of women and **8% of men**" で **8%は男性の割合**。また同論文に日本の記述はなく「日本人男性の約5%」は[6]で裏付けられない。**修正案: Birch J. "Worldwide prevalence of red-green color deficiency". *J Opt Soc Am A*, 29(3), 313-320, 2012. DOI 10.1364/JOSAA.29.000313 を追加（European Caucasian 男性約8%、中国系・日本系男性4〜6.5%で両方カバー）** |
| LIKELY | 5 | エピグラフが「1983年初版」、参考文献[7]と bib が「2001年第2版」で**章内混在**。ISBN 978-0961392147 は2001年第2版のもの。p.92 の妥当性は両版とも197ページで判別できず UNCERTAIN |
| LIKELY | 402 | 「`Matplotlib.rcParams`」→ モジュール名は小文字 **`matplotlib`**。バッククォート内のコード識別子なのでそのまま書くと `NameError`。直後のコード例は正しく `plt.rcParams` |
| LIKELY | `ch13.bib` | L675 で Robinson et al. "Integrative genomics viewer"(2011) を紹介しているが **BibTeX 未登録**。DOI `10.1038/nbt.1754`、*Nat Biotechnol* 29(1):24-26（著者表記は Thorvaldsdóttir の "ó" に注意） |

**正しいと確認できたもの**: pyGenomeTracks のコマンド・INIキー、UCSC カスタムトラック行、`sns.matrix.ClusterGrid`、`violinplot(hue=..., legend=False)`、`np.select` の文字列choices、TIFF保存。§13 が参照する図はすべて実在。

---

## §14 `14_workflow.md`（9件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 165-183 vs 229 | 本文の `config.yaml` の `params:` は `star` と `featurecounts` のみだが、Snakefile 例が `config["params"]["fastqc"]["threads"]` を参照 → **`KeyError: 'fastqc'`**。実体 `scripts/ch14/config.yaml:16-18` には `fastqc: threads: 4` がある（抜粋漏れ）。`trimmomatic` も欠落だがSnakefile側が省略しているため実害なし |
| CONFIRMED | 392 | `dockerPull: biocontainers/fastp:0.23.4--hadf994f_0` が**レジストリ・タグとも誤り**。`<version>--<buildhash>` 形式は `quay.io/biocontainers` のみの規約で、レジストリ未指定だと Docker Hub の `biocontainers/fastp`（`v0.20.1_cv1` と `v0.19.6dfsg-1-deb_cv1` の2タグのみ）に解決される。さらにこのタグは Quay 側にも存在しない（`{"tags":[]}`）。実在するのは `0.23.4--h5f740d0_0`、`--hadf994f_1/_2/_3`、`--h125f33a_4/_5`。CWL の DockerRequirement は実行時に必ず pull するためそのままでは動かない。**修正案: `quay.io/biocontainers/fastp:0.23.4--h125f33a_5`**（fastp 現行は 1.3.6 なので例の更新も検討） |
| CONFIRMED | 506, 73 | 「CWLは TRE環境（Seven Bridges、**Terra、AnVIL**）で価値がある」→ **Terra は WDL 専用**（AnVIL も Terra 上）。Dockstore 公式は "Only the WDL language is supported." と明記。CWL が標準なのは Seven Bridges / CGC。**演習14-1のヒント（L779）が「CWL/WDL」と正しく併記しているのとも矛盾** |
| CONFIRMED | `ch14.bib` | 章末リストは[1]〜[11]だが bib は8件のみ。[9] CWL・[10] cwltool・[11] Dockstore が**未登録**。逆に[6] Grüning Bioconda は**本文未引用** |
| LIKELY | 332-336 | `nf-core/rnaseq --genome GRCh38` → 現行 usage docs は `--fasta`/`--gtf` を標準例とし、iGenomes の `--genome` は "provided for legacy compatibility but is **not recommended** for new analyses"（遺伝子アノテーションが古い）。`--input`/`--outdir`/`-profile docker` は変更なし |
| LIKELY | 205 | `snakemake --use-conda` → 誤りではない（9.23.1 でも有効・警告なし）が、公式のv8移行ガイドで **deprecated** とされ現行推奨は `--software-deployment-method conda`（`--sdm conda`）。**「削除された」とは書かないこと** |
| LIKELY | 290, 856 | Nextflow 公式ドキュメントの URL が 302 で **`https://docs.seqera.io/nextflow/`** へ転送。`ch14.bib` の `nextflow_docs` も同様 |
| LIKELY | 572 | 「nf-core（**100+**パイプライン）」→ 現在 **153パイプライン**（リリース版約100、アーカイブ13、dev専用53）。サイト表記は "the 153 pipelines that are currently available" |
| UNCERTAIN | 527 | `release-111`（2024年）→ 最新は **release-116**。Ensembl は旧リリースを恒久保持するため URL 自体は生きており実害は小さい。リリース番号を変数化して「読者が差し替える箇所」と明示する手もある |

**正しいと確認できたもの**: L324 の `--cluster`/`--slurm` の留保（v7で実在、v9.23.1では削除され executor plugin へ移行）、Nextflow の `input: path(fastq)`（strictパーサ・`nextflow lint` とも警告なし）、`cwlVersion: v1.2`（最新仕様は v1.2.1 で誤植修正のみ、v1.3 は未リリース）、cwltool の `--cachedir` を「限定的」とする表現。実体の Snakefile + config.yaml は snakemake 9.23.1 でドライラン成功（13ジョブ、DAG正常解決）。

---

## §15 `15_container.md`（11件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 496-502 | **CUDA のバージョン互換性の説明が誤り**。「3つのバージョンが**一致**」「ドライバ12.2環境でCUDA 12.4コンテナはエラー」→ CUDA 11.1以降、**同一メジャーリリース内では minor version compatibility が保証**（最低ドライバ >= 525）。PyTorch/TensorFlow の公式コンテナはこの仕組みに依存しており本文は現実と逆。実行専用コンテナには `nvcc` が入っていないことが多く「`nvcc --version`で確認」も常には成り立たない。**修正案: 「互換である必要がある」に改め、例をメジャー跨ぎに差し替え** |
| CONFIRMED | `scripts/ch15/Dockerfile:2-3`, `Dockerfile.multistage:6`, `apptainer.def:2` | 3ファイルとも `condaforge/mambaforge:24.3.0-0` のまま。**本文161行は「Mambaforge は非推奨化されたため新規の例では Miniforge3 に揃える」と明言**し、本文の全コード例（115, 177, 226, 409, 424, 549, 621）は `miniforge3` を使う。**書籍の主張と付属コードの正面衝突** |
| CONFIRMED | `scripts/ch15/environment.yml:4-7` | チャネルが `bioconda` → `conda-forge` → `defaults` の順。**列挙順がそのまま優先度**なので、Bioconda 公式が要求する「conda-forge 最高優先」と逆。strict priority 下で依存解決が壊れる典型パターン。`defaults` も2024年8月に推奨から除外（Anaconda 商用ライセンスの問題も） |
| CONFIRMED | 351 | 「biocondaに登録された**1万以上**のツール[4]」→ Grüning et al. 2018 は "over **3,000**"。数値自体は2026年時点で妥当だが引用が支持していない |
| CONFIRMED | 1105 | [12] MLflow の **DOI `10.1109/DSAA.2018.00006` が "Message from the DSAA 2018 Program Co-Chairs"（巻頭挨拶）に解決される**（Crossref API で確認）。MLflow 論文（*IEEE Data Eng. Bull.* 41(4):39-45）にDOIは存在しない。`ch15.bib` にはDOIが無く章末リストだけに誤DOIが付いている。**修正案: DOI を削除し `http://sites.computer.org/debull/A18dec/p39.pdf` へ** |
| CONFIRMED | `ch15.bib:24` | BioContainers の著者に**実在しない名前**。`Alberín, Saulo`/`Boekel, Hannes`/`Gober, Julianus` は誤記（正: `Alves Aflitos, Saulo`/`Röst, Hannes L`/`Pfeuffer, Julianus`）で、**`Peltzer, Alexander` と `Ternent, Tobias` はこの論文の著者ではない**。章末は "et al." 表記のため表示上は露見しないが bib が真実の源 |
| CONFIRMED | 1083-1115 | 参考文献**17件中12件が本文未引用**（本文は[1] 51行、[3][4] 351行、[2] 396行、[7] 712行の5件のみ）。特に **[11] wandb / [12] MLflow / [13] hydra / [14] DVC は §15-6 で節を割いて解説されているのに引用番号が付いていない** |
| LIKELY | 549-557, 620-634 | `conda-lock` / `uv` が**未インストールのまま実行**されている。miniforge3 ベースイメージに含まれるのは conda/mamba/python のみで、`docker build` すると `conda-lock: command not found` で失敗。**修正案: `RUN mamba install -y -n base conda-lock && conda-lock install ...`** |
| LIKELY | 11, 47 | 「どの計算機でも同一の実行環境を再現」「**根本的に解決する**」→ コンテナは**CPUアーキテクチャを吸収しない**。Apple Silicon（arm64）でビルドしたイメージは HPC の x86_64 で `exec format error`、逆に amd64 のみの BioContainers を Mac で動かすと QEMU で著しく遅い。**章内に `--platform`/`buildx`/arm64/amd64 の言及がゼロ**（grep で0ヒット）。本書の想定読者（MacBook → HPC）が最も高頻度で踏む罠 |
| LIKELY | 394-398 | 「Dockerデーモンはroot権限で動作するため」→ Docker 20.10 以降 **rootless mode** が正式提供。HPC で避けられる実際の主因は「`docker` グループ所属＝実質ホストroot相当」という権限モデルと共有多テナント非対応。現状の書き方は「原理的に rootless にできない」という誤解を生む |
| LIKELY | 415 | `docker save ... \| apptainer build ... docker-archive:/dev/stdin` → Apptainer 公式が文書化しているのは `docker-archive:file.tar` のファイル指定のみ。docker-archive はアーカイブ内をシークするためパイプでは失敗しうる。**修正案: 2段階に分割** |
| LIKELY | 396 | 「**Apptainer**（旧Singularity）」→ 単なる改名ではない。2021-11-30 に Linux Foundation 傘下へ移行して改名した一方、**Sylabs 社は SingularityCE として別フォークを継続**。施設によって `singularity` の実体が異なり機能差がある |
| LIKELY | 928-929 | JSONL 出力例が実装と不一致。`scripts/ch15/experiment_logger.py` の `_get_git_hash()` は `git rev-parse HEAD` をそのまま返すため **40文字フルハッシュ**（例は `a1b2c3d` の短縮形）。timestamp も `datetime.now(timezone.utc).isoformat()` でマイクロ秒付き |

**記載漏れ**: Docker Desktop のライセンス条件（**従業員250名以上または年商1,000万ドル以上**の組織での業務利用は有償。大学・研究所・企業ラボの読者に直接影響）、`COPY` vs `ADD` の挙動差と「原則 COPY」の指針、`--user` / rootless コンテナ（コンテナ内rootで書いたファイルがホストでroot所有になる問題）。

**正しいと確認できたもの**: `validate_dockerfile.py` の API と4項目、`experiment_logger.py` の関数名・引数・戻り値、BioContainers `samtools:1.20--h50ea8bc_0`（quay.io API でタグ実在確認）、`condaforge/miniforge3:24.3.0-0`（Docker Hub にタグ実在）、Baker 2016 の「1,500名以上」「70%以上」。

---

## §16 `16_hpc.md`（10件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 247 | 「ステップ1が失敗した場合、ステップ2以降は**自動的にキャンセルされる**」→ Slurm 既定では **PENDING のまま残り続ける**（Reason: `DependencyNeverSatisfied`）。自動キャンセルは `DependencyParameters=kill_invalid_depend` 設定サイトのみ。**読者が信じると失敗パイプラインのゾンビジョブがキューを占有し、共有クラスタで実害が出る。** `scripts/ch16/pipeline_submit.sh` 末尾の「全キャンセル」行と紐づけるとよい |
| CONFIRMED | 667 | `aws s3 cp s3://sra-pub-run-odp/sra/SRR000001/ . --no-sign-request` が**そのままでは動かない**。末尾スラッシュ付きプレフィックスには **`--recursive` が必須**。SRA Open Data の実体は `s3://sra-pub-run-odp/sra/SRR000001/SRR000001` |
| CONFIRMED | 155, 171-174, `scripts/ch16/array_job.sh:7,23,26` | `#SBATCH --cpus-per-task=8` に対し `hisat2 -p 8 \| samtools sort -@ 4`。**`samtools sort -@ 4` は追加で4スレッド起動する**（`-@` は additional threads）ため合計12スレッド以上を8コアで走らせる。cgroup の cpuset で圧縮されコンテキストスイッチ増による性能劣化。本章 §16-1「リソース申請の考え方」とも矛盾。**修正案: `-p 6` + `-@ 2`（合計8）か `--cpus-per-task=12`。「パイプ全体のスレッド合計が `SLURM_CPUS_PER_TASK` を超えないように」を明記** |
| CONFIRMED | 506, 514 | 「`$TMPDIR` は**Slurmがジョブごとに割り当てる**一時領域」→ Slurm 本体は既定で `$TMPDIR` を設定しない。ジョブごと専用 `/tmp` は `job_container/tmpfs` プラグイン（`NamespaceType=namespace/tmpfs` + `PrologFlags=Contain`）を管理者が明示有効化した場合の機能で**既定では無効**。多くのサイトは独自 prolog/spank で用意し変数名も施設ごとに異なる |
| CONFIRMED | 765-778 | **本文中に `[N](URL)` 形式の引用が1件も存在しない**（grep で0件）にもかかわらず章末に[1]-[8]が並ぶ。Slurm コマンド仕様、3-2-1 ルール、rsync アルゴリズム、ストレージ階層など出典を示すべき主張が多数ある。[6] Bailis & Kingsbury と [7] CISA は本文のどの記述に対応するかも不明 |
| CONFIRMED | `ch16.bib:1`, `ch17.bib:1` | bib 冒頭コメントの章番号が誤り（`% §14 HPC` → §16、`% §15 パフォーマンスと最適化` → §17） |
| LIKELY | 199, 211, 221, 232 | 「`sbatch --parsable` は**ジョブIDのみを返す**」→ man は "Outputs only the job ID number **and the cluster name if present**. The values are separated by a **semicolon**." マルチクラスタ構成では `12345;mycluster` が返り依存指定が壊れる。**修正案: `JOB1=$(sbatch --parsable ... \| cut -d';' -f1)`** |
| LIKELY | 395 | rsync の「**`-v`は進捗表示**」→ `-v` は verbose（転送ファイル名の一覧）。進捗は `--progress`（`-P` = `--partial --progress`）。**本文自身が412-416行で正しく書いており内部矛盾** |
| LIKELY | `scripts/ch16/gpu_train_job.sh:19` | `source activate ml_env` は conda 4.4 以降の非推奨形式で、非対話シェル（＝Slurmバッチジョブ）では動かないことが多い。**本文318-319行は正しく `conda.sh` + `conda activate` を教えており食い違い** |
| LIKELY | `scripts/ch16/ssh_config.example:36,45` | `LocalForward 8888 localhost:8888` は**ログインノードの** localhost へ転送。本文§16-3（425行）は「**計算ノード上で実行すること**」と明示し `ssh -L 8888:compute-node-01:8888` を教えている。この設定例に従うとログインノードでJupyterを起動する運用（§16-1が禁じる行為）に誘導される |
| UNCERTAIN | 4 | エピグラフ「孫悟空, 鳥山明『ドラゴンボール』其之二百三十三, 第20巻 (集英社, 1990)」の話数・巻数・発行年を確認できず（元気玉の初使用は其之二百三十六前後との情報もある） |

**記載漏れ**: tmux / screen（長時間ジョブの監視・切断対策）、`--ntasks`（本文は全編 `--cpus-per-task` を正しく使っており**混同はない**が、MPIジョブや `--ntasks` を要求する施設テンプレートに遭遇した読者が判断できない）。

**正しいと確認できたもの**: Slurm 状態コード表、`#SBATCH` 配置ルール、`%A`/`%a`、`--array=1-100%10`、クラウド用語（`m5.xlarge` = 4 vCPU/16 GB、`ap-northeast-1` = 東京）。

---

## §17 `17_performance.md`（6件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 854 vs 865 | CRAM の圧縮率が**章内で矛盾**。854行「ファイルサイズ | 基準 | **BAMの30〜60%**」（= 40〜70%削減）vs 865行「**30〜60%のサイズ削減**」（= BAMの40〜70%）。よく引用されるのは「BAMより30〜60%小さい（＝BAMの40〜70%）」 |
| CONFIRMED | 342-381, 426, 950, 1015 | **`memory_profiler` は開発終了**。PyPI 最終リリース 0.61.0（2022-11-15）、配布ページに "This package is no longer actively maintained." と明記。独立小節を割き、まとめ表・演習17-4でも第一選択として提示している。**代替: `memray`、`scalene`、標準ライブラリ `tracemalloc`** |
| CONFIRMED | 1055 | 参考文献[7] Apache Parquet が**本文未引用**。本文の引用出現順は [1][2][3][4][5][6][9][10][8] で [7] が欠番かつ [8] が [9][10] の後に登場 |
| LIKELY | 496-500 | 「**CPythonにはGILがあり**」と無条件断定 → Python 3.13 で free-threaded build（PEP 703）が実験導入され、**PEP 779 の受理により 3.14 で公式サポート（Phase II、既定ではない）**。**本リポジトリ自体が 3.14.6 で動作している。** 演習17-3のヒント（995行）も同様。**修正案: 「既定のCPythonビルドには…」と限定し、`python3.14t` の存在、単一スレッド性能1〜8%のオーバーヘッド、未対応拡張モジュールを注記** |
| LIKELY | 710 | 「Numbaが対応していない操作（文字列処理、**辞書操作**など）」→ Numba は nopython モードで **`numba.typed.Dict`** をサポートし Unicode 文字列も限定サポート。**修正案: 「Python の汎用オブジェクト（任意型の dict、クラスインスタンス等）や複雑な文字列処理は扱いにくく、型付きコンテナへの書き換えが必要」** |
| LIKELY | 190-194 | `n_workers = min(os.cpu_count() - 1, len(tasks))` の2つの問題。(1) `os.cpu_count()` は取得できない環境で `None` を返し `TypeError`。(2) より重要な点として、**cgroup/コンテナ/Slurm 配下ではホスト全体の論理コア数を返す**ため、本文自身の52行「HPCのジョブ内では `SLURM_CPUS_PER_TASK` や cpuset 制約を優先」、67行、719行のエージェント指示例と矛盾。**修正案: `int(os.environ.get("SLURM_CPUS_PER_TASK") or os.process_cpu_count() or 1)`**（3.13+ の `os.process_cpu_count()`） |

**記載漏れ**: py-spy / scalene（特に py-spy は「すでに走っているHPCジョブに後から attach できる」点で §16 との接続で実用価値が高い）、`__slots__` / Dask / Polars streaming（polars は依存に入っているが §17 では未使用）。`pyarrow` が pyproject.toml の dependencies に無く `scripts/ch17/file_format_bench.py` が `uv sync` 環境で実行できない（本文840行は「pyarrow が必要」と正しく注記済みなのでリポジトリ側の漏れ）。

**実行検証で問題なしを確認**: TPM正規化 slow/fast（数値一致、列合計=1,000,000、実測**135倍**高速 → 「数十〜数百倍」は妥当）、cProfile スニペットと出力カラム説明、Amdahl の数値（p=0.1 → 1.111倍、p=0.8/s=2 → 1.667倍）、bisect 例（n=10⁶ で実測**8,227倍** → 「数千倍」✓）、メモリ見積り（160MB/8GB/80MB）、Welford バッチ結合（pandas `var(ddof=1)` と最大誤差 1.8e-15）、ジェネレータチェーン・itertools・gzip、Knuth[1]/Amdahl[2] の DOI・巻号ページ（引用文の p.268 も正しい）。

---

## §18 `18_documentation.md`（6件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 354 | **§11-3 への参照が誤り。正しくは §11-1** |

（§18 は他に5件の指摘があったが、統合報告作成時点で詳細が取得できていない。`docs/review/` に §18 単独の再レビューを行うことを推奨する。）

---

## §19 `19_database_api.md`（19件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 425-437, 126-137 | **SPARQL クエリが `PREFIX rdfs:` 欠落で HTTP 400**。実測エラー: `{"exception": "Invalid SPARQL query: Prefix rdfs was not registered using a PREFIX declaration", "metadata": {"line": 8, "positionInLine": 11}}`。裏付け3重 — (1) 宣言なし400/ありで200、(2) W3C SPARQL 1.1 に既定プレフィックスは存在しない、(3) **UniProt 公式サンプルクエリ126件の全数調査で `rdfs:` 使用例は全件が `PREFIX rdfs:` を宣言、未宣言0件**。当エンドポイントは Virtuoso でなく **QLever**（`X-Powered-By: sib.swiss`）でプレフィックスの暗黙定義を一切行わない。**付属スクリプトには宣言があり本文だけが欠落** |
| CONFIRMED | 433 | **GO の URI が誤りで、エラーを出さず静かに0件を返す**。`http://purl.uniprot.org/go/0005739` はグラフ中に**主語としても一切存在しない**。正しい `http://purl.obolibrary.org/obo/GO_0005739` ではヒト **3,872件**がヒット。**最も発見が遅れる型のバグ** |
| **★注意** | — | **上記2点を修正する際、述語 `rdfs:label` は変更してはならない。** 検証: ヒト `up:Protein` 総数 vs `rdfs:label` 保有数 = **210,709 / 210,709（被覆率100%）**、P04637 の `rdfs:label` = `"Cellular tumor antigen p53"`。**unreviewed（TrEMBL）エントリでは `up:recommendedName/up:fullName` が空**で `up:submittedName/up:fullName` 側にしか名前がないため、`up:recommendedName` へ書き換えると **TrEMBL エントリが黙って全件脱落する**。書籍の選択のほうが堅牢 |
| CONFIRMED | 638 | Google Cloud Storage を「**認証不要**」と誤記 → 実際は **requester pays** で認証・課金が必須。`gsutil` は2027年3月に同梱終了 |
| CONFIRMED | 1039 | Biomni 論文の**第一著者が誤り**（正: **Kexin Huang**）。かつ **2026-07-09 に *Science* 掲載済み**（DOI: 10.1126/science.adz4351）でプレプリント引用は差し替え可能 |
| CONFIRMED | 624 | NCBI Aspera FTP のパスが **404** |
| CONFIRMED | 519, 521 | **Ensembl 116 が現行サイトの最終リリース**。REST API・公開MySQL・FTP は e!116 で最終更新、**2026年夏に ensembl.org は beta.ensembl.org へリダイレクト**、USEast/Asia ミラー廃止。後継は GraphQL(Thoas)/refget/Beta FTP。「認証不要で手軽に試せる、最初に覚えたいAPI」という推奨は移行先を示さないと読者を袋小路へ導く。**BioMart の後継は公式にも未提示なので「移行先未定」と正直に書くのが安全** |
| CONFIRMED | 519 | Ensembl REST の**レート制限が未記載**。実測ヘッダ `x-ratelimit-limit: 55000` / `x-ratelimit-period: 3600` = **55,000リクエスト/時（IP単位）**、超過時 `Retry-After`。NCBI についてはレート制限を強調しているので**記述の非対称**（誤りではなく欠落） |
| CONFIRMED | 525 | TogoWS の実態が「手軽に試せる」水準にない。**応答が10〜48秒**（`entry/uniprot/P04637` の実測が47.8秒）で25〜30秒のタイムアウトでは全リクエスト失敗。`entry/pdb/1a3n` → **404**、`entry/uniprot/P04637.json` → **500**。HTTP/HTTPS 両方200だが自動リダイレクトなし。サービス終了の告知はなし |
| CONFIRMED | 872 | ArrayExpress → BioStudies 移行が**リダイレクトで実証**（`/arrayexpress/` → 302 → `/biostudies/arrayexpress`、個別実験ページも同様） |
| CONFIRMED | 236 | PDB ID の失効時期。wwPDB 公式の逐語「**By 2028** 4-character PDB IDs will be fully allocated」「Starting **July 21, 2027**... New 4-character PDB IDs will not be issued」。拡張IDは接頭辞込みで**12文字**（`pdb_` + 英数字8文字、例 `pdb_1000axyz`）。現在の公開エントリ数 **256,840**。**PDBe API は拡張IDを既に受理**（`/pdbe/api/pdb/entry/summary/pdb_00001a3n` → 200）、RCSB Data API は未対応（404）。**本文に4文字前提の正規表現（`^[0-9][A-Za-z0-9]{3}$` 相当）があれば要見直し** |
| CONFIRMED | 533 | BioMCP「**12種**のバイオメディカルエンティティ」→ **約30の情報源**（v0.8.25、2026-07-08、MIT） |
| CONFIRMED | — | NCBI E-utilities の**レート制限は変更なし**（APIキーなし3 req/sec、あり10 req/sec）。**本書の記述はそのまま有効**。※NCBI Datasets は5/10 req/sec で別物なので混同に注意 |
| CONFIRMED | — | 参考文献[7] が**本文未引用** |

（§19 は上記以外にも指摘があったが、統合時に詳細が確定できなかったものがある。）

---

## §20 `20_security_ethics.md`（8件＋記載漏れ5件）

| 確信度 | 行 | 内容 |
|---|---|---|
| **CONFIRMED** | **356** | **Claude Consumer の「学習非利用が既定」は事実と逆**。Anthropic の現行文言は "We may use your Inputs and Outputs to train and improve Anthropic AI models, **unless you opt out**" ＝ **opt-out 方式で既定は学習利用**。保持も、学習利用を許可した場合 "we may retain your data in a de-identified format for **up to 5 years** in our model training pipelines"。「30日程度」は削除会話のバックエンド消去期限であって既定保持期間ではない。**本章は「クラウドAIに何を渡してよいか」を判断させる表なので実害が最大。** 365行の一般論も要見直し |
| CONFIRMED | 309 | ゲノムデータが個人情報に「**該当しうる**」→ 引用元ガイドライン[11]自身が「全核ゲノムシークエンスデータ等は『個人情報』に**該当**」と断定。全核ゲノム/全エクソーム/SNPアレイは**個人識別符号**で該当性に例外はない |
| CONFIRMED | 293 | **JGA の運営主体と申請先が誤り**。「運営: DDBJ / 申請先: データ提供者が指定するDAC」→ 公式は「JGA へのデータ登録および利用は**DBCLS**で審査承認」。申請は humandbs.dbcls.jp への**一元申請で中央審査委員会方式**（DAC 方式ではない）。dbGaP/EGA との手続きの違いは申請実務に直結 |
| CONFIRMED | 309 | **令和8年改正個人情報保護法（2026-07-17 公布）が未反映**。「制度見直しが継続している」→ 本レビュー日時点では「改正法が成立・公布済み」が正確。施行は公布から2年以内の政令指定日で**政令未制定** |
| CONFIRMED | 779 | JST 基本方針の文書名が誤り。「オープンサイエンス**推進**に向けた…基本方針」→ 正しくは「オープンサイエンス**促進**に向けた研究成果の取扱いに関する**JSTの**基本方針」（令和7年4月版が最新） |
| LIKELY | 357, 365, 408 | **ZDR を機密データの解として提示しているが、最新世代モデルが ZDR 非対応である但し書きがない**。Claude Fable 5 は30日保持必須で ZDR 組織からのリクエストは400エラー。Anthropic の商用向け解説でも既定保持は「custom retention を設定しない限り無期限、Enterprise のカスタム設定でも**最小30日**」 |
| LIKELY | 630 | NEDO「**ムーンショット事業で先行導入**」が引用先[20]に**存在しない**。同ページはムーンショットに一切言及せず、内閣府2021年4月ガイドラインを受け2023年12月改定、助成事業は「2024年度以降に開始するもの」から適用、と述べるのみ。提出「事業者判断」は正しい |
| LIKELY | 310 | 次世代医療基盤法「**2024年改正**」→ 仮名加工医療情報を導入した改正法は **2023年5月26日公布・2024年4月1日施行**。改正年と施行年の混同 |
| LIKELY | 112-116 | `scan_content` の署名が実体と不一致（実体は第3引数 `patterns` を持つ）。`SECRET_PATTERNS` は「一部抜粋」明記あり（実体6/本文3）だが関数署名は抜粋と断っていない |
| — | 761 | OWASP のプロジェクト名が "OWASP GenAI Security Project" に改称、2025年版は genai.owasp.org/llm-top-10/ へ移動。prompt injection は **LLM01＝第1位**なので198行の「最も重大なリスクの一つ」は控えめすぎる |

**記載漏れ**: NIH DMS Policy と **NOT-OD-25-083**（2025-04-04 発効、懸念国からの controlled-access データアクセス禁止）、**NOT-OD-26-046**（DMP 必須要素改定、2026-05-25 以降の申請に新様式必須）、**シークレット漏洩後の対処**（`grep -rn "filter-repo\|BFG" chapters/` → **0件**。20-1-1 は予防のみでライフサイクルの「失効」（20:31）と対応していない）、**EU AI Act**（`grep -rn "AI Act"` → **0件**）、ICMJE/CRediT。

**正しいと確認できたもの**: 科研費DMP（令和6年度以降の全課題で作成義務・**提出不要**、メタデータは KAKEN/CiNii Research に連携公開）、AMED の令和8年4月以降の提出義務、HIPAA Safe Harbor 18識別子、k≥5、Gymrek 2013 の再識別手法、個人遺伝情報ガイドライン[11]が令和6年3月1日一部改正で**現行有効**、引用番号[1]-[34]の欠番・重複・未引用**ゼロ**、`scripts/ch20/anonymize_metadata.py` の本文との整合（`generalize_age(35)` → `'30-39'` を実行確認）。

---

## §21 `21_collaboration.md`（11件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 87, 90-126, 128, 138 | `format_question.py` が本文と不一致。本文は `collect_environment(packages)` が `os`/`python`/`architecture` を返し `format_question(...)` があると説明 → 実体は `collect_environment()`（**引数なし**、モジュール定数 `_TARGET_PACKAGES` 使用）でキーは `python_version`/`os_info`。**`format_question` 関数は存在しない**（実際は `format_biostars_question`, `format_github_issue`）。ランタイム確認 `hasattr(fq,'format_question') == False`。138行の指示例も実行不能 |
| CONFIRMED | 326, 329-354, 356 | `review_helper.py` の **`summarize_diff` / `format_pr_description` / `DiffSummary` が存在しない**。実体の公開関数は `parse_diff`/`check_type_hints`/`check_docstrings`/`generate_review_checklist`、データクラスは `DiffFile` |
| CONFIRMED | 544, 574, 577-610, 612, 622 | `progress_report.py` が `--oneline` を受け付けない。本文は `parse_git_log` を「`git log --oneline` の出力をパース」と説明し544行で読者に実行させ622行でスクリプトに渡すよう指示 → 実体は **`%H\|%s\|%ai` のパイプ区切り3フィールド前提**。ランタイム確認 `parse_git_log('abc1234 fix: something')` → `[]`（警告「不正な形式の行をスキップ」）。**読者が本文どおり操作すると必ず空レポートになる**。`generate_report` の署名も本文 `(log_text, results, next_steps, issues, date)` に対し実体は `(commits, period)`。**修正案: 544行を `git log --since="1 week ago" --no-merges --format="%H\|%s\|%ai"` に** |
| CONFIRMED | 706, 709-741, 745 | `analysis_intake.py` の **`REQUIRED_COLUMNS` / `IntakeResult` が存在しない**。実体の署名は `validate_metadata(metadata_rows, required_columns)` |
| CONFIRMED | 832 vs `07_git.md:583` | **GPL の伝播について章間で矛盾**。演習21-3ヒント「直接取り込む場合と**インポートして使う場合では影響範囲が異なる**」は「`pip install` して import するだけなら GPL は及ばない」と読め、§7 の演習7-3ヒント（「リンク・インポートして利用するソフトウェアも GPL 互換で公開する必要」）および FSF の立場と矛盾。**読者が法的リスクを負う** |
| CONFIRMED | 790 vs 518 | まとめ「パーミッシブ同士は互換性あり」が本文518行の「Apache-2.0 → MIT は△ 要注意」と矛盾。**修正案: 「パーミッシブ同士でも Apache-2.0 の NOTICE・特許条項は保持が必要」** |
| CONFIRMED | 551 | 「Wilson et al.(2017)[6]が提唱する『Good enough practices』でも**定期的な進捗記録**の重要性が強調されている」→ 同論文の Collaboration 節の推奨は「共有 to-do リスト（notes.txt/todo.txt）」「コミュニケーション戦略の決定」等で、**定期的な進捗報告・ステータス報告は推奨していない**。"Keeping track of changes" 節が CHANGELOG.txt を推奨するのみ |
| CONFIRMED | 854, 884, `ch21.bib:31-38` | 『Producing Open Source Software』の**出版社と年が誤り**。O'Reilly は**第1版のみ**（サイトに "Order print copies of **v1** (O'Reilly Media)"）。第2版はクラウドファンディングによる**自主出版**で、サイトの日付入り告知は "**2020-08-14**: The 2nd Edition rewrite is finished"。CC BY-SA 4.0。第3版は存在しない。**修正案: `Fogel, K. Producing Open Source Software (2nd ed.). 2020 (自主出版, CC BY-SA 4.0)`** |
| CONFIRMED | 878 | Biostars のサイト名「Pair of Scissors」→ **"Bioinformatics Answers"**。`references/ch21.bib:12` は既に正しいので**章側だけ**修正 |
| CONFIRMED | 452-476 | Bioconda の meta.yaml 例が**lint に通らない**。**`about:` が実質必須**（`missing_home`/`missing_summary`/`missing_license` の3つの lint check）、`build: script:` 欠落（`{{ PYTHON }} -m pip install . -vvv --no-deps --no-build-isolation` 相当が必要）、**`run_exports` 欠落**（`missing_run_exports`）、`license_file` 欠落（`gpl_requires_license_distributed`）、`extra: recipe-maintainers:` は公式テンプレートにあり慣例。pure-Python なら `noarch: python` も通常必要。`sha256: abc123...` はプレースホルダと明示すべき |
| LIKELY | 513-521 | ライセンス互換性表に **GPL-2.0 / LGPL / AGPL がない**。(a) **Apache-2.0 は GPL-3.0 とは互換だが GPL-2.0 とは非互換**という頻出の罠が表にない。(b) **LGPL（動的リンクなら伝播しない）と AGPL（§13 のネットワーク配信条項）は書籍全体で一度も言及がない**（grep 0件）。バイオインフォではウェブサービス公開時に AGPL が効くケースがある |
| LIKELY | 890 vs `ch21.bib:53` | Meta SO 投稿タイトルが章「Policy: Generative AI (e.g., ChatGPT) is banned」/ bib「**Temporary** policy: …」で不一致。投稿から "Temporary" が外れたため**章側が新しい**。bib を章に合わせる |
| CONFIRMED | 3-5 | Stan Lee の引用が**原文と異なる**。原文（*Amazing Fantasy* #15, 1962 最終パネル）は "And a lean, silent figure slowly fades in the gathering darkness, aware at last that in this world, **with great power there must also come -- great responsibility!**"。しかも**ナレーションであり Uncle Ben の台詞ではない**（Ben への帰属は1972年の音声劇が初出で、コミックでは1987年頃まで確立していない）。「with great power comes great responsibility」は2002年の映画で広まった近代的パラフレーズ |
| UNCERTAIN | 262 | Stack Overflow の生成AIポリシーの現行内容を確認できず（stackoverflow.com は本環境から取得不可）。※別調査では**2026-07-19 時点でも全面禁止が維持**と確認。ただし「質問文の生成やリライトも含む」の根拠は meta 421831 ではなく **Help Center の "in part or in whole"** に付け替えるのが正確 |
| UNCERTAIN | 3-4 | 『ONE PIECE』第10巻・第90話の対応。**第90話が第10巻収録は確認**（第10巻は第82-90話、「OK, Let's STAND UP!」、集英社、**1999-10-04**、ISBN 4-08-872773-8）。第90話のタイトルは「何ができる」で引用文が答える形になっており整合的だが、**パネル本文そのものは未検証** |

**正しいと確認できたもの**: Bacchelli & Bird（ICSE 2013, pp.712-721, DOI 10.1109/ICSE.2013.6606617）、Wilson et al. 2017 の全著者（Wilson G, Bryan J, Cranston K, Kitzes J, Nederbragt L, Teal TK, *PLoS Comput Biol* 13(6):e1005510）、Raymond "Smart Questions" の2014年（Revision 3.10, 2014-05-21 が最新）、XY Problem（xyproblem.info）、GitHub PR レビュー docs、Biostars の2009年設立（"created in late 2009"、公開は2010-01-18）。

**注意**: `https://www.catb.org` は**TLS証明書が不一致**（証明書が無関係なドメインをカバー）。本書が使う `http://` URL は正常だが、HTTPS へ「アップグレード」すると壊れる。

---

## はじめに `hajimeni.md`（10件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 10 | SWE-bench の起点が誤り。「最先端のAIモデルは**2024年半ばの約50%**から」→ 2024年半ばの SOTA は**約33%**（Claude 3.5 Sonnet 2024年6月 = 33.4%、GPT-4o 2024年8月 = 33.2%）。約49〜50%到達は**2024年後半**（10月 upgraded Claude 3.5 Sonnet = 49%、12月 o1-preview = 49%）。終点「2025年末に80%超」は正しい。**冒頭の主張で、実際より進歩を小さく見せる方向に誤っている** |
| CONFIRMED | 26 | **Thorgeirsson 研究の結論を過度に一般化**。「計算機科学の学業成績と文章力がともに…**この効果は汎用的な推論能力を統制しても消えなかった**」→ 統制後も有意を維持したのは**計算機科学の成績のみ**（partial r=0.281, p=0.005）。**文章力は統制後に有意でなくなった**（partial r=0.186, **p=0.066**, n.s.）。100名・「CSは文章力の約2倍の寄与」（ΔR² = 0.125 vs 0.059）・CHI '26 掲載は正しい。**この研究は本書の中核的論拠で hajimeni:26・:58・付録A:25 の3箇所で参照されており、訂正すると本書の主張はむしろ強化される** |
| CONFIRMED | 48 | 「AI Scientistは実験の**42%**がコーディングエラーで失敗し、Kosmosは1回の実行で42,000行のコードを生成する[23]」→ 一つの引用が二つの主張を担っているが、**42% は Kosmos 論文にも Sakana 原論文[20]にも存在しない**。出典は第三者評価 **arXiv:2502.14297**（"Evaluating Sakana's AI Scientist"）の "42% of experiments failed due to coding errors"。Kosmos の 42,000行は**平均値**（200エージェントロールアウト合計の平均）なので「平均42,000行」と明記すべき |
| CONFIRMED | 107 | 『Dr. Bonoの生命科学データ解析』に**第2版がある**（2021年3月、MEDSI、ISBN 978-4-8157-3011-6、211p）。初心者への推薦図書として旧版を挙げている。※『生命科学者のためのDr. Bonoデータ解析実践道場』（2019/第2版2023）とは別シリーズなので混同しないこと |
| CONFIRMED | 106 | 『生命科学研究のためのデジタルツール入門 第2版』の責任表示は **「坊農秀雅, 小野浩雅 監修」**。坊農氏の単著ではなく**共同監修**。書名・副題・出版社・出版年（2024.6）・ISBN（978-4-8157-3106-9）は正しい |
| LIKELY | 46 | Genesis Mission の目標が「米国の**科学的生産性**を倍増」→ 公式文言は "double the productivity and impact of American science **and engineering**"。また倍増目標は大統領令本文の条項ではなく DOE／ホワイトハウスの発表文言。署名日2025-11-24 は正しい |
| LIKELY | 46 | 「AlphaFoldによるタンパク質構造予測は2024年のノーベル化学賞を**受賞し**」→ 賞は AlphaFold（ソフトウェア）にではなく **Demis Hassabis と John Jumper** に、かつ**賞の半分**（残り半分は David Baker の計算タンパク質設計） |
| UNCERTAIN | — | [20] Nature論文の書誌が確定している（*Nature* **651**(8107), 914–919, 2026-03-25、PMID 41882133）が本書は巻・号・ページを欠く。著者に "Lu, C." が2名（Chris Lu / Cong Lu）おり「Lu, C. et al.」は曖昧 |
| UNCERTAIN | — | [21] AI co-scientist の「Gemini 2.0ベース」は **v1**（2025-02-26）の abstract と一致し正しい。現行版は改題され abstract も "built on Gemini"（版番号なし）に変更済み |

**正しいと確認できたもの**: SWE-bench Verified 500問、Claude Opus 4.5 = 80.9%、GPT-5.2 = 80.0%（正確には "GPT-5.2 **Thinking**"）、Octoverse 2025 の986 millionコミット、SemiAnalysis の4%／年末20%推計、Copilot 20M+ users（"all-time" であってアクティブではない点のみ注意）、Copilot 46%、Karpathy の命名日と status ID、Collins WOTY 2025 = "vibe coding"（2025-11-06 発表）、Nature論文の実在と Sakana AI 帰属、Biomni の「105のバイオソフトウェアと59のデータベース」、理研 TRIP-AGIS（正式英名 Advanced General Intelligence for Science Program、PD 泰地真弘人）、『改訂 独習Pythonバイオ情報解析』の全書誌情報。引用番号[1]–[31]の本文・文献リスト対応も問題なし。

---

## 付録B `appendix_b_cli_reference.md`（11件）

**対照表の11行が要修正。付録単位での全面改訂を推奨する。**

| 行 | 内容 |
|---|---|
| モデル表6セル中5セル | Claude: Opus 4.7 → **Opus 4.8**、Sonnet 4.6 → **Sonnet 5**（Haiku 4.5 は据え置き）。Codex: GPT-5.5/5.4/5.4-mini → **GPT-5.6 Sol / Terra / Luna** |
| 31 | `--full-auto` が**公式に非推奨化**。`--sandbox workspace-write` へ |
| 33 | `approval_policy` に **granular オブジェクト形式**が追加（カテゴリ別の許可/自動拒否） |
| 43-44 | effort 段階に **Max / Ultra** が新設（Codex UI 側） |
| 53 | `/compact` の存在（Claude Code 側） |
| 65 | **Codex hooks が正式機能化**（「2026年3月時点では一般向け安定機能として扱わない」は誤り） |
| 68 | プロファイルが**別ファイル方式**へ（`$CODEX_HOME/profile-name.config.toml`）。`CODEX_PROFILE` 環境変数も可 |
| **32** | **「危険な完全無保護」欄の Claude Code が「—」**。`--dangerously-skip-permissions`（`bypassPermissions`）が実在するのに「存在しない」と読め、**安全に関わる読者の誤解を生む** |
| 3, 79 | 「2026年4月時点」の日付を改訂時に更新 |
| 64 | カスタムコマンド: Claude Code は skills に統合済み、Codex は `.agents/skills/<name>/SKILL.md` |

---

## 付録A `appendix_a_learning_patterns.md`（6件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 77 | **METR 論文の著者名が捏造されている**。正しくは **Becker, J., Rush, N., Barnes, E. & Rein, D.** |
| CONFIRMED | 83 | **BioCoder の著者名が捏造されている**。正しくは **Tang, Qian, Gao, Chen, Chen & Gerstein**、巻号は **40(Supplement_1), i266–i276** |
| CONFIRMED | 3 vs 95 | **同一文書内で時点が矛盾**（3行目「2026年4月時点」vs 95行目「2026年3月時点」） |
| CONFIRMED | — | 参考文献[1]〜[9]が**すべて本文未引用** |
| CONFIRMED | 17 | **METR の「19%遅くなる」が続報で覆されつつある**。2026-02-24 の続報で復帰参加者は**点推定18%のスピードアップ**（CI −38%〜+9%、統計的に有意でない）。参加者の30〜50%が「AI禁止」条件のタスク提出を回避する選択バイアスも判明し、METR 自身が "our data is only very weak evidence" と明記。**旧数値のみの引用は2026年時点では不正確で、続報の併記が必須** |
| — | 25 | Thorgeirsson 研究の参照箇所（hajimeni:26 の訂正と連動させること） |

---

## 用語集 `glossary.md`（6件）

| 確信度 | 行 | 内容 |
|---|---|---|
| CONFIRMED | 173 | GIL の項で「Python 3.13以降では**実験的に**GILを無効化する free-threaded build が導入されている」→ **PEP 779 の受理により Python 3.14 で公式サポート（Phase II）** に移行済み。本リポジトリ自体が 3.14.6 |
| CONFIRMED | 287 | 色覚多様性「世界全体で8%」→ **男性限定の数値**（女性は0.5%） |
| — | 473 | TOML の項（内容は正しい） |
| — | — | モデル名を含む8箇所が世代遅れ |

---

## README・章間整合性（4件）

| 確信度 | 内容 |
|---|---|
| CONFIRMED | **書名の表記ゆれ**。`README.md:1` = 『AIエージェントを使いこなす はじめてのバイオインフォマティクス開発作法』（新）／`CLAUDE.md:4`・`CHANGELOG.md:3`・`vivliostyle.config.js:2` = 『AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法』（旧）。表紙PDFビルドは新タイトルを使用。**サブタイトルも2種併存** |
| CONFIRMED | 付録D:152「**do定義**」は実在しない用語の可能性が高く、初心者向け用語集としてリスク |
| CONFIRMED | `notice.md` の §20-2-1 参照に誤記 |
| — | README 目次と全章見出しの機械的突合、全リンク・全アンカーの解決性、README の文字数統計は**いずれも問題なし** |

---

## 付録C `appendix_c_checklist.md` / 著者紹介 `author.md`

**指摘事項なし。** 著者紹介の「2025年、竹田国際貢献賞受賞」は実在を確認（令和7年度 東京科学大学 生命理工学院 竹田国際貢献賞、授賞式2025-10-30、「1細胞RNAシークエンス法の開発と細胞アトラス構築への国際貢献」）。理研 TRIP-AGIS オミクスAI研究チームの肩書きも裏付けられた。

---

## 付録: 機械的検証の実行方法

本レビューで使用した検証は以下で再現できる。

```bash
cd /Users/itoshi/Projects/writing/ai-biocode-kata

# 相互参照・構造規約
uv run python scripts/review/check_xref.py
uv run python scripts/review/check_structure.py

# テスト・リント
uv run pytest -q
uv run ruff check scripts/ tests/

# URL 生存確認（ネットワーク、数分かかる）
uv run python scripts/review/check_urls_all.py
```

引用番号の整合性チェック（本文の `[N](url)` と章末リストの突き合わせ、コードフェンス対応の検証を含む）は本レビューのために作成したもので、リポジトリには含まれていない。恒久的に使うなら `scripts/review/` へ追加することを推奨する。
