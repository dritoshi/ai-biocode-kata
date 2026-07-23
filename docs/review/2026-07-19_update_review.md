# 更新レビュー報告 — 2026年7月19日

本書 v0.4.0（2026-04-25）以降の差分調査と、全章の事実確認レビューの結果である。

- **調査基準日**: 2026年7月19日
- **本書の想定時点**: 2026年4月（`notice.md`、付録A、付録B、§20-2-1 に明記）
- **調査方法**: 14本の並列エージェントによる章別レビューと領域別調査、および機械的検証スクリプトの実行
- **確信度**: CONFIRMED（一次情報で裏取り済み）／ LIKELY（強い根拠あり）／ UNCERTAIN（要確認）

> **本書の記述は一切変更していない。** 本ファイルは指摘の記録のみである。

> 📄 **本ファイルは重要度順に再構成した統合サマリである。修正作業を行う際は、章別に全指摘を記録した [2026-07-19_findings_by_chapter.md](./2026-07-19_findings_by_chapter.md) を参照すること**（行番号・具体的な修正案・実測値・「正しいと確認できた箇所」を含む）。

---

## エグゼクティブサマリ

### 最優先で対応すべき10件

読者への実害の大きさで並べた。

| # | 箇所 | 問題 | 確信度 |
|---|---|---|---|
| 1 | `20_security_ethics.md:356` | **Claude Consumer の「学習非利用が既定」は事実と逆**（実際は opt-out 方式で既定は学習利用、最大5年保持）。**何を送ってよいか判断させる表**なので実害が最大 | CONFIRMED |
| 2 | `06_dev_environment.md:334,341-350` | **conda のチャネル順が逆**（`-c bioconda -c conda-forge`）。Bioconda 公式が必須とする順序に反し、**読者が実際に環境を壊す**。同章の `.condarc` 例とも矛盾 | CONFIRMED |
| 3 | `00_ai_agent.md:725-727` | 引用[17]が主張していない統計値を帰属させている。**節全体の論拠が崩れる** | CONFIRMED（二重検証） |
| 4 | 全 `.bib` | **6ファイルで参考文献の著者名が誤り**。実在の研究者に、書いていない論文を帰属させている。全数照合が必要 | CONFIRMED |
| 5 | `12_data_processing.md:46-65` | 「高速化の実例」が比較対象より**13倍遅い**（実測）。章の中心命題が自身の例で反証される。ベンチ図も別コードを測定 | CONFIRMED |
| 6 | `04_data_formats.md:346-347,357` | **全角文字に対する Python の挙動が3箇所とも事実と逆**。ただしコラムの結論は正しく、根拠を実挙動に直せば主張はむしろ強くなる | CONFIRMED |
| 7 | `21_collaboration.md` | **付属スクリプト4本すべてが本文と不一致**。特に週次レポートは本文どおり操作すると必ず空出力 | CONFIRMED |
| 8 | `19_database_api.md:425-437,433` | SPARQL が `PREFIX rdfs:` 欠落で **HTTP 400**、GO URI 誤りで**静かに0件**。付属スクリプトには宣言があり本文だけ欠落 | CONFIRMED |
| 9 | `16_hpc.md:247` | `afterok` 失敗時の「自動キャンセル」は誤り。**共有クラスタにゾンビジョブを残す** | CONFIRMED |
| 10 | 付録B・§0-7 全体、`19_database_api.md:519` | モデルラインナップが2世代古い。**Ensembl 116 が現行サイトの最終リリース**で REST API 更新停止 | CONFIRMED |

### 全体像

- **AI発展との差分**: モデル世代交代（Fable 5 / Opus 4.8 / Sonnet 5、GPT-5.6 Sol/Terra/Luna）に加え、**ベンチマークの信頼性崩壊**という構造的変化があった。Codex CLI では `--full-auto` 非推奨化とフック正式機能化という破壊的変更が起きている。
- **記載の誤り**: 引用の誤り（誤帰属・著者違い・書誌情報の誤り）が最も多く、本書 README の「引用に誤りが残っている可能性があります」という但し書きは実態を正しく反映していた。
- **良好だった点**: 相互参照リンク480本すべて正常、テスト760件全通過、ruff 全通過、引用番号の欠番・重複ほぼ皆無。**構造面の品質は高い。**

---

## Part 1: AI発展との差分（2026年4月25日 → 7月19日）

### 1-1. モデルラインナップの世代交代

#### Anthropic（一次情報で確認）

| モデル | モデルID | context | 入力 $/MTok | 出力 $/MTok | 備考 |
|---|---|---|---|---|---|
| **Claude Fable 5** | `claude-fable-5` | 1M | **10.00** | **50.00** | 新設の Mythos クラス。Opus ティアの上位 |
| Claude Mythos 5 | `claude-mythos-5` | 1M | 10.00 | 50.00 | Project Glasswing 参加組織限定 |
| **Claude Opus 4.8** | `claude-opus-4-8` | 1M | 5.00 | 25.00 | 現行 Opus |
| Claude Opus 4.7 | `claude-opus-4-7` | 1M | 5.00 | 25.00 | **Legacy 扱いに移動** |
| **Claude Sonnet 5** | `claude-sonnet-5` | 1M | 3.00（導入 2.00、2026-08-31まで） | 15.00（導入 10.00） | 新トークナイザで 4.6 比 約30%多いトークン |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M | 3.00 | 15.00 | **Legacy 扱いに移動** |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 200K | 1.00 | 5.00 | 軽量ティアは据え置き |

#### OpenAI（一次情報で確認）

GPT-5.6 は `mini`/`nano` から**天体名 3バリアント**へ命名体系が変わった。2026-06-26 限定プレビュー（米政府審査済み約20社）→ **2026-07-09 GA**。

| ティア | モデル | API識別子 | 入力 | 出力 | context |
|---|---|---|---|---|---|
| フラッグシップ | **GPT-5.6 Sol** | `gpt-5.6-sol`（`gpt-5.6`） | $5.00 | $30.00 | 1,050,000 |
| バランス | **GPT-5.6 Terra** | `gpt-5.6-terra` | $2.50 | $15.00 | 1,050,000 |
| 軽量 | **GPT-5.6 Luna** | `gpt-5.6-luna` | $1.00 | $6.00 | 1,050,000 |

- GPT-5.6 Sol は **GPT-5.5 と同価格**。移行に価格上の不利がない
- GPT-5.5 / 5.4 系は**廃止告知なし**。API で引き続き利用可
- 最安は依然 `gpt-5.4-mini`（$0.75/$4.50）。「とにかく安く」の文脈では 5.4-mini への言及を残す判断もありうる
- **2026-07-23 に `gpt-5-codex` / `gpt-5.1-codex` 系が停止**（本報告の4日後）

#### thinking / effort 仕様（§0-7 の表は全面差し替えが必要）

| モデル | thinking 設定 | 省略時の挙動 | budget_tokens | temperature 等 | effort |
|---|---|---|---|---|---|
| Fable 5 | `adaptive` または省略。`disabled` は **400エラー** | adaptive で動作 | 400 | 400 | low〜max |
| Opus 4.8 / 4.7 | `adaptive` が唯一の on。`disabled` 可 | **thinking なしで動作** | 400 | 400 | low〜max |
| Sonnet 5 | `adaptive` が唯一の on。`disabled` 可 | adaptive で動作 | 400 | 400 | low〜max |
| Opus 4.6 / Sonnet 4.6 | `adaptive` 推奨 | 明示が必要 | 非推奨（動作はする） | 許容 | xhigh なし |
| Haiku 4.5 | `enabled` + budget_tokens | thinking なし | 必須 | 許容 | **effort 非対応** |

- `effort` は `output_config` 内に置く。既定は `high`
- `thinking.display` は Fable 5 / Opus 4.8 / 4.7 / Sonnet 5 で既定が `"omitted"`（4.6 系は `"summarized"`）
- **本書の記述で現行でも正しいもの**: 「Opus 4.7 以降は `temperature`/`top_p`/`top_k` を受け付けない」「新トークナイザで最大1.35倍」

#### ★ §20 のプライバシー議論に直結する新事実

**Claude Fable 5 は30日間のデータ保持が必須で、ゼロデータ保持（ZDR）では利用できない。** ZDR 設定の組織からのリクエストは全て `400 invalid_request_error` を返す。

本書は §20-2 と `notice.md` で ZDR を機密データ運用の選択肢として提示している。**「最高性能モデルと ZDR が両立しない場合がある」という新しいトレードオフ**が発生しており、未発表データ・制限付きデータを扱う読者にとって実務上重要な論点である。

---

### 1-2. ★ ベンチマークの読み方が主要論点になった（本書の構成に関わる変化）

本書 §0-7「ベンチマークで見るモデルの性能差」は SWE-bench 系のスコアを並べてモデルを比較する構成である。**この前提の揺らぎが2026年前半の主要論点になった。**

> ### ⚠️ 調査エージェント間で判定が割れた項目 — 著者による手動確認が必須
>
> 「**OpenAI が SWE-bench Verified の報告を公式に停止し、失敗問題の59.4%に欠陥があったと結論した**」という言説について、2本の独立した調査が**正反対の結論**を出した。
>
> - **調査A**: `https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/` を出典として、報告停止と 59.4% の欠陥率、SWE-bench Pro の撤回（タスクの約30%が破損）を報告
> - **調査B**: 「低信頼サイトのみが言及しており一次情報で確認できなかった。**書籍に採用すべきでない**」と結論
>
> `openai.com` は自動取得を HTTP 403 で拒否するため、**どちらも一次情報に到達できていない**。本報告では確定事実として扱わない。**ブラウザでの手動確認を強く推奨する。**

一方、**一次情報で確認できた**ベンチマーク関連の変化は以下である。

- **Scale AI の SWE-bench Pro 公式リーダーボードには Opus 4.7 / 4.8 / Fable 5 / GPT-5.5 のエントリが存在しない。** 巷で流通する 64.3% / 58.6% 等はすべてベンダー自己申告値であり、Scale 標準ハーネス値とは別物である
- **llm-stats は SWE-bench Verified について「verified 0件・self-reported 104件」と明記**している。ベンダー発表値（90%台）と公式実測値（70%台）の乖離が常態化した
- **Terminal-Bench 2.1 の公式注記によれば、2.0 のタスク修正だけで精度が最大12ポイント変動し、順位が最大3つ入れ替わった。** ベンチマークのタスク品質が順位を左右することが運営側から明示された
- **公式 SWE-bench は「同一システムプロンプト・bash-only」方式へ移行**し、ハーネスやプロンプト最適化の品質は測定対象外になった

**この3点だけでも、「スコアを並べて優劣を語る」構成の前提は十分に揺らいでいる。** 数値の更新ではなく、ベンチマークの読み方（自己申告か第三者測定か、条件は何か）を教える構成への転換を推奨する。

#### Terminal-Bench 2.1 公式リーダーボード（2026-07-11 更新）

2.0 は legacy 化。3.0 と terminal-bench-science 1.0 が coming soon。

| 順位 | エージェント × モデル | スコア |
|---|---|---|
| 1 | Claude Code + Fable 5 | 83.8% ± 1.2 |
| 2 | Codex + GPT-5.5 | 83.1% ± 1.1 |
| 3 | Terminus 2 + Fable 5 | 80.4% ± 1.2 |
| 5 | Claude Code + Opus 4.8 | 78.9% ± 1.3 |
| 10 | Claude Code + Sonnet 5 | 74.6% ± 1.6 |
| 12 | Claude Code + Opus 4.7 | 68.9% ± 1.4 |

同じ Fable 5 でもスキャフォールドの差で 3.4 ポイント動く（Claude Code 83.8% vs Terminus 2 80.4%）。**これは §0-7「エージェントの性能はモデルだけで決まらない」の主張を裏づける、出典の確かな代替データである**（後述する引用[17]の誤帰属の差し替え候補になる）。

#### 新ベンチマーク FrontierCode（Cognition、2026-06-08）

測定するのは「**メンテナが実際にこの PR をマージするか**」。20名超の OSS メンテナが1タスクあたり40時間以上かけて設計。

