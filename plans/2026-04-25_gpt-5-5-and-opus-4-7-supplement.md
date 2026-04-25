# GPT-5.5 対応 + Opus 4.7 補強 — 原稿アップデート計画

## Context

前回の Opus 4.7 対応（commit `71279da`）の後、新たに 2 つの公式情報が出た。

1. **GPT-5.5 公開（2026-04-23）** — Codex CLI のモデルラインナップが GPT-5.5 / GPT-5.4 / GPT-5.4-mini / GPT-5.3-Codex / GPT-5.3-Codex-Spark に再編。GPT-5.5 が新しい推奨デフォルトに昇格
2. **Anthropic 公式 Opus 4.7 ニュース記事** — 前回未取得だった具体ベンチマーク数値（Opus 4.6 比 +13% 解決率、CursorBench 58→70%、BigLaw 90.9%、Rakuten-SWE 3 倍）と公開日（**2026-04-16**）が判明

これを踏まえて、Codex CLI 周りのモデル階層と、§0-7 ベンチマーク表周辺の Opus 4.7 記述を補強する。

## ユーザー方針（確定済）

1. Codex CLI のモデル階層は **GPT-5.5 / GPT-5.4 / GPT-5.4-mini** に置き換え
2. **GPT-5.5 の価格は本書に載せない**（公式ページ 403 で取得不可、二次情報を載せるリスク回避、リーダーボード/公式 pricing への誘導で十分）
3. `hajimeni.md` L127 の執筆環境表記は **GPT-5.4 と GPT-5.5 を併記**
4. **SWE-bench Pro での Opus 4.7 (64.3%) vs GPT-5.5 (58.6%) を本文に書く**（「タスク特性で得意モデルが異なる」例）

## GPT-5.5 主要情報（公式 Codex Developer ドキュメント由来）

- リリース: 2026-04-23、Codex CLI / ChatGPT (Plus/Pro/Business/Enterprise) で利用可
- 新ラインナップ: **GPT-5.5**（推奨デフォルト）/ GPT-5.4 / **GPT-5.4-mini**（新登場、subagents 向け）/ GPT-5.3-Codex / GPT-5.3-Codex-Spark
- ベンチマーク:
  - SWE-bench Verified: **88.7%**
  - SWE-bench Pro: **58.6%**（Opus 4.7 64.3% に劣後）
  - Terminal-Bench 2.0: **82.7%**（state-of-the-art）
- デフォルト reasoning effort: **medium**、評価は `xhigh` で実施
- GPT-5.4 と同 per-token レイテンシで、同じ Codex タスクをより少ないトークンで完了

## Opus 4.7 公式記事から得た追加情報（前回未取得）

- **公開日: 2026-04-16**
- 内部コーディング評価: **Opus 4.6 比 13% 解決率向上**
- CursorBench: **58%（4.6）→ 70%（4.7）**
- BigLaw Bench for Harvey: 90.9%（高 effort）
- Rakuten-SWE-Bench: Opus 4.6 比 3 倍解決
- 「指示追従の大幅改善」「ファイルシステムメモリ活用の向上」「難問途中放棄せず推進」傾向

## 修正箇所リスト

### 🔴 GPT-5.5 関連

#### `chapters/appendix_b_cli_reference.md` L37-46 モデル階層表
- L39 最高精度: `Opus 4.7 / GPT-5.4` → `Opus 4.7 / **GPT-5.5**`
- L40 バランス: `Sonnet 4.6 / GPT-5.3-Codex` → `Sonnet 4.6 / **GPT-5.4**`
- L41 高速・低コスト: `Haiku 4.5 / GPT-5.3-Codex-Spark` → `Haiku 4.5 / **GPT-5.4-mini**`

#### `chapters/00_ai_agent.md` §0-7 L645-647 モデル階層表
- 同上の Codex 列を更新（GPT-5.4 → **GPT-5.5**、GPT-5.3-Codex → **GPT-5.4**、GPT-5.3-Codex-Spark → **GPT-5.4-mini**）

#### `chapters/00_ai_agent.md` §0-7 L671-684 使い分けの指針コードブロック
- 簡単な修正: `Codex: GPT-5.3-Codex, Reasoning = Low` → `Codex: GPT-5.4-mini, Reasoning = Low`
- 日常実装: `Codex: GPT-5.3-Codex, Reasoning = Medium（デフォルト）` → `Codex: GPT-5.4, Reasoning = Medium`
- 複雑設計: `Codex: GPT-5.4, Reasoning = High / Extra High` → `Codex: GPT-5.5, Reasoning = High / Extra High`

