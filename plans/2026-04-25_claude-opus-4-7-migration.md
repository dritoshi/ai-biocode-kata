# Claude Opus 4.7 対応 — 原稿アップデート計画

## Context

Claude Opus 4.7（モデル ID `claude-opus-4-7`）の登場により、Messages API の挙動・プロンプト指針に複数の重要変更が入った。本書は 2026年3〜4月時点の Claude Opus 4.6 を前提に書かれており、該当記述を 4.7 に合わせて更新する必要がある。

### 4.7 の主要変更点（3 つの公式ドキュメント統合）

**API・挙動**
- `temperature` / `top_p` / `top_k` を非デフォルト値にすると 400 エラー
- Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) は 4.7 では 400 エラー
- **Adaptive thinking が Opus 4.7 で唯一のモード**、かつ**デフォルト OFF**（明示的に `thinking: {type: "adaptive"}` を指定しないと思考しない）
- **Adaptive thinking は Interleaved thinking を自動有効化** — ツール呼び出しの間で考えられる。エージェント用途で特に有効
- `thinking.display` のデフォルトが Opus 4.7 では `"omitted"`（4.6 は `"summarized"`）。思考内容を見たければ `"summarized"` を明示
- 新トークナイザ: 1.0〜1.35x のトークン消費増、`max_tokens` に余裕が必要
- 1M コンテキスト / 128k 出力、1M が標準価格（long-context premium なし）
- 高解像度画像対応（2576px / 3.75MP）、座標はピクセルと 1:1
- サンプリングパラメータ（temperature 等）廃止によりプロンプト側で挙動を制御

**Effort パラメータ（output_config.effort）**
- レベル: `max`, **`xhigh`（Opus 4.7 のみ）**, `high`（デフォルト）, `medium`, `low`
- 効果範囲: thinking だけでなく、テキスト応答・ツール呼び出し・tool args を含む**全トークン**に影響
- **Opus 4.7 の推奨**:
  - コーディング・エージェント → `xhigh` スタート
  - 知的作業の最低ライン → `high`
  - コスト重視 → `medium`
  - `max` は eval で `xhigh` に余裕がある時のみ
- Opus 4.7 は 4.6 より effort を**厳格に遵守**（低 effort では「頼まれた範囲」しかやらない、周辺は補完しない）
- shallow reasoning を見たらプロンプトではなく effort を先に上げる
- `xhigh` / `max` 使用時は `max_tokens` を 64k 以上に
- Sonnet 4.6 はデフォルト `high` だが**運用上は `medium` 推奨**（レイテンシ抑制）
- Opus 4.6 / Sonnet 4.6 での `budget_tokens` は deprecated（将来削除）

**Task budgets (beta)**
- エージェントループ全体のトークン予算を「モデルが認識する助言」として渡せる
- `max_tokens` との違い: task_budget はモデルに見える、max_tokens は見えないハードキャップ
- ベータヘッダ `task-budgets-2026-03-13`、最小 20k

**挙動変化（= プロンプトの書き方のコツ）**
- より字義通りの指示追従（特に低 effort 時）。暗黙的一般化をしない → 指示は**列挙**する
- 応答長はタスク複雑度に自動調整（固定の饒舌さではない）
- ツール呼び出しはデフォルト減（推論優先）。増やしたければ effort を上げる
- トーンは直接的、検証フレーズ・絵文字は減少
- 自発的な進捗報告が増える → 強制する scaffolding は外して再評価
- サブエージェント生成は抑制的。プロンプトで steerable
- 4.6 向けの防御的 scaffolding（"ダブルチェックしろ" "冗長にするな" "中間ステータスを出せ"）は外して再ベースライン

本計画は **修正箇所のリスト化まで** を対象とする（実装は別タスク）。

---

## 修正箇所リスト（ファイル別・優先度順）

### 🔴 優先度: 高（事実誤認になる記述）

#### `chapters/hajimeni.md`
- **L127**: 「Claude Code CLI (Claude Opus 4.5, effort: high)」
  - `Opus 4.5` → `Opus 4.7` に更新。`effort: high` 表記は 4.7 仕様でも妥当（`xhigh` に上げるかは著者判断）
  - 注意: 執筆完了時点の記録という性格もあるため、書き換えか併記か要判断