| モデル | Diamond | Main | Extended |
|---|---|---|---|
| Claude Opus 4.8 | **13.4%** | 34.3% | 51.8% |
| GPT-5.5 | 6.3% | — | — |
| Gemini 3.1 Pro | 4.7% | — | — |

**最高性能モデルでも最難関サブセットで約13%。** SWE-bench 系の 88〜95% とは全く違う景色を示す。「正解を出す」と「マージされるコードを書く」の落差は、**本書の中心テーマである「人間がレビュー・判断する」の必要性を数値で裏づける最良の題材**であり、§0-7 または §21 コードレビュー節への追加を強く推奨する。

---

### 1-3. Codex CLI の破壊的変更（付録B対照表に直結）

| 書籍の記述 | 判定 | 現状 |
|---|---|---|
| `--full-auto` | **廃止（非推奨）** | 公式に deprecated。使用時に警告が出る。`--sandbox workspace-write` へ |
| フック「2026年3月時点では一般向け安定機能として扱わない」 | **記述が古い** | **2026年4〜5月に GA。** 9種のライフサイクルイベントを持つ正式機能 |
| `$skill-name`（SKILL.mdベース） | **配置場所が変更** | 記法は維持。配置は `.agents/skills/<name>/SKILL.md`（ほかに `$HOME/.agents/skills`、`/etc/codex/skills`） |
| `--profile dev`（config.toml の `[profiles]`） | **方式が変更** | `$CODEX_HOME/profile-name.config.toml` を重ねる別ファイル方式。旧記法の後方互換は要検証 |
| `~/.codex/config.toml` | **多層化** | プロジェクト `.codex/config.toml`、システム `/etc/codex/config.toml` を含む優先順位付き構造 |
| 推論強度「None〜Extra High」 | **最下位が誤り** | 許容値は `minimal`/`low`/`medium`/`high`/`xhigh`。**"None" は存在しない**。UI は Low〜Ultra |
| `-s read-only` / `-a on-request` / `codex resume` / `codex exec` / `codex mcp add` | 現状維持 | 有効 |
| `--dangerously-bypass-approvals-and-sandbox` | 現状維持 | 有効。`--yolo` エイリアス追加 |

**提供形態の拡大**: 2026-07-09 に **ChatGPT デスクトップアプリへ統合**。Chrome 拡張、iOS/Android、Amazon Bedrock も追加。本書が「CLI + IDE拡張 + web」で記述している箇所は拡充が必要。

**Claude Code 側の変更**: カスタムコマンドが skills に統合された（`.claude/commands/*.md` は後方互換で動作するが、現行の推奨は `.claude/skills/<name>/SKILL.md`）。両ツールが `SKILL.md` に収斂したことは、対照表としてむしろ説明しやすくなっている。

---

### 1-4. AIコーディングツール市場・MCP・規制

#### ツール市場が2026年6月に激変した（§20-1 のツール表・§0 の記述に直結）

| ツール | 状況 | 本書への影響 |
|---|---|---|
| **Windsurf** | **製品名が消滅。2026-06-02 に「Devin Desktop」へ改名** | `00_ai_agent.md:10` の「Cursor、Windsurf等」が無効に |
| **Continue** | **Cursor に買収され事実上終了**（2026年6月中旬）。最終版 2.0.0、リポジトリは読み取り専用 | §20 のツール表に残すなら注記が必要 |
| **Cursor** | **SpaceX が株式交換 600億ドルで買収合意**（2026-06-16） | — |
| **Aider** | **実質メンテナンスモード**（最終タグ 2025-08-09、期間内の新リリースなし） | §20 のツール表に注記が必要 |
| **GitHub Copilot** | デスクトップアプリ「Copilot app」発表（2026-06-02）、従量課金全面化 | — |

**業界的な収斂（本書の主張を補強する材料）**: 並列エージェント + git worktree 分離が標準装備化し、「エージェント群の監視画面を第一画面にする管制塔UI」を GitHub・Cognition・Google が同時期に採用。「エージェントが書き、別のエージェントが検証し、人間は最終ゲートに立つ」体制が製品として実装された。

#### MCP の進化（§5-5 に直結）

- **ガバナンスが移管された**: 2025-12-09、Anthropic が MCP を **Linux Foundation 傘下の Agentic AI Foundation（AAIF）へ寄贈**（Anthropic / Block / OpenAI の共同創設、Apache 2.0）。**MCP を「特定ベンダーの仕組み」ではなく業界標準として説明できる段階になった**
- **2026-07-28（本報告の9日後）に史上最大の改訂が確定予定**（RC は 2026-05-21 公開）: ステートレス・コア化（`initialize` ハンドシェイクと `Mcp-Session-Id` の廃止）、**Roots / Sampling / Logging の非推奨化**（12か月猶予）、MCP Apps と Tasks の公式拡張新設
- **AGENTS.md も AAIF へ寄贈済み**（6万超の OSS が採用）。**Agent Skills（SKILL.md）は agentskills.io としてオープン標準化**され40以上の製品が対応
- **セキュリティ**: CSA の調査（2026-05-04）で約20万の脆弱インスタンス、認証なし公開サーバ1,862件。**tool poisoning / rug pull / cross-server tool shadowing** が脅威分類として確立。特に arXiv:2607.05744（2026-07-07）は**不可視 Unicode でツールメタデータにペイロードを隠し、人間の承認画面には見えず LLM にだけ届く**攻撃を実証しており、**本書が繰り返す「人間が承認する」という前提そのものへの反例**として扱う価値が高い

#### 規制の重要な進展（§20 に直結）

- **EU AI Act の Digital Omnibus が成立した**（欧州議会 2026-06-16、理事会 2026-06-29、署名 2026-07-08）。**高リスク義務が延期された**:
  - 2026-08-02: 第50条 透明性義務（チャットボットの機械開示、合成コンテンツ表示）— 維持
  - 2027-12-02: 附属書III 単独型 高リスクAI（約16か月延期）
  - **2028-08-02: 附属書I 製品組込型 高リスクAI（医療機器・IVD 含む）— 1年延期**
  - **第2条6項「専ら科学的な研究開発の目的」の AI は適用除外** — 研究者読者に最も重要
  - 本書 `20_security_ethics.md:309-313` の法規制表に **EU AI Act の項目が完全に欠落**している
- **個人情報保護法 令和8年改正**（**2026-07-10 成立・2026-07-17 公布**、施行は公布から2年以内の政令指定日で政令未制定）:
  - **統計情報等の作成に係る同意不要の特例を新設**し、「統計作成等であると整理できる AI 開発等」を含むと明記。**公開されている要配慮個人情報の取得**も対象
  - **学術研究例外の主体に病院・診療所等を含むことを明示**（従来は大学附属病院のみ）
  - 課徴金制度の導入など規制強化も同時に行われた
  - 書くなら「**成立済み・未施行**」を明示すること
- **AI事業者ガイドライン 第1.2版**（2026-03-31）が現行最新。**「AIエージェント・フィジカルAI」の定義・便益・リスクが追記された** — 本書のコンセプトを公的文書で裏付けられる
- **NIH NOT-OD-25-081**: 制限付きデータを第三者生成AIに入力することを明示的に禁止。さらに**生成AIモデル本体・パラメータが "Data Derivatives" として元データと同じ制約を受ける**。ローカルLLMでファインチューニングする読者に直接効く論点で、本書に記述がない

#### 品質・生産性研究の続報

- **★ METR の「19%遅くなる」は続報で覆されつつある**（2026-02-24）。復帰参加者は**点推定で18%のスピードアップ**（ただし統計的に有意でなく、METR 自身が "our data is only very weak evidence" と明記）。参加者の30〜50%が「AI禁止」条件のタスク提出を回避する選択バイアスも判明。**`appendix_a_learning_patterns.md:17` の旧数値のみの引用は2026年時点では不正確であり、続報の併記が必須**
- **「Habituation at the Gate」**（arXiv:2606.22721、2026-06-21、プレプリント）: 400名のレビュアー追跡で、AI生成PRへの**承認率が 30.1% → 36.8% に上昇する一方、レビューコメントは22%減少**。**「AIレビューの形骸化」を定量化**した研究で、本書のレビュー章と最も親和性が高い
- DORA 2026 は **J-Curve モデル**（導入直後は検証オーバーヘッドで一時的に生産性低下 → 基盤整備後に回復）を提示。単純タスクで35〜40%向上だが**複雑なレガシーコードでは約10%**

#### ★ 書籍に採用してはならない誤情報（調査中に確認）

- **「Llama 5 が 2026-04-08 に 600B / 5M context でリリース」** — Meta 公式と矛盾する誤情報（AI生成コンテンツファーム由来と推定）。同日に実際に発表されたのは Muse Spark である

### 1-5. AI for Science / バイオインフォマティクス分野

#### ★ AlphaFold 3 のライセンスが変更された（更新期間のど真ん中）

git コミット履歴で確認: **2026-06-09 に「Change the code license from CC BY-NC-SA 4.0 to Apache 2.0」**（v3.0.3）。

| 対象 | ライセンス | 商用利用 |
|---|---|---|
| ソースコード | **Apache 2.0**（2026-06-09 変更） | **可** |
| モデル重み | AlphaFold 3 Model Parameters Terms of Use | **不可**（再配布禁止、競合モデル学習禁止、Google への個別申請が必要） |

「AlphaFold 3 はコードも重みも非商用」という記述があれば**誤りになった**。なおこのライセンス階層の違いは §20（倫理）の good example にもなる。

#### 公共DB・インフラの重要な変更

| 対象 | 変更内容 | 本書への影響 |
|---|---|---|
| **Ensembl** | **116 が現行サイトの最終リリース**。REST API・公開MySQL・FTP は更新停止。2026年夏に beta.ensembl.org へリダイレクト、ミラー廃止。後継は GraphQL(Thoas) / refget | §19-3 の「最初に覚えたいAPI」という推奨が読者を袋小路へ導く |
| **PDB** | **2027-07-21 以降の新規エントリでレガシー PDB 形式を生成しない**（mmCIF / PDBML のみ）。4文字IDは2028年前に枯渇、拡張ID へ移行。wwPDB は2026年末までの完全移行を推奨 | §19-4 / §4 に追記が必要 |
| **NCBI E-utilities** | **レート制限は変更なし**（APIキーなし3 req/sec、あり10 req/sec）。**本書 §19-3 の記述はそのまま有効** | 修正不要（NCBI Datasets は5/10 req/sec で別物） |
| **PMC** | FTP 廃止 → AWS へ移行。レガシーファイルは**2026年8月に完全削除** | §19-4 に影響 |
| **UniProt** | 2026_02（2026-06-10）。総エントリ 149,810,139 | 数値記載があれば更新 |
| **DDBJ** | 利用規約改訂（2026-06-30、名古屋議定書関連 ABS）。INSDC Minimal Specifications | §19 / §20 に追記候補 |
| **ArrayExpress** | `https://www.ebi.ac.uk/arrayexpress/` は **302 で `/biostudies/arrayexpress` へ転送**（個別実験ページも同様）。移行は実証済み | `19_database_api.md:872` |
| **TogoWS** | **応答が10〜48秒**（`entry/uniprot/P04637` の実測が47.8秒）。25〜30秒のタイムアウトでは全リクエストが失敗する。`entry/pdb/1a3n` は404、`entry/uniprot/P04637.json` は500。サービス終了の告知はなし | `19_database_api.md:525` が「手軽に試せる」と紹介しているが、そのまま試すと高確率でタイムアウトする。長めのタイムアウト設定の注記が必要 |
| **Ensembl REST のレート制限** | 実測ヘッダは `x-ratelimit-limit: 55000` / `x-ratelimit-period: 3600` = **55,000リクエスト/時（IP単位）**。超過時は `Retry-After` | 誤りではなく**欠落**。NCBI についてはレート制限を強調している章なので、Ensembl だけ触れないのは記述の非対称 |
| **NCBI Aspera FTP** | 本文が示すパスは **404** | `19_database_api.md:624` |
| **PDB ID の失効** | wwPDB 公式の逐語: 「**By 2028** 4-character PDB IDs will be fully allocated」「Starting **July 21, 2027**... New 4-character PDB IDs will not be issued」。拡張IDは接頭辞込みで**12文字**（`pdb_` + 英数字8文字）。PDBe API は拡張IDを既に受理、RCSB Data API は未対応 | 本文に PDB ID のバリデータやパーサで `^[0-9][A-Za-z0-9]{3}$` 相当の4文字前提の正規表現があれば要見直し |