#### `chapters/00_ai_agent.md` §0-7 L715 ベンチマーク間順位入れ替え
- 現状:「Terminal-Bench 2.0 では GPT-5.3-Codex が首位 (77.3%)、LiveCodeBench では Gemini 3 Pro が首位 (91.7%)」
- 更新案:「Terminal-Bench 2.0 では **GPT-5.5 が首位 (82.7%)、SWE-bench Pro では Claude Opus 4.7 が首位 (64.3%、GPT-5.5 は 58.6%)、LiveCodeBench では Gemini 3 Pro が首位 (91.7%)** と…」（Opus 4.7 の SWE-Pro 優位を「タスク特性で得意モデルが異なる」例に追加。LiveCodeBench は維持）

#### `chapters/hajimeni.md` L127 執筆環境表記
- 現状: `Codex CLI (GPT-5.4, reasoning: xhigh)`
- 更新案: `Codex CLI (GPT-5.4 / GPT-5.5, reasoning: xhigh)`

#### `references/ch00.bib`
- 新エントリ追加:
  - `openai2026introducinggpt55` — https://openai.com/index/introducing-gpt-5-5/
  - `openai2026codexmodels` — https://developers.openai.com/codex/models

### 🔴 Opus 4.7 補強

#### `chapters/00_ai_agent.md` §0-7 L713 ベンチマーク表後の文言
- 現状:「2026年4月に Anthropic は Claude Opus 4.7 を Opus 4.6 と同じ $5 / $25 per MTok で公開し、agentic coding のさらなる向上を報告している[29]。最新のスコアは [SWE-bench リーダーボード] を参照されたい」
- 更新案:「**2026年4月16日に** Anthropic は Claude Opus 4.7 を Opus 4.6 と同じ $5 / $25 per MTok で公開した。Anthropic の内部評価では Opus 4.6 比でコーディング解決率が **13% 向上**し、**CursorBench では 58% から 70% に改善している**[新脚注: anthropic news]。最新のスコアは [SWE-bench リーダーボード] を参照されたい」

#### `references/ch00.bib`
- 新エントリ追加:
  - `anthropic2026opus47news` — https://www.anthropic.com/news/claude-opus-4-7

### 🟠 中優先度

#### Opus 4.7 補強の波及候補（必要に応じて）
- `chapters/00_ai_agent.md` §0-8 アンチパターン表後の補注（前回追加済）に「指示追従の大幅改善」を 1 単語強める余地あり → **見送り**（既存記述で十分）
- `chapters/glossary.md` Adaptive thinking 項に「ファイルシステムメモリ活用の向上」を追加するか → **見送り**（メモリは別文脈で本書外）

### 🟡 変更不要

- `chapters/hajimeni.md` L10 の年表記述: 2025 年末時点の物語として保持（4 月時点の数値を加えると物語が冗長化）
- `chapters/00_ai_agent.md` §0-2 Deep Research コラム: GPT-5.5 が DR に組み込まれたかは未確認のため現状維持
- 付録D「ChatGPT/Codex 特有の傾向」: GPT-5.5 system card 詳細未取得、変更見送り
- `chapters/glossary.md` の Effort 項: GPT-5.5 を加えると Codex 側の記述が重くなるため、現状の「Codex CLI では Reasoning Effort という同等の概念」表現で十分

## 脚注番号の処理

前回の編集で §0 の脚注は [29] まで使用。今回追加する 3 つの脚注:
- [30] anthropic.com news/claude-opus-4-7（Opus 4.7 補強で本文参照）
- [31] openai.com index/introducing-gpt-5-5（必要なら本文参照、または bib のみ）
- [32] developers.openai.com/codex/models（必要なら本文参照、または bib のみ）

GPT-5.5 関連は対照表の更新中心で本文での新規 inline 引用は不要。脚注 [30] のみ本文（Opus 4.7 補強）で参照。
[31] [32] は references/ch00.bib に登録するが、本文での脚注番号付与は見送る（対照表中の表記更新のみで足りる）。

## 検証方法

1. **grep で残存チェック**:
   ```
   grep -rn "GPT-5\.3-Codex\|GPT-5\.3-Codex-Spark" chapters/
   grep -rn "GPT-5\.4" chapters/   # hajimeni 併記行と既存歴史記述以外残存しないこと
   ```
2. **脚注整合**: 新規 [30] が本文と末尾欄で揃う
3. **相対リンク維持**: §0-7 アンカー、glossary・付録間の参照を変更しない
4. **表崩れ**: pandoc ビルドで HTML/PDF を出して目視確認
5. **コミット**: 1 commit で「Codex CLI を GPT-5.5 世代に更新、Opus 4.7 のベンチマーク補強」

## 関連ファイル
- `chapters/00_ai_agent.md`
- `chapters/appendix_b_cli_reference.md`
- `chapters/hajimeni.md`
- `references/ch00.bib`
- 前回アーカイブ: `plans/2026-04-25_claude-opus-4-7-migration.md`（参考用、本回は別計画）