#### `chapters/00_ai_agent.md` — §0-7 モデル選択・推論の深さ・コスト意識
- **L640-647 モデルの階層表**: バージョン番号の表記方針を 4.7 世代に揃える（Opus 4.7 / Sonnet 4.6 or 4.7 / Haiku 4.5 or 4.6）
- **L649-659 推論の深さ (Reasoning Depth)** — 全面改訂が必要:
  - 概念名「**Extended Thinking**」→「**Adaptive Thinking**」に刷新。脚注12の URL を `adaptive-thinking` ページに差し替え
  - L656「ON / OFF（Opus 4.6ではadaptive thinkingが自動調節）」→「**Opus 4.7 ではデフォルト OFF、`thinking: {type: "adaptive"}` を明示指定して ON**」。Manual thinking (`budget_tokens`) は 4.7 で廃止、4.6/Sonnet 4.6 でも deprecated
  - 「段階 ON / OFF」の二段階モデルは古い。effort レベル（`low` / `medium` / `high` / `xhigh` / `max`）が新しい調整軸である旨を明示
  - L657-659 切り替え方法・計画時設定: Claude Code CLI 側の操作（Alt+T / Plan Mode）は維持できるが、API レベルでは `output_config.effort` に書き換え
- **L661-678 使い分けの指針** — 全面刷新:
  - L666「Sonnet（adaptive thinkingに任せる）」→ Sonnet 4.6 では effort `medium` 明示推奨（レイテンシ回避）
  - L676「Opus + Extended Thinking ON」→ Opus 4.7 + effort `xhigh`（コーディング・エージェント）
  - 新しい三段階の指針例:
    - 簡単な修正 → Sonnet/Haiku + effort `low` or `medium`
    - 日常実装 → Sonnet + effort `medium`
    - 複雑な設計 → Opus 4.7 + effort `xhigh`（必要なら `max`）
- **L680-684 コスト意識** — 補強:
  - 脚注7（pricing）は維持。加えて新トークナイザで同テキスト 1.0〜1.35x のトークン増を明記
  - `max_tokens` を `xhigh`/`max` 使用時は 64k 以上に、を触れる
- **L686-707 ベンチマーク表**:
  - L697 「2026年3月時点」→ 更新
  - L701-703 の Opus 4.6 / Sonnet 4.6 / Haiku 4.5 行 → 4.7 世代のスコア・価格に要更新（要調査）
  - L705 Sonnet 4.6 と Opus 4.6 の 1.2 ポイント差記述も再計算
- **L724-726 本書の再現性** — 記述刷新:
  - 「temperature=0 に設定しても…」は Ouyang et al. 2025 の一般論として残せるが、「Claude Opus 4.7 以降の Messages API では `temperature`/`top_p`/`top_k` パラメータ自体が設定不能（400 エラー）」を補注
  - 「モデル側の非決定性は削減不可能」「決定性が必要なら出力の Syntax 評価・テストで担保」を強調
- **追加挿入候補**（§0-7 末尾または新サブ節「4.7 世代で押さえるポイント」）:
  - Adaptive thinking のデフォルト OFF と明示指定の重要性
  - `thinking.display` のデフォルトが `"omitted"`（ストリーム時の first-text が速くなるが思考内容は見えない）
  - Interleaved thinking の自動有効化 → エージェント協働で有利
  - Effort と `max_tokens` の併用指針
  - Task budgets (beta) の紹介（脚注扱いでも可）
  - プロンプトで 4.6 向けに入れていた防御的 scaffolding を外すとよい、という移行指針

#### `chapters/appendix_b_cli_reference.md`
- **L3, L77 タイムスタンプ**: 「2026年3月時点」→ 4.7 登場後時点に更新
- **L35-46 モデルと推論** — 全面改訂:
  - L39 「最高精度: Opus 4.6」→ Opus 4.7
  - L40 「バランス: Sonnet 4.6」→ 現行 Sonnet バージョン確認（4.7 アナウンスなしの可能性）
  - L41 「高速・低コスト: Haiku 4.5」→ 現行 Haiku バージョン確認
  - L43 「推論の深さ: Extended Thinking (`Alt+T` / `Option+T`)」→ 「Adaptive Thinking（`Alt+T` / `Option+T` でトグル、4.7 は adaptive のみ）」
  - L44 「Opus 4.6: adaptive（自動調節）」→「Opus 4.7: adaptive のみ、デフォルト OFF、effort で強度制御」
  - L45 「Plan Mode + Extended Thinking」→「Plan Mode + Adaptive Thinking」