#### 米国の研究予算削減 — 実害の所在を正確に区別すべき

FY2026 は政権が NIH の約40%削減を提示したが**議会が否決**し、487億ドル（前年比 +約1%）で成立。**NLM を他研究所へ統合する再編案も否決**された。

実際にサービス縮退が起きたのは**モデル生物DB**である:

- **FlyBase**: 2025年5月に NIH がハーバード大への全グラントを打ち切り、2025年8〜10月に職員8名全員を解雇。Wellcome Trust の緊急資金で1〜2年分を確保、寄付募集中
- **WormBase**: **WS298 を最後のメジャーリリース**とし、Alliance of Genome Resources へ統合。以後アーカイブ保守モード
- **SGD** も財政逼迫を表明

> ⚠️ **GenBank / SRA / PubMed 本体が停止・縮退した事実は確認されていない。** GenBank は 265.0〜272.0 と定期リリースを継続している。本書でこの区別を曖昧にしてはならない。

#### 主要ツールのバージョン（本書の記述と要照合）

| ツール | 最新版 | 本書への影響 |
|---|---|---|
| **Biopython 1.87** | 2026-03-30 | **1.86 で `Bio.Application` / `Bio.Blast.Applications` を全削除。**（※本書は未使用なので影響なし — 確認済み）。**CVE-2025-68463 修正のため 1.87 以上を明記すべき** |
| **Apptainer 1.5.2** | 2026-06-23 | 本書の「Apptainer 1.3」（`15_container.md:648`）は2世代古い。`SINGULARITY_` プレフィックスは公式に DEPRECATED |
| **pandas 3.0.x** | 3.0.0 は 2026-01-21 | 本書の `pandas 1.5.3 / 2.2.0`（`06_dev_environment.md:459`）は要見直し |
| **NumPy 2.5.x** | 2026-07-04 | **NEP 50 の型昇格変更**が §3-2（浮動小数点）と §12 に直結。`np.float32(3) + 3.` が float32 を返す |
| **AnnData 0.13.x** | 2026-07-13 | `.X` の copy-on-write 化、`concatenate()` 削除。（※本書は概念説明のみで該当コードなし — 確認済み） |
| **scanpy 1.12.2** | 2026-06-29 | 本書の `scanpy 1.9 / 1.10`（`06_dev_environment.md:20`）は古い。`louvain()` 非推奨 → `leiden()` |
| **Snakemake 9.23.1 / Nextflow 26.04.6 / CWL v1.2.1** | — | **DSL3 は存在しない**（strict syntax は DSL2 の厳密実装）。Nextflow 26.04 から strict parser がデフォルト |
| **pysam 0.24.0** | 2026-04-27 | **CRAM 参照データの EBI 自動取得が廃止 → `REF_CACHE`/`REF_PATH` 必須** |
| **samtools 1.24** | 2026-07-09 | **`view --subsample` のデフォルトシード挙動が変更**（再現性の記述に影響） |
| **Bioconda** | — | **2024年8月に `defaults` チャネルが推奨セットから削除済み。** 4行構成を載せていれば古い |

#### バイオ系 MCP の現状

| サーバー | 本書の記述 | 現状 |
|---|---|---|
| **BioMCP** | 「12種のバイオメディカルエンティティ」 | **約30の情報源**（v0.8.25, 2026-07-08, MIT） |
| **TogoMCP** | 「20以上のDB」 | **30以上**。かつ **bioRxiv 論文が公開され引用可能に** |
| **PubMed MCP** | JackKuo666 版（参照日 2026-03-23） | 2026年時点のメンテ状況は未確認 |

**新規の枠組み**: MCPmed（Brief Bioinform 2026-01、GEO/STRING/UCSC Cell Browser で実装）、BioContextAI（Nature Biotechnology 2025、生物医学 MCP のレジストリ）。EMBL-EBI は MCP 対応を**検討中**で、公式サーバはまだ存在しない。

**Biomni は Science 誌に2026-07-09 掲載**（DOI: 10.1126/science.adz4351）。本書のプレプリント引用は査読付き論文へ差し替え可能。

#### データポリシーの変更

- **NIH**: NOT-OD-26-046（2026-02-25）で **DMP の必須要素が全面改定**。**2026年5月25日以降の申請に新様式が必須**。ナラティブ6要素から Yes/No + 表形式へ。ただし **DMS Policy 本体は不変**（「方針は同じ、書き方が変わった」が正確）
- **科研費**: DMP **提出は不要**（策定は必要）。ただしメタデータ報告が事実上の義務で、KAKEN および CiNii Research に公開される
- **AMED**: **令和8(2026)年4月以降に締結する全課題で DMP 提出が義務**。ガイドライン2.2版 + 様式202512
- **PLOS Biology: 2026年1月1日投稿分からコード公開を義務化**（DOI発行の永続リポジトリへの寄託を強く推奨）。PLOS Medicine は2027年義務化。Nature Portfolio は中核コードが**査読対象**
- **Nature の生成AI開示**: LLM 使用は Methods に記載。コピーエディット目的は申告不要。生成AI画像は原則掲載不可。**査読者は原稿を生成AIにアップロード禁止**

---

## Part 2: 記載の誤り

### 2-0. 機械的検証の結果（自前実行・全件確認済み）

| 検証項目 | 結果 |
|---|---|
| 相互参照リンク（章間480本・画像40本） | **問題 0 件** |
| pytest | **760 passed / 2 skipped** |
| ruff check | **All checks passed** |
| コードフェンスの閉じ忘れ | **0 件** |
| 引用番号の欠番・重複・本文↔リスト対応 | CRITICAL 0 / **MAJOR 4（§13）** |
| URL 生存確認（410件） | ok 397 / error 4 / anti-bot 8 / timeout 1 |
| 構造規約（太字内カッコ） | MINOR 21 件 |

**構造面の品質は高い。** 問題は内容、とりわけ引用に集中している。

---

### 2-1. 引用の誤り（最重要カテゴリ）

#### [CONFIRMED・二重検証] `00_ai_agent.md:725-727` — 引用[17]が主張していない統計値を帰属させている

- **現状**: 「同一のモデルでも、エージェントの実装が異なると、SWE-benchのスコアが42%から78%まで変動する——36ポイントもの差が生じる。一方、フロンティアモデル6種を同一のエージェントで比較した場合、スコアの差はわずか1.3ポイント以内に収まる[17]」
- **問題**: 引用先 arXiv:2604.03515 は実在するが、タイトルは "Inside the Scaffold: A Source-Code Taxonomy of Coding Agent Architectures"（Benjamin Rombaut）で、**13個のオープンソース・スキャフォールドのソースコード分類学的調査**である。要約は "This paper presents a source-code-level architectural taxonomy derived from analysis of 13 open-source coding agent scaffolds at pinned commit hashes." であり、**性能ベンチマークを一切実施していない**。42%/78%/1.3ポイントという数値は論文中に存在しない。
- **影響**: 節タイトル「エージェントの性能はモデルだけで決まらない」の論拠が丸ごと崩れる。
- **修正案**: (a) 数値を削除し、[17] は「スキャフォールドの設計が多様であること」の論拠としてのみ使う。(b) 主張を残すなら **Terminal-Bench 2.1 公式リーダーボードの実データ**（同じ Fable 5 でも Claude Code 83.8% vs Terminus 2 80.4% と 3.4 ポイント差）に差し替える。こちらは出典が明確で、主張の方向も同じである。

#### [CONFIRMED] `references/ch00.bib:30` — SWE-agent の arXiv ID が無関係の論文を指す

- **現状**: `@article{yang2024sweagent, ... url = {https://arxiv.org/abs/2401.05566}}`
- **問題**: arXiv:2401.05566 は Hubinger et al. "Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training" であり、SWE-agent とは全く無関係。正しくは **arXiv:2405.15793**（本文側リスト `00_ai_agent.md:976` は正しい）。
- **修正案**: `ch00.bib` の URL を `https://arxiv.org/abs/2405.15793` に修正。

#### [CONFIRMED] 参考文献の著者名の誤り（3件）

| 箇所 | 現状 | 正しい著者 |
|---|---|---|
| `00_ai_agent.md:988`（[16] Terminal-Bench） | Wijk, D., Phan, L., Berglund, L., et al. | **Merrill, M. A., Shaw, A. G., Carlini, N., et al.**（計85名）。また arXiv 上に "ICLR 2026" の会議情報はない |
| `00_ai_agent.md:996`（[24]） | Huang, Y., et al. | **Xi, Y., Lin, J., Xiao, Y., et al.**（第一著者 Yunjia Xi） |
| `00_ai_agent.md:997`（[25]） | Xu, R., et al. | **Zhang, W., Li, X., Zhang, Y., et al.**（第一著者 Wenlin Zhang） |

いずれも `references/ch00.bib` 側も同様に要修正。実在論文に別人の名前が付いており、読者が原典に到達できない。

#### [CONFIRMED] `13_visualization.md:11` — 引用番号とURLが入れ替わっている

- **現状**: 本文 `Matplotlib[1](doi/10.1109/MCSE.2007.55)[2](matplotlib.org)、Seaborn[3](doi/10.21105/joss.03021)[4](seaborn.pydata.org)`
- **問題**: 文献リストは [1]=Matplotlib Documentation、[2]=Hunter論文、[3]=seaborn Documentation、[4]=Waskom論文。**本文と [1]↔[2]、[3]↔[4] が逆**になっている。
- **修正案**: 本文を `Matplotlib[2][1]、Seaborn[4][3]` にするか、文献リストの1↔2・3↔4を入れ替える。

#### [CONFIRMED] `00_ai_agent.md:991` — BioCoder の書誌情報が誤り

- **現状**: *Bioinformatics*, 40(4), 2024.
- **正しくは**: ***Bioinformatics*, 40(Supplement_1), i266–i276, 2024**（ISMB 2024 特集号）。「40(4)」は存在しない号。

#### [CONFIRMED] `00_ai_agent.md:736` — Ouyang et al. の 75.76% は3データセット中の最悪値

- **現状**: 「同じコード生成タスクを5回実行した場合、75.76%のタスクでテスト結果が毎回異なった[18]」
- **問題**: 原典は "75.76%, 51.00%, and 47.56% for CodeContests, APPS, and HumanEval" と記載。75.76% は競技プログラミング系 CodeContests のみの値で、HumanEval では 47.56%。単一の代表値として提示すると非決定性を約1.5倍過大に見せる。「5回実行」という試行回数も原典で確認できない。
- **修正案**: 「データセットにより47.6%〜75.8%のタスクで、リクエストごとにテスト結果が一致しなかった（CodeContests 75.76%、APPS 51.00%、HumanEval 47.56%）」と範囲で記述する。

#### [CONFIRMED] `10_deliverables.md:604` — 12factor の引用が主張と逆