- **追加行候補**:
  - 「effort レベル」行: Claude Code CLI の UI で設定可能なら、Codex の Reasoning Effort と対応付け
  - 「Task budgets (beta)」行
- **参考文献追記**: `references/` 側で adaptive-thinking / effort / whats-new のエントリを追加

#### `chapters/glossary.md`
- **L187-191 コンテキストウィンドウ**: 1M が標準価格（long-context premium なし）を 1 文追加
- **L317-321 推論（Reasoning）** — 要刷新:
  - 「推論の深さをタスクの複雑さに応じて調整できる」の記述は維持しつつ、**Adaptive thinking による自動調節** と **effort レベルでのガイド** という新しい枠組みで書き直す
  - Interleaved thinking への言及（エージェント協働で推論がツール呼び出しの間にも走る）
- **L463-467 トークン**: 新トークナイザでモデル間でも同じテキストのトークン数が変動（Opus 4.7 は 4.6 比 1.0〜1.35x）と、max_tokens の余裕を持つべき旨を 1 文追加
- **追加候補**: 新規エントリ「**Adaptive thinking / Interleaved thinking / Effort**」の用語解説を追加

### 🟠 優先度: 中（挙動変化の反映）

#### `chapters/00_ai_agent.md` — §0-5 サブエージェントとタスク委譲
- **L601-609 付近**: 4.7 はサブエージェント生成を**抑制的**にする挙動。サブエージェント活用を推奨する記述と整合を取る（「4.7 以降は明示的に指示しないと自動分割されにくい」旨の 1 文）

#### `chapters/00_ai_agent.md` — §0-4 エージェントにレビューさせる
- Interleaved thinking の紹介と合わせ、レビュー用のサブエージェントやツール呼び出しとの相性を触れる余地あり（著者判断）

#### `chapters/00_ai_agent.md` — §0-8 AI 生成コードのアンチパターン集
- **L769-785 アンチパターン表**: 4.7 では「防御的すぎる例外処理」「過剰なコメント」「過剰な設定化」などがモデル側でも抑制される傾向。既存の指摘は削除せず、表の後に「Opus 4.7 以降はこれらの傾向が減り、低 effort ではむしろ最小限に倒れる。指示で必要なチェックは**明示列挙**すること」の注記を追加

#### `chapters/appendix_a_learning_patterns.md`
- **L3 タイムスタンプ**: 「2026年3月時点」→ 4.7 登場時点に
- **L71 「推論深度の調整」**: 表現を「effort レベルのコントロール」「adaptive thinking の自動調節」に寄せる

#### `chapters/appendix_d_agent_vocabulary.md`
- **L3 前書き**: 「Reasoning モードによって異なる」の表現を Adaptive thinking に合わせて正確化
- **L47-55 「Claude特有の傾向」**: 4.7 では「長文化しやすい」「安全側に倒す」「代替案を必ず出す」が**抑制**方向。表の下に注で「Opus 4.7 以降は 1〜4 行目の傾向が抑制される（効率化、より直接的、必要な指摘に絞る）」を追記
- **追加候補**: 「自発的な進捗報告」が新たな特徴として現れる点を触れる

### 🟡 優先度: 低（確認のみ、変更不要）

#### `chapters/19_database_api.md`
- **L567**: Biomni の例で `llm='claude-sonnet-4-20250514'`。Biomni 側の推奨モデルが追従していない可能性があるため、**変更不要**

#### `chapters/07_git.md`
- **L103**: サブエージェント並列実行への言及。git worktree の説明自体は 4.7 でも有効。**変更不要**

---

## 要確認事項（著者判断）

実装フェーズで判断が必要:

1. **モデルバージョン表記の方針**:
   - (A) Opus 4.6 → Opus 4.7 に一斉置換。Sonnet/Haiku は現行版（4.6 / 4.5）を維持
   - (B) すべて世代非依存（「最新 Opus」等）に寄せる
   - (C) 表記は今のまま、脚注で「Opus 4.7 登場後は…」と差分情報だけ追記
   - **推奨**: (A)。公式発表は Opus のみ 4.7、Sonnet/Haiku は現状維持

2. **§0-7 推論の深さの章立て**:
   - (A) 「Extended Thinking / Adaptive Thinking」のコラムで並記して移行史を残す
   - (B) Adaptive Thinking + effort に全面置換し、Extended Thinking は用語集で 1 行触れる
   - **推奨**: (B)。本書は「今どう使うか」が主目的、歴史の記述は用語集で十分

3. **ベンチマーク表（L697-705）の更新範囲**:
   - (A) 4.7 のスコアを調査して 3 行を差し替え
   - (B) 現行表を維持し、末尾に 4.7 登場の脚注
   - (C) 表を削除しリーダーボード URL に誘導
   - **推奨**: 著者指示待ち（公式スコアの有無に依存）

4. **§0-7 再現性節 L726 temperature 記述**:
   - (A) Ouyang et al. 引用を残しつつ「4.7 では temperature が廃止」を補注
   - (B) 温度の話を削り、「モデル側の非決定性」「モデル更新」「新トークナイザ」の 3 軸に集約
   - **推奨**: (A)。引用エビデンスは残す価値がある

5. **task budgets (beta) / `display: omitted` / Interleaved thinking の取扱い**:
   - (A) §0-7 本文に組み込み
   - (B) 付録B 対照表に行追加のみ
   - (C) コラム（🤖）で別項立て
   - **推奨**: 本文に Adaptive thinking と effort を組み込み、task budgets と display はコラムまたは脚注

6. **付録D「Claude特有の傾向」更新深度**:
   - (A) 既存行を残し、脚注で「Opus 4.7 以降は抑制傾向」と補足
   - (B) 4.7 挙動の新行を追加し、既存行には「〜4.6 までの傾向」と断る
   - **推奨**: (A)。表構造を保ったまま注で補足が安全

---

## 実装時の検証方法

1. **grep で残存チェック**:
   ```
   grep -rn "Opus 4\.[0-6]\|Sonnet 4\.[0-5]\|Haiku 4\.[0-4]" chapters/
   grep -rn "Extended Thinking\|extended thinking\|budget_tokens" chapters/
   grep -rn "temperature" chapters/
   grep -rn "2026年3月時点" chapters/
   ```
2. **相対リンク検証**: §0-7 のアンカー `#0-7-モデル選択推論の深さコスト意識` 等が維持されていること（目次・相互参照を壊さない）
3. **表の崩れ**: `appendix_b_cli_reference.md` の表は行追加時にアラインが崩れやすい。pandoc ビルド（`build/`）で HTML/PDF を出力し目視確認
4. **引用整合**:
   - `references/ch00.bib` に以下の Anthropic 公式ドキュメントを追加:
     - `whats-new-claude-4-7`
     - `adaptive-thinking`
     - `effort`
     - `task-budgets`
   - `references/ch00.bib` の既存 `extended-thinking` 引用（脚注12）を adaptive-thinking に差し替え
5. **演習・エージェント指示例の整合**:
   - §0-7 に演習がある場合、effort レベル指定の指示例に更新
   - 各章の「エージェントへの指示例」で thinking や effort に触れているものがないか最終確認

---

## 関連する既存ファイル（再利用/参照先）

- `references/ch00.bib` — Anthropic 公式ドキュメントの引用管理
- `CLAUDE.md` 執筆規約 — Markdown 記法（太字・数式）、引用番号形式、相互参照ルールに従う
- `README.md` 目次 — 節アンカーは目次の節番号に一致させる
- `TODO.md` — 本対応を TODO エントリとして追加する余地あり（著者判断）

---

## 次のステップ

この計画への承認後、実装フェーズでは:

1. 上記「要確認事項」の 6 点を先に詰める（AskUserQuestion か対話）
2. 🔴 高優先度の 4 ファイルから順に修正
3. 🟠 中優先度を修正
4. `references/ch00.bib` 更新
5. grep チェック → pandoc ビルド → 目視確認