- **現状**: 「パラメータは設定ファイル（YAMLまたはTOML）で外部化する[6](https://12factor.net/)」
- **問題**: The Twelve-Factor App の Config は設定を**環境変数**に置くことを推奨し、設定ファイル方式は "it's easy to mistakenly check in a config file to the repo" と**弱点として明示的に挙げている**。設定ファイル推奨の典拠に引くのは誤引用。なお `10_deliverables.md:669`（秘密情報を環境変数で管理）で [6] を引くのは正しい。

#### [CONFIRMED] `01_design.md:154` — 引用[6]のリンク先が文献リストと一致しない

- 本文の `[6]` は Wikipedia にリンクしているが、文献リストの [6] は Martin *Clean Code*（URLなし）。番号とリンク先が別物。加えて SRP の一次文献は *Agile Software Development, Principles, Patterns, and Practices*(2003) であり *Clean Code*(2008) は解説書。

#### [CONFIRMED] `02_terminal.md:805-806` — 「参考文献[1]/[2]で引用」という記述が事実に反する

- §2 は本文中の引用マーカーが `[9]`(L521) と `[10]`(L531) の2つだけで、**[1]〜[8] は本文に一度も出現しない**。にもかかわらず L805-806 に「本章の参考文献 [1] で引用」「[2] で引用」と書かれている。[8] seqtk に至っては章内に "seqtk" の語自体が出てこない。

#### [CONFIRMED] `10_deliverables.md` — 引用 [8][9][10] が `references/ch10.bib` に存在しない

GitHub Pages[8]、Streamlit Community Cloud[9]、Hugging Face Spaces[10] を本文で引用し文献リストにも載せているが、`ch10.bib` は8エントリのみでこの3件がない。CLAUDE.md の「BibTeX で一元管理」に反し、PDF/EPUB ビルド時に文献が欠落する。

#### [CONFIRMED] `21_collaboration.md` — 書誌情報の誤り3件

| 対象 | 現状 | 正しい情報 |
|---|---|---|
| Producing Open Source Software | O'Reilly、2017年 | **O'Reilly は第1版のみ。第2版はクラウドファンディングによる自主出版、2020年**（サイトに "2020-08-14: The 2nd Edition rewrite is finished"、CC BY-SA 4.0） |
| Biostars（サイト名） | "Pair of Scissors" | **"Bioinformatics Answers"**（BibTeX 側は正しい。文献リストのみ誤り） |
| Stan Lee の引用 | "with great power comes great responsibility" | 原文は **"with great power there must also come -- great responsibility!"**。しかも**ナレーションであり Uncle Ben の台詞ではない**（Ben への帰属は後年の retcon） |

#### ★ [CONFIRMED] 複数の .bib で著者名が捏造されている — 系統的な問題

**同一パターンの誤りが章をまたいで発見された**: 実在する筆頭著者・最終著者の間に、その論文の著者ではない研究者名が挿入されている。

| 箇所 | 現状の著者 | 正しい著者 |
|---|---|---|
| `00_ai_agent.md:988`（[16] Terminal-Bench） | Wijk, D., Phan, L., Berglund, L., et al. | **Merrill, M. A., Shaw, A. G., Carlini, N., et al.**（計85名）。arXiv 上に "ICLR 2026" の会議情報もない |
| `00_ai_agent.md:996`（[24]） | Huang, Y., et al. | **Xi, Y., Lin, J., Xiao, Y., et al.** |
| `00_ai_agent.md:997`（[25]） | Xu, R., et al. | **Zhang, W., Li, X., Zhang, Y., et al.** |
| `appendix_a_learning_patterns.md:77`（METR論文） | — | **Becker, J., Rush, N., Barnes, E. & Rein, D.** |
| `appendix_a_learning_patterns.md:83`（BioCoder） | — | **Tang, Qian, Gao, Chen, Chen & Gerstein**、40(Supplement_1), i266–i276 |
| `references/ch13.bib:87`（deepTools2） | … Bhatt, Vivek / Lucks, Friederike / **Arenber, Konstantin A.** / **Raffan, Frank** … | **Bhardwaj V, Kilpert F, Richter AS, Heyne S, Dündar F**。Arenber と Raffan は著者ではなく、Kilpert・Richter・Heyne が欠落 |
| `references/ch13.bib:99`（pyGenomeTracks） | … Bhatt, Vivek … | **Bhardwaj V, Backofen R**。Backofen が欠落 |
| `references/ch15.bib:24`（BioContainers） | … **Peltzer, Alexander** / **Ternent, Tobias** … | **Alves Aflitos, Saulo / Röst, Hannes L / Pfeuffer, Julianus**。Peltzer と Ternent はこの論文の著者ではない |
| `references/ch02.bib:75` / `02_terminal.md:839`（fd） | Peterka, David | **Peter, David**（GitHub `sharkdp` の本名） |
| `references/ch07.bib:118`（Keep a Changelog） | Langlois, Olivier | **Lacan, Olivier** |

> **推奨**: **全22章の `.bib` について著者名の全数照合を行うこと。** 現時点で `ch00.bib` / `ch02.bib` / `ch07.bib` / `ch13.bib` / `ch15.bib` / `appendix_a.bib` の**6ファイル**で確認されており、未調査の章にも同様の誤りがある可能性が高い。読者が原典に到達できないだけでなく、**実在の研究者に、書いていない論文を帰属させている**点で書籍として看過できない。

#### [CONFIRMED] 書誌情報（年・巻号）の誤り

| 箇所 | 現状 | 正しい情報 |
|---|---|---|
| `references/ch07.bib:150` / `07_git.md:609`（Blischak） | *PLOS Comput Biol*, **11(1)**, e1004668, **2015** | ***PLOS Comput Biol*, 12(1), e1004668, 2016**（年・巻とも誤り） |
| `00_ai_agent.md:991`（BioCoder） | *Bioinformatics*, **40(4)**, 2024 | ***Bioinformatics*, 40(Supplement_1), i266–i276, 2024**（40(4) は存在しない号） |
| `references/ch09.bib:53` / `09_debug.md:806`（UCSC） | "FAQ: Coordinate Transforms" | 実タイトルは **"Frequently Asked Questions: Data File Formats"**。さらに本文の「座標系の混乱は最大のバグ源」という主張をこのページは述べていない |
| `hajimeni.md:107`（Dr. Bono） | 2017年初版 | **第2版が2021年3月に刊行**（MEDSI, ISBN 978-4-8157-3011-6） |
| `hajimeni.md:106`（デジタルツール入門） | 坊農秀雅（単著扱い） | **坊農秀雅・小野浩雅 監修**（共同監修） |
| `13_visualization.md:5` vs 参考文献[7] | エピグラフは1983年初版、文献リストは2001年第2版 | 同一章内で版が混在。統一が必要 |
| `19_database_api.md:1039`（Biomni） | 第一著者が誤り | **Kexin Huang**。かつ 2026-07-09 に *Science* 掲載済み（DOI: 10.1126/science.adz4351）でプレプリント引用は差し替え可能 |
| `12_data_processing.md:3`（エピグラフ） | "Tidy datasets are all alike, but every messy dataset…" | 原文は **"Like families, tidy datasets are all alike but every messy dataset is messy in its own way."** 冒頭の "Like families," が脱落し、原文にないカンマが入っている |
| `13_visualization.md:320` | dynamite plot 回避の主張を Rougier et al. 2014[8] に帰属 | 同論文の10ルールに棒グラフ・平均値表示の項目は**ない**。正しい出典は **Weissgerber et al., *PLOS Biology*, 13(4), e1002128, 2015**（DOI: 10.1371/journal.pbio.1002128） |
| `18_documentation.md:354` | §11-3 への参照 | **§11-1 が正しい** |

#### [CONFIRMED] DOI が全く別の文書を指している（2件）

| 箇所 | 現状 | 実際の解決先 |
|---|---|---|
| `references/ch00.bib:30`（SWE-agent） | arXiv:2401.05566 | Hubinger et al. "Sleeper Agents"。正しくは **arXiv:2405.15793** |
| `15_container.md:1105`（[12] MLflow） | `10.1109/DSAA.2018.00006` | **"Message from the DSAA 2018 Program Co-Chairs"**（巻頭挨拶）。MLflow 論文には DOI が存在しないため、公式PDF `http://sites.computer.org/debull/A18dec/p39.pdf` へ差し替える |

#### [CONFIRMED] `15_container.md:351` — bioconda「1万以上のツール」を2018年論文に帰属

引用先の Grüning et al. 2018 は "The Bioconda project provides **over 3,000** Conda software packages" と述べており、1万という数字の根拠にならない。数値自体は2026年時点なら妥当だが、引用が主張を支持していない。

#### [CONFIRMED] 未引用の参考文献（本文に番号引用が1つも無い章）

§2（10件全部）、**§16（8件全部 — 本文中の引用マーカーがゼロ）**、付録A（9件全部）、付録B（2件全部）、**§15（17中12件）**、§12（9中5）、§4（4件）、§9（3件）、§7（2件）、§1（2件）、§18（2件）、§0/§5/§11/§17/§19（各1件）。

CLAUDE.md の「その章で引用した文献を番号順にリストする」規約と不整合。**§0 の [4]（SWE-agent）と §17 の [7]（Apache Parquet）は完全な欠番**。§15 では [11] wandb / [12] MLflow / [13] hydra / [14] DVC が §15-6 で節を割いて解説されているのに引用番号が付いていない。

---

### 2-2. 技術的な事実誤り

#### [CONFIRMED] `03_cs_basics.md:389` — NaN の「あらゆる比較演算が False」は誤り

- **問題**: `!=` は `True` を返す。しかも **4行上の L385 で本書自身が `print(nan != nan)  # → True` と正しく示しており、章内で直接矛盾**している。「あらゆる比較が False」と覚えた読者は `if x != x:` によるNaN検出（実際に有効なイディオム）を誤りと判断してしまう。
- **修正案**: 「等値・大小比較（`==`, `<`, `>`, `<=`, `>=`）がすべて `False` を返す（`!=` だけは `True`）」

#### [CONFIRMED] `02_terminal.md:493` および L428-440 — 「grep/sed のパターンをそのまま Python に持ち込める」は誤り

実行検証の結果:
- BRE では `+` と `?` は**リテラル**（`grep 'AT+G'` は `ATG` にマッチせず、文字列 `AT+G` にマッチする）
- `\d` は **BSD sed で機能しない**（`sed -E 's/chr\d+/X/'` は `chr1` を変換できない。`[0-9]+` なら可）
- メタ文字表は PCRE/Python 方言で書かれているが、`grep`・`sed` の既定は POSIX BRE

**修正案**: 表に方言の列/注記を追加し、「`+` `?` `\d` `\s` `\w` には `grep -E` か `grep -P` が必要、`sed` は `-E` でも `\d` を解釈しない。POSIX ツールでは `[0-9]` が安全」と明示する。

#### [CONFIRMED] `02_terminal.md:458-463, 499` — GFF3 と GTF の取り違え（2箇所）

- **現状**: 「GFF3のattributeからgene_idを抽出する例」に続いて `gene_id "ENSG00000012048"; transcript_id "..."`
- **問題**: GFF3 の第9列は `tag=value` をセミコロン区切りで並べる形式（`ID=gene00001;Name=EDEN`）で、仕様書は「属性値は引用符で囲む必要はなく、囲むべきでもない」と明記。`gene_id "..."` という引用符付き記法は **GTF（GFF2系）** のもの。バイオインフォ書籍として実害が大きい。
- **修正案**: 見出し・コメント・L499の指示例を「GTF」に変更（正規表現 `r'gene_id "([^"]+)"'` は GTF に対して正しいのでそのまま使える）。

#### [CONFIRMED] `11_cli.md:709-717` — `RichHandler` が stdout に出力し、本章の鉄則を本章のコードが破っている

- **現状**: `# stderrハンドラ（richが利用可能ならRichHandler）` の直下で `stderr_handler = RichHandler(show_time=True, show_path=False)`
- **問題**: `RichHandler` は `console` 未指定だとグローバル Console（= **stdout**）を使う。実測で `handler.console.file is sys.stdout` が `True`。本章が繰り返し掲げる「結果はstdout、それ以外はstderr」（L779）に真っ向から反し、パイプの結果データにログが混入する。**実体 `scripts/ch11/logging_setup.py:47-53` は `console=Console(stderr=True)` を正しく渡しており、本文への縮約時に決定的な引数だけ落ちている。**
- **修正案**: `RichHandler(console=Console(stderr=True), ...)` と `from rich.console import Console` を追加。

#### [CONFIRMED] `11_cli.md:323-327` — samtools のパイプ例が成果物ゼロ

- **現状**: `samtools view -b input.sam | samtools sort | samtools index -`
- **問題**: 実測（samtools 1.23.1）で生成されるのは **`-.bai` という名前のファイル1つだけで、BAM 本体はどこにも保存されない**（sort の出力は index の stdin に流れて消える）。「優れた設計の実例」として提示されているため誤解が大きい。
- **修正案**: `samtools view -b input.sam | samtools sort -o sorted.bam && samtools index sorted.bam`

#### [CONFIRMED] `00_ai_agent.md:522, 526` / 付録B — Codex CLI の hooks を「未対応/開発中」と記述

現在は正式機能（9種のライフサイクルイベント）。§8-3 の記述にも波及する。

#### [LIKELY] `00_ai_agent.md:675` — Haiku 4.5 に effort は指定できない

- **現状**: 「Claude Code: Sonnet 4.6 または Haiku 4.5, effort = low」
- **問題**: effort 対応モデルに **Haiku 4.5 は含まれない**。本書自身も L658 で「Haiku 4.5 は Adaptive に未対応」と書いており、L675 と実質的に矛盾している。

#### [LIKELY] `00_ai_agent.md:664` — effort 専用コマンド `/effort` の存在

Claude Code には `/effort`（"Set the model effort level"）がある。`Alt+T`/`Option+T` は「拡張思考のオン/オフ」であり effort の強度指定とは別軸。同じ行に並べると読者が混同する。

#### [CONFIRMED] `10_deliverables.md:77-90` + 演習10-4 — `[build-system]` の欠落と、説明されていない内容を問う演習

- 中核の pyproject.toml 例に `[build-system]` がない。引用元 PyPA ガイドは "The `[build-system]` table **should always be present**" と明記
- さらに**演習10-4 が `[build-system] requires = ["hatchling"]` の意味を答えさせる**のに、`[build-system]`・ビルドバックエンド・hatchling/setuptools/flit を説明した箇所が**全章のどこにも存在しない**

#### [CONFIRMED] `11_cli.md:55-63` — `argparse.FileType` は Python 3.14 で非推奨

公式ドキュメントに "Deprecated since version 3.14" と明記。**本リポジトリ自身が Python 3.14.6 で動作しており、`scripts/ch11/cli_argparse.py` は既に `type=Path` へ移行済みで、本文だけが古いまま取り残されている。**

#### [CONFIRMED] `03_cs_basics.md:718` — `typing` からの Sequence/Iterable/Callable は3.9以降非推奨

PEP 585 により `collections.abc` からのインポートが正しい。本書は Python 3.10+ 前提で、直前の L679/L690 では新記法を教えているのにここだけ旧来の案内になっている。L730 で「mypy --strict で警告が出ないように」と指示させている点とも噛み合わない。

#### [CONFIRMED] `01_design.md:284` — スプリントの期間定義が引用元と矛盾

引用元の Scrum Guide（2020年11月版）は "fixed length events of **one month or less**" と定義。「1〜2週間」は実務慣行であり定義ではない。

#### ★ [CONFIRMED] `12_data_processing.md:46-65` — 「高速化の実例」が比較対象より13倍**遅い**

- **現状**: L21-31 の `seq.count("G") + seq.count("C")` を使うループ版を「遅い」と提示し、L46-63 の `gc_content_vectorized()` を高速な代替として示す
- **問題**: 実測（50,000配列×150bp）は**逆**である。

| 実装 | 時間 |
|---|---|
| L23-28 のループ版（`str.count`） | **10.3 ms** |
| L49-62 の「ベクトル化」版（`np.frombuffer`） | **135.3 ms（13倍遅い）** |
| 真にベクトル化した版（全配列を1バッファ→2D reshape） | 8.3 ms |

原因は、(a) `str.count()` が既にCレベルの走査でありPythonループのオーバーヘッドが1配列につき1回しか発生しないこと、(b) 提示コードが配列ごとのPythonループを残したまま、150要素という小さすぎる配列に `.upper()` / `.encode()` / `np.frombuffer` / 比較2回 / OR / `.sum()` の固定コストを払っていること。

**本章の中心命題「forループを排除して高速化」の実例が、命題と逆の結果を示している。** さらに `figures/ch12_vectorize_bench.png`（"speedup: 72x"）を生成する `scripts/ch12/plot_vectorize_bench.py` は**本文とは別のコード**（1塩基ずつのネストPythonループ vs 事前構築済み整数配列）を測っており、読者が本文のコードで再現しても72倍にはならない。

- **修正案**: 比較対象を「1塩基ずつPythonで判定するネストループ版」に変えるか、ベクトル化版を全配列一括処理に書き換える。あわせて「`str.count` のような文字列組み込みメソッドは既にC実装であり、NumPy化の効果は小さい」という**判断基準**を本文に加えると、読者がエージェントの提案をレビューする力に直結する。

#### ★ [CONFIRMED] `13_visualization.md:389` — 「dpi はベクタ形式では無視される」は誤り

- **問題**: PDF/SVG バックエンドは `dpi` を**埋め込みラスタ要素の解像度**として使う。ベクタ幾何（線・文字）は72 pt/inch固定だが、`imshow`・`pcolormesh`・`rasterized=True` の要素は `figsize × savefig_dpi` ピクセルで実際にラスタライズされる。実測でファイルサイズが最大11倍変わる
- **実害**: ヒートマップや数万点の散布図をPDF入稿する場面はバイオインフォで一般的。デフォルト dpi=100 のまま保存すると埋め込み画像が低解像度になり**投稿規定を満たさない**

#### [CONFIRMED] `13_visualization.md:159-193` — 距離行列を `clustermap()` にそのまま渡すのは誤用

`clustermap()` は入力を**観測値行列**として扱い、その行間のユークリッド距離を計算する。既に距離行列である入力を渡すと「距離の距離」でクラスタリングされる。**本リポジトリの pytest 実行時に出る `ClusterWarning: The symmetric non-negative hollow observation matrix looks suspiciously like an uncondensed distance matrix` はこれが原因である**（テストは通るが結果が意図と異なる）。`figures/ch13_expression_heatmap.png` も同じ経路で生成されている。

#### [CONFIRMED] `08_testing.md:573-584` — Claude Code hooks の設定 JSON が構造的に無効

- **現状**: `{"hooks": {"PostToolUse": [{"matcher": "Edit|Write", "command": "ruff check --fix $FILEPATH"}]}}`
- **問題**: 2点とも動作しない。(1) matcher エントリ直下に `command` は置けず、`hooks` 配列 →`{"type": "command", "command": ...}` のネストが必須。(2) **`$FILEPATH` という環境変数は存在しない**。フックはファイルパスを stdin の JSON（`tool_input.file_path`）で受け取る
- **修正案**: `{"hooks": {"PostToolUse": [{"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "ruff check --fix"}]}]}}`。パスが必要なら `jq -r '.tool_input.file_path'` で取得する旨を補足

#### [CONFIRMED] `09_debug.md:274, 661-673, 695` — pandas の `SettingWithCopyWarning` は現行版で廃止済み

**本リポジトリが lock している pandas 3.0.3 では `pd.errors.SettingWithCopyWarning` が存在しない**（実測で確認）。Copy-on-Write が既定になり、送出されるのは `ChainedAssignmentError`。挙動も「どちらが変更されるか曖昧」ではなく**確定的に何も起きない**（元 DataFrame は不変）。`.loc[]` を使う結論は据え置きでよい。

#### [CONFIRMED] `09_debug.md:643-645` — `a = 257; b = 257; a is b` はスクリプトでは `True`

CPython は同一コードオブジェクト内の定数を共有するため、**.py ファイルに書くと 257 でも `True`** になる。`False` になるのは対話 REPL のように文が別々にコンパイルされる場合だけ。読者がそのまま貼り付けると本文と逆の結果が出る。「小さい整数はキャッシュされる」という説明自体は正しい。

#### [CONFIRMED] `14_workflow.md:506`（および L73） — Terra / AnVIL は CWL を実行できない

「CWLは TRE環境（Seven Bridges、Terra、AnVIL）で価値がある」と記述しているが、**Terra は WDL 専用**（AnVIL も Terra 上で動く）。Dockstore 公式は Terra への launch について "Only the WDL language is supported." と明記。CWL が標準なのは Seven Bridges / CGC である。演習14-1のヒント（L779）が「CWL/WDL」と正しく併記しているのとも矛盾する。

#### [CONFIRMED] `13_visualization.md:483` — `deepTools bamCoverage` というコマンドは存在しない

deepTools は `bamCoverage` / `plotHeatmap` 等を**個別の実行ファイル**としてインストールする。サブコマンド方式のディスパッチャは存在しない。加えて実行ファイル名は小文字 `deeptools` で、`deepTools` は command not found。オプション（`--bam` / `--normalizeUsing RPKM` 等）はすべて正しいので、先頭の `deepTools ` を削除するだけでよい。

#### [CONFIRMED] `15_container.md:496-502` — CUDA のバージョン互換性の説明が誤り

- **現状**: 「3つのバージョンが**一致している**必要がある」「ドライバが CUDA 12.2までサポートしている環境で、CUDA 12.4のコンテナを実行するとエラーになる」
- **問題**: CUDA 11.1 以降、**同一メジャーリリース内では minor version compatibility が保証されている**。CUDA 12.4 でビルドしたコンテナは CUDA 12.x の最低ドライバ要件（>= 525）を満たせば動作する。PyTorch/TensorFlow の公式コンテナはまさにこの仕組みに依存しており、本文の例は現実と逆の指導になる

#### ★ [CONFIRMED] `19_database_api.md:425-437, 126-137` — SPARQL クエリが `PREFIX rdfs:` 欠落で HTTP 400

- **実測したエラー**: `{"exception": "Invalid SPARQL query: Prefix rdfs was not registered using a PREFIX declaration", "metadata": {"line": 8, "positionInLine": 11}, "status": "ERROR"}`
- **裏付け**: (1) 宣言なしで400／宣言ありで200 を実測、(2) W3C SPARQL 1.1 仕様に既定プレフィックスは存在しない、(3) **UniProt 公式のサンプルクエリ126件を全数調査したところ、`rdfs:` を使う例は例外なく全件が `PREFIX rdfs:` を宣言しており未宣言は0件**
- **付属スクリプトには宣言があり、本文だけが欠落している**（本レビューで多発している縮約時の脱落パターン）

#### ★ [CONFIRMED] `19_database_api.md:433` — GO の URI が誤っており、エラーを出さず静かに0件を返す

- **現状**: `http://purl.uniprot.org/go/0005739`
- **問題**: この URI はグラフ中に**主語としても一切存在しない**。正しい `http://purl.obolibrary.org/obo/GO_0005739` ではヒト **3,872件**がヒットする
- **なぜ危険か**: **エラーを出さず静かに0件を返す**ため、読者が原因に到達しにくい。本レビュー全体でも最も発見が遅れる型のバグである

> ⚠️ **修正時の注意**: 上記2点を直す際、**述語 `rdfs:label` は変更してはならない。** 検証の結果、ヒト `up:Protein` の `rdfs:label` 被覆率は 210,709 / 210,709（100%）である一方、**unreviewed（TrEMBL）エントリでは `up:recommendedName/up:fullName` が空**であり、`up:recommendedName` へ書き換えると **TrEMBL エントリが黙って全件脱落する**。書籍の選択のほうが堅牢である。

#### [CONFIRMED] `19_database_api.md:638` — Google Cloud Storage を「認証不要」と誤記

実際は **requester pays** で認証・課金が必須。あわせて `gsutil` は 2027年3月に同梱終了予定。

#### ★★ [CONFIRMED] `06_dev_environment.md:334, 341-350` — conda のチャネル優先順位が**逆**（読者が実際に環境を壊す）

- **現状**: `conda install -c bioconda -c conda-forge samtools minimap2 fastp`（同コラムの4コマンドすべて同順）
- **問題**: conda の `-c` は「与えられた順に検索」＝**先に書いたチャネルが高優先度**。この書き方は bioconda を conda-forge より上に置く。Bioconda 公式は「bioconda は conda-forge に強く依存するため **conda-forge が最高優先度でなければならない**」と明記しており、逆順は依存解決の破綻を招く既知の落とし穴である
- **さらに**: 本書自身が L316 で「conda-forge と bioconda を上位に置く」と述べ、L310-311 の `.condarc` 例では conda-forge を先頭に置いている。**章内で矛盾している**
- **修正案**: すべて `-c conda-forge -c bioconda` に統一。L330 の説明も「先に書いたチャネルが高優先度になるため、bioconda が依存する conda-forge を必ず先に書く」と補う

#### ★ [CONFIRMED] `04_data_formats.md:346-347, 357` — 全角文字に関する Python の挙動が3箇所とも**事実と逆**

実測（Python 3.14.6）の結果:

| 本文の記述 | 実際の挙動 |
|---|---|
| 「`split()` は全角スペースを区切り文字と認識しない」 | 引数なし `str.split()` は Unicode 空白全般で分割する。`"a　b".split()` → `['a', 'b']` |
| 「`int()` は全角数字をパースできない」 | `int("１２３")` → **`123`**（Unicode の Nd カテゴリを受理） |
| 「`int(fields[1])` → `ValueError`」 | `int("　100")` → **`100`**（`int()` が Unicode 空白を strip するため例外は発生しない） |

- **重要**: コラムの結論（「サイレントに失敗する」）**自体は正しく、根拠を実挙動に合わせると主張はむしろ強くなる**。「`int()` は全角数字も全角スペースも黙って受理してしまうため、混入に気づけないまま処理が進む」と書き直すのが適切。なお `awk` 側の記述は正しい（U+3000 では分割されないことを実測で確認）

#### [CONFIRMED] `04_data_formats.md:224-227` — `[project.dependencies]` は不正な pyproject.toml

- **現状**: `[project.dependencies]` テーブルに `biopython = ">=1.83"` 形式で列挙
- **問題**: PEP 621 では `dependencies` は `[project]` 直下の**文字列配列**。テーブル形式は Poetry の `[tool.poetry.dependencies]` の書き方で、標準の pyproject.toml では機能しない。`uvx validate-pyproject` が `ValidationError: 'project.dependencies' must be array` を返す
- **さらに**: **§6:159-169 の同じ例は正しい配列形式**で書かれており、しかも §6:160 が「§4 でも登場」と明示的にリンクしている。章間の矛盾が目立つ

#### [CONFIRMED] `05_software_components.md:560` — Claude Code の MCP スコープ一覧が誤り

- **現状**: 「`-s project` / `-s user` / `-s global`」
- **問題**: 現行のスコープは **`local`（既定）/ `project` / `user`** の3つ。公式ドキュメントは「`user`: Older versions called this scope `global`」と明記しており、**`global` は `user` の旧称**である。しかも**既定値である `local` が表から抜けている**ため、`-s` を省略したときの挙動が読者に伝わらない

#### [CONFIRMED] `05_software_components.md:317, 369` — `conda info <パッケージ名>` は存在しないコマンド

`conda info` は conda インストール自体の情報を表示するコマンドで、**位置引数を取らない**。パッケージの詳細は `conda search --info <pkg>` である。

#### [CONFIRMED] `05_software_components.md:566, 569` — GitHub MCP の npm パッケージは非推奨

`@modelcontextprotocol/server-github` は npm メタデータに `deprecated: "Package no longer supported."` と記載（最終版 2025.4.8）。GitHub 公式は `github/github-mcp-server` へ移管され、リモート HTTP エンドポイント（`https://api.githubcopilot.com/mcp/`）経由が推奨。同表の PostgreSQL MCP も同様に deprecated。

#### [CONFIRMED] `06_dev_environment.md:43` — pyenv のバージョン解決順序が逆

pyenv の優先順位は **`PYENV_VERSION` 環境変数が最優先**、次に `.python-version`、最後にグローバル。本文は上位2つを入れ替えている。

#### [CONFIRMED] `06_dev_environment.md:369-380` — PyTorch の conda インストールは提供終了

PyTorch は公式 Anaconda チャネルへの公開を終了し（2.5系が最後）、現行の公式インストールガイドは **pip のみ**をサポート対象としている。`pytorch-cuda=12.1` も維持されておらず、pip 側の `cu121` インデックスも現行の提供 CUDA（11.8 / 12.6 / 12.8）から外れている。**本書が「conda推奨」と書いている点が特に問題。**

#### [LIKELY] `06_dev_environment.md:92` — Anaconda のライセンス条件の要約が不正確

- **現状**: 「Anacondaのライセンス変更（**商用利用の有償化**）により」
- **問題**: 現行条件は「**従業員・契約者200名以上の組織**に属するユーザーは有償 Business ライセンスが必要」であり、商用/非商用の別ではなく**組織規模**が基準。**200名超の大学・研究所の研究者は「非商用」でも対象になりうる**一方、学術・非営利研究機関には免除規定がある。本書の読者（アカデミアの実験系研究者）にとってこの差は結論を左右する

#### [CONFIRMED] `04_data_formats.md:11` — Forbes 調査の「60%」の意味を取り違えている

- **現状**: 「調査対象のデータサイエンティストの**60%**がデータクリーニングと整理に最も時間を使い」
- **問題**: 60% は「回答者の割合」ではなく「**作業時間に占める割合**」。引用元は "Data scientists spend 60% of their time on cleaning and organizing data"。章冒頭の導入で提示される数字であるため影響が大きい（57% は正しい）

#### [CONFIRMED] `04_data_formats.md:259` — RIKEN クローンIDの科学表記の指数が誤り

`2310009E13` は $2310009 \times 10^{13} = 2.31 \times 10^{19}$ であり、本文の $2.31 \times 10^{13}$ は誤り。表示例 `2.31E+13` は引用元論文の粗い表記を踏襲したものだが、本書はそこに独自の数式解釈を加えており、その数式が算術的に誤っている。

#### [CONFIRMED] `04_data_formats.md:82` / `04_data_formats.md:700` — その他の §4 の誤り

- **OpenStreetMap は CC-BY-SA ではなく ODbL**（2012年9月に移行済み。CC-BY-SA なのは OSM の Wiki のみ）
- 「ヒトの遺伝子の約95%が選択的スプライシングを受ける」は出典（Pan et al. 2008）が **"approximately 95% of multiexon genes"** と限定しており、**「多エクソン遺伝子の」が落ちている**。加えて本文に引用が付いていない

#### [CONFIRMED] `05_software_components.md:171, 179` — `python -m` の `sys.path[0]` は Python 3.11 以降 `''` ではない

Python 3.11（bpo-33053）で `-m` の挙動が変更され、`sys.path[0]` には**カレントディレクトリの絶対パス**が入る。`''` のままなのは対話実行・`python -c`・`python -`。`sys.path` を読ませてデバッグさせる文脈なので誤解を生む。

#### ★★ [CONFIRMED] `20_security_ethics.md:356` — Claude Consumer プランの学習利用の記述が**逆**

- **現状**: 表の行「Claude Code（Consumer Pro / Max）| **学習非利用が既定** | 一般的に30日程度」
- **問題**: Anthropic のプライバシーポリシーの現行文言は "We may use your Inputs and Outputs to train and improve Anthropic AI models, **unless you opt out** through your account settings" — つまり **opt-out 方式で、既定は学習利用**である。保持についても、学習利用を許可した場合は "we may retain your data in a de-identified format for **up to 5 years** in our model training pipelines"。「30日程度」は削除した会話のバックエンド消去期限であって既定の保持期間ではない
- **実害**: **本章はまさに「クラウドAIに何を渡してよいか」を読者に判断させるための表である。** 既定が逆に書かれていると、読者が誤った安心のもとで未発表データや制限付きデータを送信しかねない。本レビュー全体で最も実害が大きい誤りと判断する
- **修正案**: 「学習利用が既定（アカウント設定で opt-out 可）。opt-out しない場合、学習パイプラインで最大5年保持」。本文365行の一般論も同様に要見直し

#### ★ [CONFIRMED] `20_security_ethics.md:309` — ゲノムデータの個人情報該当性が弱められている

- **現状**: 「個人遺伝情報やゲノムデータは個人情報に**該当しうる**」
- **問題**: 引用元ガイドライン[11]自身が「政令第1条第1号イに定める『細胞から採取されたDNAを構成する塩基の配列』のうち、**全核ゲノムシークエンスデータ等は『個人情報』に該当**」と断定している。全核ゲノム／全エクソーム／SNPアレイ等は**個人識別符号**であり、該当性に条件はない。「該当しうる」は読者に判断の余地があるかのような誤解を与える

#### [CONFIRMED] `20_security_ethics.md:293` — JGA の運営主体と申請先が誤り

- **現状**: 「JGA | 運営: DDBJ（日本） | アクセス申請先: データ提供者が指定する DAC」
- **問題**: 公式は「JGA へのデータ登録および利用は、**ライフサイエンス統合データベースセンター (DBCLS)** で審査承認のうえ実施」。申請は humandbs.dbcls.jp への一元申請で、**データセットごとの DAC 方式ではなく中央審査委員会方式**。dbGaP/EGA と JGA の手続きの違いは申請実務に直結する

#### ★ [CONFIRMED] `21_collaboration.md:832` vs `07_git.md:583` — GPL の伝播について章間で矛盾（法的リスク）

- **現状**: 演習21-3のヒント「コードを直接取り込む場合と**インポートして使う場合では、ライセンスの影響範囲が異なる**」
- **問題**: §7 の演習7-3ヒントは正しく「GPL ライブラリを**リンク・インポートして利用する**ソフトウェアは、そのソフトウェア自体も GPL 互換ライセンスで公開する必要がある」と書いている。21章のヒントは「`pip install` して import するだけなら GPL は及ばない」と読め、FSF の立場と矛盾する。**読者が法的リスクを負う**
- **関連**: `21_collaboration.md:790` のまとめ「パーミッシブ同士は互換性あり」も、本文518行が Apache-2.0 → MIT を「△ 要注意」としているのと矛盾。また **LGPL / AGPL は書籍全体で一度も言及がなく**（`grep -rn "LGPL\|AGPL" chapters/` → 0件）、Apache-2.0 が **GPL-3.0 とは互換だが GPL-2.0 とは非互換**という頻出の罠も表にない

#### ★ [CONFIRMED] `16_hpc.md:247` — `afterok` 失敗時に後続ジョブは「自動的にキャンセル」されない

- **問題**: Slurm の既定動作では、依存が満たされ得なくなったジョブは **PENDING のまま残り続ける**（Reason: `DependencyNeverSatisfied`）。自動キャンセルされるのは `DependencyParameters=kill_invalid_depend` が設定されたサイトのみ
- **実害**: 読者が本文どおり信じると、失敗したパイプラインのゾンビジョブがキューを占有し続け、**共有クラスタで他の利用者に迷惑をかける**

#### [LIKELY] `17_performance.md:496-500` — GIL の説明が Python 3.14 の状況に未対応

「CPython には GIL がある」と無条件に断定しているが、Python 3.13 で free-threaded build（PEP 703）が実験的に導入され、**PEP 779 の受理により Python 3.14 で公式サポート（既定ではない）に移行**した。**本リポジトリ自体が Python 3.14.6 上で動作している。** `glossary.md:173` も同様（「3.13以降で実験的」のまま）。

#### [CONFIRMED] `17_performance.md:342-381` ほか — `memory_profiler` は開発終了パッケージ

PyPI の最終リリースは 0.61.0（2022-11-15）で、配布ページに "This package is no longer actively maintained." と明記。§17 は独立した小節を割き、まとめ表・演習17-4でも第一選択として提示している。代替（`memray`、`scalene`、標準ライブラリ `tracemalloc`）の併記が必要。

---

### 2-3. コードの誤り（本文と `scripts/` 実体の乖離）

複数章で**「本文へ縮約する際に決定的な行が落ちて動かなくなっている」**パターンが共通して見つかった。

| 箇所 | 問題 |
|---|---|
| `00_ai_agent.md:173-186` | Viterbi 抜粋で `seq = sequence.upper()` が落ちており、引数 `sequence` に対し本体が `seq` を参照して `NameError`。実体 `scripts/ch00/hmm_gene_predict.py:72` には存在する |
| `11_cli.md:538-555` | `sys` / `min_gc` / `gc_content` の3つが未定義で `NameError`。さらに click 8.x が生成するサブコマンド名は `filter` ではなく **`filter-sequences`**（実体は `@cli.command(name="filter")` で正しく回避している） |
| `11_cli.md:508-516` | rich.Progress スニペットで `Console` が未 import → `NameError` |
| `11_cli.md:622-635` | `logger.setLevel()` がなく、ルートロガー既定の WARNING により **INFO/DEBUG が出ない**。直前で「INFO=処理の進行状況」と教えた直後 |
| `02_terminal.md:503` | 指示例の正規表現が `\\t`（バックスラッシュ+t の2文字）でタブにマッチしない。`\t` が正しい |
| `10_deliverables.md:763-810` | 本文の `validate_fasta` と実体 `scripts/ch10/error_handling.py` が乖離。実体は先頭行検査を行うが本文版は Biopython の deprecated なコメント解釈に依存 |
| `13_visualization.md:80-91` | `from pathlib import Path` が欠落し、`output_path: Path \| None` のアノテーションで **Python 3.13以前は `NameError`**（3.14 は PEP 649 の遅延評価で偶然通る）。実体 `scripts/ch13/bio_plots.py:7` には存在する |
| `12_data_processing.md:244-259` | Polars の lazy 例が存在しない `direction` 列で group_by し、`ColumnNotFoundError` で落ちる。`.with_columns()` の追加が必要 |
| `14_workflow.md:165-183 vs 229` | 本文の `config.yaml` に `fastqc` キーがないのに Snakefile 例が参照。組み合わせると `KeyError: 'fastqc'`。実体 `scripts/ch14/config.yaml:16-18` には存在する |
| `09_debug.md:49, 239` | traceback / pdb の行番号が実体と不一致（30→26、13→28）。さらに **`pdb_demo.py` に `breakpoint()` が1つも無く**、本文209-219のコードが実体に存在しない |
| `08_testing.md:192-198` | `filter_sequences_by_gc` は `scripts/ch01/` にしか無く `scripts/ch08/` に無い。import も示されずコピーしても動かない |
| **`21_collaboration.md` 全体** | **付属スクリプト4本すべてが本文と不一致。** `format_question.py`（`format_question` 関数が存在しない）、`review_helper.py`（`summarize_diff` / `format_pr_description` / `DiffSummary` が存在しない）、`progress_report.py`（本文は `--oneline` 出力を渡させるが実体は `%H\|%s\|%ai` 前提で**必ず空出力**）、`analysis_intake.py`（`REQUIRED_COLUMNS` / `IntakeResult` が存在しない）。いずれもランタイム確認済み |
| `scripts/ch15/Dockerfile` ほか3ファイル | 本文が「Mambaforge は非推奨なので Miniforge3 に揃える」と明言しているのに、付属コードは `condaforge/mambaforge` のまま |
| `scripts/ch15/environment.yml` | チャネル順が bioconda 公式推奨と**逆**（`bioconda` → `conda-forge`）、かつ2024年8月に推奨から外れた `defaults` を含む |
| `scripts/ch16/gpu_train_job.sh:19` | 本文（318-319行）が正しく `conda.sh` + `conda activate` を教えているのに、スクリプトは非推奨の `source activate` |

**これは体系的な問題である。** 本文コードと `scripts/` の同期を検証する仕組み（例: 本文コードブロックを実体から自動抽出する、あるいは差分検出テストを追加する）の導入を検討する価値がある。

---

### 2-3-2. 記載漏れ（誤りではないが、本書のスコープ上の穴）

| 項目 | 状況 |
|---|---|
| **コミット済みシークレットの事後対処** | `grep -rn "filter-repo\|BFG" chapters/` → **0件**。§20-1-1 は予防（`.gitignore` / git-secrets）のみで、履歴書き換えによる除去手順がない。ライフサイクルの「失効」（20:31）と対応していない |
| **ICMJE / CRediT / 研究不正の定義** | `grep -rn "ICMJE\|CRediT\|オーサーシップ"` → **0件**。§21-3 が共同研究のコミュニケーションを扱う以上、著者資格基準と貢献者ロールの不在は目立つ |
| **EU AI Act** | `grep -rn "AI Act"` → **0件**。`20_security_ethics.md:311` の GDPR 行が「AI 関連規制との関係は別途確認が必要」と逃げているのみ |
| **NIH NOT-OD-25-081 / NOT-OD-25-083** | §20 は dbGaP を繰り返し扱うのに、制限付きデータの第三者生成AIへの入力禁止と、**生成AIモデル本体が "Data Derivatives" として同じ制約を受ける**という論点がない |
| **`[build-system]` / ビルドバックエンド** | 全章のどこにも説明がないのに、演習10-4 がその意味を問うている |
| **CPU アーキテクチャの壁** | §15 に `--platform` / `buildx` / arm64 / amd64 の言及が**ゼロ**。Apple Silicon Mac でビルドして HPC の x86_64 で動かす読者が最も高頻度で踏む罠 |
| **終了コードの慣習** | §11 は「適切な終了コード」を良いCLIの要件に掲げるが、`sys.exit` も 0/1/2 の慣習も本文にない |
| **py-spy / scalene** | §17 に未言及。特に py-spy は「すでに走っている HPC ジョブに後から attach できる」点で §16 との接続で実用価値が高い |

---

### 2-4. 数値の誤り

| 箇所 | 現状 | 正しい値 | 確信度 |
|---|---|---|---|
| `00_ai_agent.md:712` | Sonnet 4.6: SWE-bench Verified **79.6%** | Anthropic 公表は **79.2%**（10 trials 平均） | CONFIRMED |
| `00_ai_agent.md:715` | GPT-5.5: SWE-bench Verified **88.7%** | **一次ソースが存在しない**。OpenAI は同指標の報告を停止しており System Card にも記載なし。※エージェント間で判定が割れたため**著者による手動確認が必要**（openai.com は自動取得を拒否） | 要確認 |
| `00_ai_agent.md:715` | 「Anthropic の内部評価では…解決率が **13%** 向上」 | Anthropic の一次記述は「複雑なマルチステップ workflow で **+14%**」。また「13% lift」は**パートナー企業の証言**であり Anthropic の内部評価ではない。CursorBench 58%→70% は正しい（Cursor 社のベンチマーク） | CONFIRMED |
| `00_ai_agent.md:721` | BioCoder で GPT-4 は **約60%** | 論文抄録は "50% versus up to 25%" で**約50%** | LIKELY |
| `00_ai_agent.md:532` | TogoMCP「**20以上**のDB」 | **30以上** | LIKELY |
| `19_database_api.md:533` | BioMCP「**12種**のエンティティ」 | **約30の情報源** | CONFIRMED |
| `02_terminal.md:521` | ripgrep が「再帰検索が **10〜50倍** 高速」 | 引用元のベンチマークは単一ファイルで約**1.9倍**、再帰検索は git grep とほぼ同等。10〜50倍を支持する数値は同記事にない | CONFIRMED |
| `10_deliverables.md:152` | Bioconda「**1万以上**のパッケージ」 | 公式サイトは "over **8000**"。また典拠の2018年論文は「1万以上」の出典にならない | LIKELY |
| §20 UK Biobank RAP | 40PB以上 / 28,000人以上 / 90か国以上 | **30PB超 / 22,000人超 / 60か国超**（3つとも過大） | CONFIRMED |
| §20 AnVIL | 60万サンプル以上 | 裏付けなし。公式は **293k participants / 4.7PB+ / 67 studies / 382 datasets** | CONFIRMED |
| §20 Cancer Genomics Cloud | 850以上のツール | **900以上** | CONFIRMED |
| `02_terminal.md:839` / `ch02.bib:75` | fd の作者 "Peterka, D." | **Peter, David**（GitHub `sharkdp` の本名） | CONFIRMED |
| `03_cs_basics.md:127` | Counter の出力例 | `'CGA': 2` が欠落し順序も異なる。実際は `Counter({'CGA': 2, 'GAT': 2, 'ATC': 2, 'TCG': 2, 'ATG': 1, 'TGC': 1, 'GCG': 1})` | CONFIRMED |
| `03_cs_basics.md:742` | まとめ表「sum()で0.1を10回足すと1.0にならない」 | 本文 L299-300 と矛盾。Python 3.12以降の `sum()` は **1.0 になる**（実測）。「**逐次加算**で」に直せば全バージョンで成立 | CONFIRMED |

---

### 2-5. 陳腐化した記述

| 箇所 | 内容 |
|---|---|
| `00_ai_agent.md:643-687`、付録B | モデルラインナップが2世代古い（Part 1-1 参照） |
| `00_ai_agent.md:1001` | 参考文献[29]の URL が **Opus 4.8 のページを返す**。本文7箇所（600, 658, 668, 694, 736, 742, 808行）がこれに依拠しており読者が検証できない |
| `00_ai_agent.md:55, 973-979, 1004` ほか | 主要な公式ドキュメント URL がすべて 301/308 リダイレクト（`docs.anthropic.com` → `code.claude.com` / `platform.claude.com`、`developers.openai.com/codex/models` → `learn.chatgpt.com/docs/models`） |
| `00_ai_agent.md:523`、`11_cli.md:377-382` | Claude Code のカスタムコマンドは skills に統合済み。Codex のスキルは `.agents/skills/<name>/SKILL.md`（「プロジェクトルートに SKILL.md」は誤り） |
| `03_cs_basics.md:415, 834` | Unicode 16.0 を参照。最新は **17.0.0（2025年）** |
| `15_container.md:648` | Apptainer 1.3 → **1.5.2** |
| `06_dev_environment.md:20, 459` | scanpy 1.9/1.10 → **1.12.2**、pandas 1.5.3/2.2.0 → **3.0.x** |
| `07_git.md:280`、`08_testing.md:634,637,681,682`、`scripts/ch07/ci_minimal.yml` | `actions/checkout@v4` / `actions/setup-python@v5`。**リポジトリ実物の `.github/workflows/test.yml` は `actions/checkout@v6` を使っており内部不整合** |
| `08_testing.md:688` | CI マトリクスが Python 3.10/3.11/3.12。本リポジトリの venv は **3.14.6** |
| 付録A | 3行目「2026年4月時点」 vs 95行目「2026年3月時点」で**同一文書内が矛盾** |
| 全体 | 参照日が 2026-03 が197件、2026-04 が20件。改訂時に一括更新が必要 |

---

### 2-6. その他の不整合

#### [CONFIRMED] 書名の表記ゆれ

| ファイル | 書名 |
|---|---|
| `README.md:1` | 『AIエージェントを使いこなす はじめてのバイオインフォマティクス開発作法』（新） |
| `CLAUDE.md:4` | 『AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法』（旧） |
| `CHANGELOG.md:3` | 同上（旧） |
| `vivliostyle.config.js:2` | 同上（旧） |

表紙PDFビルドは新タイトルを使用している。**旧タイトルが3ファイルに残存**し、サブタイトルも2種併存している。

#### [CONFIRMED] `00_ai_agent.md:940-942` — 演習0-4 が本文に存在しない用語を参照

演習0-4 は「§0-4 で**学んだ** Writer/Reviewer パターン」と書くが、§0-4（536-579行）に「Writer/Reviewer」という語は一度も出てこない。同節は「実装後のセルフレビュー」「別人格レビュー」「テスト生成によるレビュー」の3構成。

#### 付属リポジトリの環境ギャップ

- `pyproject.toml` は `requires-python = ">=3.10"` だが実際の venv は **Python 3.14.6**
- **pyarrow と cffconvert が未導入**のため、テスト2件が静かにスキップされる（`tests/ch17/test_file_format_bench.py`、`tests/ch07/test_citation_cff.py`）
- §13 は Plotly を扱うが依存に含まれない。ただし `13_visualization.md:280` に「Plotly未インストールの環境でもMatplotlib/Seabornのコードがすべて動作するようにするため」と**理由が明記されており、意図的な設計**である

---

## Part 3: 修正方針の提案

### 方針A（改訂版）: モデル名を「型」で分け、型ごとに更新ポリシーを定める

> **初版の方針Aは「モデル名を本文から追い出す」だったが、これは目的と手段を取り違えていた。** 本当の目的は「更新すべき箇所を局所化し、**更新が必要かどうかを判断できるようにする**」ことであり、モデル名の有無は手段の一つにすぎない。以下は再検討後の設計である。

#### なぜ単純な追い出しが成立しないのか — effort 推奨は6か月で2回反転している

公式の使い分け推奨は、モデル世代の交代とともに**内容そのものが変わる**。実際の変遷は以下である。

| 世代 | effort の段階 | 公式の推奨 |
|---|---|---|
| Opus 4.6 / Sonnet 4.6 | low / medium / high / max | （xhigh は存在しない） |
| **Opus 4.7** | **xhigh を追加** | 「コーディング・エージェント作業は **`xhigh` スタート**、通常の知的作業で最低 `high`」 |
| **Opus 4.8** | 同左 | 「**`high` を既定として反復せよ**。従来 `xhigh` を反射的に選んでいたが、4.8 は知能の上限が高いので `xhigh` を初期値にするな」← **推奨が反転** |
| **Fable 5** | 同左 | 「**`low` を含む低い effort でも、旧世代の `xhigh` や `max` を上回ることが多い**」。加えて **thinking が常時オン**になり、オン/オフという軸自体が消滅 |
| **Sonnet 5** | 同左 | `thinking` 省略時の既定が **4.6 の「思考なし」から「adaptive」へ反転** |

**本書 `00_ai_agent.md:668` の「`xhigh` スタート」は、Opus 4.7 の推奨としては正しかったが、現行世代では誤った助言になっている。** ここからモデル名を抜いて「コーディングでは xhigh から始める」と一般化すると、**いま誤りである助言が、誤りだと判別できない形で無期限に残る**。モデル名と世代を明示してあれば、読者は「これは 4.7 時点の推奨だ」と気づける。

同じことは API 仕様にも当てはまる。「`budget_tokens` は受け付けない」「`temperature` は 400 エラー」は**どの世代からそうなのか**が分からなければ役に立たない。

#### 記述を6つの型に分け、型ごとに方針を変える

| 型 | 例 | モデル名 | 更新方針 | 置き場所 |
|---|---|---|---|---|
| **A 記録** | `hajimeni.md:127` の執筆環境、§0-1 の実行結果（ORF 279個 / HMM 19個） | **必須・凍結** | **書き換えない。** 改訂時は追記する（「初版は Opus 4.7、第2版は Fable 5 で執筆」） | 本文のまま |
| **B 概念** | 「モデル選択と推論の深さという2軸」「タスクの複雑さに応じて使い分ける」 | **書かない** | ほぼ不変 | 本文の中核 |
| **C 使い分け推奨** | effort 戦略、プロンプト設計指針、サブエージェント生成傾向 | **必要・世代を明示** | **判定基準（下記）に該当したときのみ本文改訂** | 本文＋日付マーカー |
| **D API仕様・破壊的変更** | `budget_tokens` が 400、トークナイザ 1.35倍、サンプリングパラメータ非対応 | **必須** | 世代交代時に必ず確認 | 本文＋対照表 |
| **E ベンチマーク数値** | SWE-bench スコア、価格 | 対照表へ集約 | 都度更新、または「読み方」の記述へ転換 | 対照表のみ |
| **F 用語定義の例示** | context window「200K〜1M」、effort の段階 | 例示として最小限 | 対照表を参照させる | 用語集 |

**型Aを凍結扱いにすることが重要である。** `hajimeni.md:127`「本書の執筆やレビューは、Claude Code CLI (Claude Opus 4.7, effort: high) および Codex CLI (GPT-5.4 / GPT-5.5, reasoning: xhigh) の支援のもとで行った」は**再現性の記録**であり、現行モデル名に書き換えると事実を偽ることになる。§0-1 の遺伝子予測の出力例（ORF 279個 → HMM後 19個）も同様で、これは実際に得られた結果である。

#### 型Cの判定基準 — 本文改訂が必要か、対照表更新で足りるか

新しいフロンティアモデルが出たとき、**以下のいずれかに該当すれば本文を改訂する**。該当しなければ対照表の更新だけでよい。

1. **制御軸そのものが増減・変質した** — 例: `budget_tokens`（手動予算）→ adaptive thinking（自動）で「予算を指定する」という概念が消えた。`xhigh` の追加で段階が増えた。Fable 5 で thinking が常時オンになりオン/オフ軸が消えた
2. **推奨の向きが反転した** — 例: 4.7「xhigh スタート」→ 4.8「high から始めて反復。xhigh を反射的に使うな」
3. **階層の構造が変わった** — 例: **Opus の上に Fable / Mythos クラスが加わり「3階層」が成立しなくなった**
4. **人間の判断ポイントが移動した** — 例: 「4.7 はサブエージェントを自発生成しにくいので明示指示が必要」という助言は、モデルが自発的に委譲するようになれば不要になる
5. **破壊的な API 変更** — 400 エラーになるパラメータの増減

**逆に、対照表の更新だけでよいもの**: 価格改定、ベンチマークスコアの更新、context window の拡大、同一ティアの世代交代で使い方が変わらない場合。

#### 実装: 日付マーカーで「いつ時点の推奨か」を読者にも更新者にも見せる

型Cと型Dのブロックに、以下の形式のマーカーを置く。

```markdown
> 📌 **モデル世代依存の記述**（最終確認: 2026-07-19 ／ 対象世代: Claude Fable 5 / Opus 4.8 / Sonnet 5、GPT-5.6 Sol / Terra / Luna）
> 一次情報: https://platform.claude.com/docs/en/build-with-claude/effort
>
> （ここに推奨内容）
```

これは**保守のためだけでなく読者のためでもある**。マーカーがなければ、2027年の読者は「xhigh スタート」が古いと知る手段がない。マーカーがあれば、日付を見て一次情報を当たれる。同時に `grep -n '📌 \*\*モデル世代依存'` で更新対象を機械的に列挙できる。

あわせて `docs/model_generations.md`（または付録Bの拡張）に、時制依存ブロックの**マニフェスト**を置く。

| 場所 | 型 | 最終確認 | 一次情報 | 判定メモ |
|---|---|---|---|---|
| `00_ai_agent.md:668` | C | 2026-07-19 | effort docs | 4.8 で推奨が反転したため要改訂 |
| `00_ai_agent.md:658` | D | 2026-07-19 | migration guide | Fable 5 で thinking 常時オン化 |
| … | | | | |

GitHub 公開が主で、かつ AI エージェントによる調査を使える条件では、**「マニフェストの各行について一次情報を確認し、判定基準に照らして本文改訂の要否を判断せよ」という定型タスク**に落とせる。フロンティアモデルのリリース都度（実績で2〜3か月間隔）に走らせれば、更新は数十ブロックの確認に収まる。

#### 今回の改訂で実際に起きること

上記の判定基準を当てはめると、今回は**判定基準3と1と2のすべてに該当**するため、本文改訂が必要である。

- **判定基準3（階層構造の変化）**: Opus の上に Fable 5 / Mythos 5 が加わった。`00_ai_agent.md:645-647` の3階層表は成立しない
- **判定基準1・2（軸の変質と推奨の反転）**: 上記のとおり effort 推奨が反転し、thinking が常時オン化した

また調査の副産物として、**現在の3階層表には設計の非対称がある**ことが分かった。Claude 側は `Opus` / `Sonnet` / `Haiku` と**ティア名のみでバージョン番号がなく既に抽象化されている**のに対し、**Codex 側は `GPT-5.5` / `GPT-5.4` / `GPT-5.4-mini` とバージョン番号がそのまま入っている**。これは OpenAI 側に恒久的なティア名が存在しなかったためで、書き方の不統一ではなく構造的な制約だった。

**GPT-5.6 で Sol / Terra / Luna というティア名が導入されたことで、この非対称が解消できる可能性がある。** 両者を「フラッグシップ / バランス / 軽量」という共通語彙で書き、ティア名を併記する形にすれば、バージョン番号を本文から外しつつ使い分けの説明を保てる。ただし Sol / Terra / Luna が次世代でも維持される保証はないため、対照表側で追随できる構造にしておくこと。

### 方針B: ベンチマーク節の再構成

§0-7 のベンチマーク節は、単なる数値更新では済まない。**「ベンチマークそのものが信頼できるか」という2026年前半の論点を取り込む**ことで、かえって本書の価値が上がる。

1. SWE-bench Verified / Pro の汚染・破損問題と、OpenAI による報告停止・撤回の経緯を記述する
2. ベンダー自己申告値と独立実測値を明確に区別し、条件（trials数、thinking budget、effort、scaffold）の併記を原則とする
3. **FrontierCode**（最高性能モデルでも Diamond 13.4%）を導入し、「正解を出す」と「マージされるコードを書く」の落差を示す。これは本書の中心テーマを数値で裏づける
4. Terminal-Bench 2.1 のスキャフォールド差（同一モデルで 3.4 ポイント）を、誤帰属している引用[17]の統計値の**差し替え**として使う

### 方針C: 引用の一斉検証

引用の誤りが最も多いカテゴリであり、しかも**「引用先がその主張をしていない」という誤帰属**が複数見つかった。数値・統計を引用している箇所は、原典に当たって以下を確認する運用を推奨する。

- その数値が原典に実在するか
- 条件（データセット、試行回数、サブセット）を落として一般化していないか
- 帰属先（誰の評価か）が正確か

`scripts/reference_usage.py` は本文と BibTeX の対応を判定できるが、**「主張と文献内容の一致」までは検証できない**。この部分は人手またはエージェントによるレビューが必要である。

### 方針D: 本文コードと `scripts/` の同期検証

本文への縮約時に import や引数が落ちるパターンが章をまたいで多発している。本文のコードブロックを `scripts/` の実体から自動生成するか、少なくとも差分を検出する仕組みの導入を検討したい。

### 方針E: 更新頻度で記述を層別する

今回の調査で、記述の陳腐化速度に大きな差があることが分かった。

| 層 | 例 | 更新頻度 | 推奨する扱い |
|---|---|---|---|
| 揮発性が高い | モデル名・価格・ベンチマーク値・CLI のフラグ | 数か月 | 対照表に集約し時点を明記 |
| 中程度 | ライブラリのバージョン・DBのURL・レート制限 | 1年 | 本文に書くが具体値は最小限に |
| 安定 | 設計原則・計算量・座標系・UNIX哲学・テスト技法 | 数年〜 | 本文の中核に置く |

本書は既に「概念で記述する」方針を持っているため、これを**モデル・ベンチマーク・ツールバージョンにも一貫適用**することで、次回改訂の作業量を大きく減らせる。

---

## 未確認・要手動確認の項目

以下は自動調査では確定できなかった。著者による確認を推奨する。

1. **GPT-5.5 の SWE-bench Verified 88.7%** — エージェント間で判定が割れた。openai.com は自動取得を拒否（HTTP 403）するため、ブラウザでの確認が必要
2. **Deep Research の現行ベースモデル** — 本書の「2026年2月に GPT-5.2 へアップグレード」はその時点では正確。ただし GPT-5.2 は 2026-06-12 に ChatGPT から提供終了済みで、現行ベースは特定できず。**時点を明記する書き方が安全**
3. **Codex CLI の `--profile` 旧記法**（config.toml 内 `[profiles]`）の後方互換性 — 実機検証が必要
4. **`plan_mode_reasoning_effort`** — 公式 config-reference ページが404で一次確認できず
5. **Terra on Azure の存廃**（2025-2026年の動向）
6. **rest.ensembl.org の正確な停止日と BioMart の後継** — 移行告知に BioMart への言及がない
7. **Compeau & Pevzner の版と刊行年の対応**（`03_cs_basics.md:813`：3rd ed. と 2015年が食い違う可能性）
8. **Codex CLI の ripgrep 依存**（`02_terminal.md:521`）と fd が Claude Code で推奨されているか

---

## 付記: 本レビューのカバー範囲

| 対象 | 状況 |
|---|---|
| 全22章（§0〜§21）、はじめに、免責事項、付録A〜D、用語集、著者紹介、README | **レビュー完了** |
| 機械的検証（相互参照・引用番号・テスト・ruff・URL生存・コードフェンス） | 全章について完了 |

§4 の座標系（BED=0-based half-open / GFF=1-based closed、pysam の `reference_start + 1` 変換、pyranges / pybedtools / Biopython SeqFeature）は**全項目が正確**であることが実行検証で確認された。本書の中核をなすドメイン知識の記述は信頼できる。

---

## 付記: 調査の限界

- 複数のエージェントが WebSearch のセッション予算上限（200件）に到達した。上記「未確認」項目の解消には追加調査が必要である
- openai.com、science.org、cell.com、elifesciences.org、grants.nih.gov は自動取得を拒否した。NIH の告知は Internet Archive 経由で原文確認した
- 検索要約は年号を複数箇所で誤っていたため（例: AlphaFold v3.0.0 を「2023年11月」と要約）、バージョン情報は git コミット履歴 / PyPI JSON API / GitHub Releases API / Ensembl REST API / UniProt レスポンスヘッダを**直接叩いて一次検証**した
