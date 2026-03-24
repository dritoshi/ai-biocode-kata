# 図表計画: 全章の図表・スクリーンショット追加リスト

## Context

本書『AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法』は全22章+付録の初稿が完成しているが、図表はほぼ未整備（既存PNG 1枚、ASCII art 8箇所、Mermaid 6箇所のみ）。プログラミング初心者の実験系生命科学者が対象読者であり、視覚的な理解支援は特に重要。本計画では、各章に追加すべき図表を優先度付きでリストアップし、作成方法と実装順序を定める。

---

## 図の作成ツールと方針

### 出版品質を最優先とするツール選定

| 種別 | 推奨ツール | 理由 |
|------|-----------|------|
| **DIAG（概念図・フローチャート）** | **draw.io MCP** | レイアウト・色・フォントを完全制御でき出版品質が最も高い。`.drawio` ソースで再編集可能 |
| **PLOT（コード出力グラフ）** | **matplotlib / seaborn** | 書籍内コード例の出力そのものであり、スクリプト実行で再現可能 |
| **SCREEN（スクリーンショット）** | **手動キャプチャ + draw.io アノテーション** | 実際の画面を示しつつ、draw.io で矢印・ラベルを追加 |

**Mermaidを使わない理由**: Mermaidはレイアウト制御が限定的で、フォントサイズ・配色・間隔の微調整ができない。EPUB/PDF変換時に別途レンダリングが必要になる問題もある。出版品質を重視し、全DIAG図をdraw.ioに統一する。

### draw.io MCP セットアップ

**公式パッケージ**: `jgraph/drawio-mcp`（無料・オープンソース）
- npm: `@drawio/mcp`
- 依存: `@modelcontextprotocol/sdk`, `pako`
- Node.js 18+ が必要

**Claude Code CLI への設定方法**:

```bash
# 方法1: CLIコマンドで追加
claude mcp add drawio -- npx -y @drawio/mcp

# 方法2: settings.json に手動追加
```

settings.json に追加する場合:
```json
{
  "mcpServers": {
    "drawio": {
      "command": "npx",
      "args": ["-y", "@drawio/mcp"]
    }
  }
}
```

**提供ツール（3つ）**:
1. `open_drawio_xml` — draw.io XML を渡してエディタで開く
2. `open_drawio_csv` — CSV/表形式データから図を生成
3. `open_drawio_mermaid` — Mermaid構文をdraw.io図に変換

**エクスポート**:
- `.drawio.png`（PNG + 埋め込みXMLで再編集可能）
- `.drawio.svg`（SVG + 埋め込みXML）
- PDF
- スケールパラメータ対応（`-s 2` で2倍解像度）

**ワークフロー**:
1. Claude Code が draw.io MCP 経由で `.drawio` XML を生成
2. draw.io Desktop または Web で開いてレイアウト微調整
3. PNG/SVG にエクスポートして `figures/` に保存
4. `.drawio` ソースファイルは `figures/drawio-src/` に保管（再編集用）

### 図の種別

| コード | 種別 | 作成方法 |
|--------|------|---------|
| PLOT | コード出力プロット | `scripts/` のPythonスクリプト実行 → `figures/` に保存 |
| DIAG | 概念図・フローチャート | draw.io MCP で生成 → draw.io Desktop で微調整 → PNG/SVG エクスポート |
| SCREEN | スクリーンショット | 手動キャプチャ + draw.io でアノテーション追加 |

### 優先度

| 優先度 | 基準 |
|--------|------|
| **P0** | テキストだけでは理解が困難、または章の核心概念の視覚化。出版前に必須 |
| **P1** | 理解を大幅に促進するが、テキストだけでも成立。出版前に可能な限り作成 |
| **P2** | 見栄えの向上、補助的な図。時間が許せば作成 |

---

## 章別の図表リスト

### Phase I: AIと始めるプログラミングの基礎

#### §0 AIエージェントにコードを書かせる

既存: `figures/ch00_orf_comparison.png`（ORF比較3パネル図、生成済み）

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-00-01 | P1 | DIAG | Plan→Execute→Reviewワークフロー | 4フェーズ(Explore/Plan/Execute/Commit)のフロー図。現在ASCII art (L241-258) | draw.io |
| fig-00-02 | P2 | SCREEN | 承認モードの動作画面 | 「承認あり」モードでファイル編集許可を求める画面 | 手動キャプチャ |

#### §1 設計原則 — 良いコードとは何か

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-01-01 | P1 | DIAG | 関心の分離 — 3層パイプライン構造 | 入力→処理→出力の分離を図示。UNIX哲学のパイプ接続も含む | draw.io |

#### §2 ターミナルとシェルの基本操作

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-02-01 | P1 | DIAG | PATHの検索順序 | `python`入力→PATHディレクトリを左から順に検索→マッチしたら実行 | draw.io |
| fig-02-02 | P1 | DIAG | パイプチェーンのデータ変換 | `grep \| awk \| sort \| uniq` でデータが各段階でどう変形するか | draw.io |

※ファイルシステムツリー (L61-71) は ASCII art のまま維持（Monospace前提で十分）

#### §3 コーディングに必要な計算機科学

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-03-01 | **P0** | PLOT | O記法の成長曲線 | $O(1), O(\log n), O(n), O(n \log n), O(n^2)$ を1グラフに重ねる。「$O(n^2)$がいかに危険か」を視覚化 | 新規 `scripts/ch03/plot_complexity.py` |
| fig-03-02 | P1 | PLOT | list vs set ベンチマーク棒グラフ | 検索速度の桁違いの差を棒グラフで視覚化 | 新規 `scripts/ch03/plot_bench.py` |

#### §4 データフォーマットの選び方

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-04-01 | P1 | DIAG | tidy data変換の概念図 | wide format → melt → tidy (long) format の変換を矢印付き表で示す | draw.io |

#### §5 ソフトウェアの構成要素

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-05-01 | P1 | DIAG | コンパイル→リンク→実行フロー | ソースコード→オブジェクト→実行ファイルの流れ。共有ライブラリ依存も含む | draw.io |

※MCPアーキテクチャ図 (L534-538) は ASCII art のまま維持（小さくシンプル）

#### §6 Python環境の構築

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-06-01 | P1 | DIAG | 環境管理ツールの責務範囲 | pyenv/venv/pip/conda/uvの担当領域を横並びで示す | draw.io |

---

### Phase II: 信頼できるコードを育てる技術

#### §7 Git入門

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-07-01 | **P0** | DIAG | Working Dir → Staging → Repository | Gitの3ステージ概念図。Git初心者にとって最重要の図 | draw.io |
| fig-07-02 | P1 | DIAG | ブランチとマージの概念図 | mainからfeatureブランチを切り、マージする流れ | draw.io |

#### §8 コードの正しさを守るテスト技法

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-08-01 | **P0** | DIAG | Red → Green → Refactor サイクル | TDDの循環図。テスト章の核心概念 | draw.io |
| fig-08-02 | P1 | DIAG | CI/CDパイプライン | push→テスト自動実行→リント→カバレッジの流れ | draw.io |

※フック処理フロー (L539-547) は ASCII art のまま維持

#### §9 デバッグの技術

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-09-01 | P1 | SCREEN | Tracebackの読み方（アノテーション付き） | 実際のtraceback出力に「ファイル名」「行番号」「エラー種別」を矢印で図示 | スクリーンショット + draw.io アノテーション |

#### §10 ソフトウェア成果物の設計

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-10-01 | P1 | DIAG | 成果物パターン選択フローチャート | 「一回きりの解析か？」→判断分岐→適切なパターン | draw.io |
| fig-10-02 | P1 | DIAG | 段階的成長パス | スクリプト→パッケージ→公開の成長図。現在ASCII art (L893-905) | draw.io |

#### §11 コマンドラインツールの設計と実装

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-11-01 | P2 | SCREEN | プログレスバーとロギング出力 | tqdmプログレスバーの表示例とloggingの色分け出力例 | 手動スクリーンショット |

---

### Phase III: データを扱うコードを書く

#### §12 データ処理の実践

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-12-01 | P1 | PLOT | ベクトル化 vs forループ性能比較 | 処理時間の棒グラフ。ch12の核心メッセージ | 新規 `scripts/ch12/plot_vectorize_bench.py` |
| fig-12-02 | P1 | DIAG | tidy dataへの変換 (melt操作) | wide format→long formatの変換をbefore/afterの表で示す | draw.io |

#### §13 可視化の実践 ★最重要章

**全プロット例にPNG出力を付ける（可視化を教える章に図がないのは致命的）**

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-13-01 | **P0** | PLOT | GC含量ヒストグラム | matplotlibの明示的APIサンプル出力 | 既存 `scripts/ch13/matplotlib_bindist.py` 実行 |
| fig-13-02 | **P0** | PLOT | Volcano plot | DEG解析の定番可視化（赤=上昇、青=減少、灰=非有意） | 既存 `scripts/ch13/bio_plots.py` の `volcano_plot()` 実行 |
| fig-13-03 | **P0** | PLOT | ヒートマップ+デンドログラム | クラスタリング付き発現量ヒートマップ | 既存 `scripts/ch13/bio_plots.py` の `expression_heatmap()` 実行 |
| fig-13-04 | **P0** | PLOT | バイオリンプロット | seaborn + tidy dataの発現量分布 | 既存 `scripts/ch13/seaborn_biodist.py` 実行 |
| fig-13-05 | P1 | PLOT | Plotly Volcano plot（静止画） | インタラクティブ版の書籍用静止画。ホバー情報のコールアウト付き | plotly → PNG export |
| fig-13-06 | **P0** | DIAG | グラフ種類選択フローチャート | テキスト内表 (L296-303) を意思決定木に図版化 | draw.io |
| fig-13-07 | P1 | PLOT | カラーマップ比較 | viridis/cividis/jet/rainbow を並べ、色覚シミュレーションとの差を示す | 新規 `scripts/ch13/plot_colormap_comparison.py` |
| fig-13-08 | P1 | PLOT | ゲノムトラック可視化 (pyGenomeTracks) | 🧬コラム内のゲノムブラウザ風プロット出力例 | 新規または既存スクリプト |

#### §14 解析パイプラインの自動化

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-14-01 | **P0** | DIAG | ワークフローDAG | RNA-seqパイプラインの有向非巡回グラフ。現在ASCII art (L62-64)。DAGの概念を教える場面で正式な図が必要 | draw.io |
| fig-14-02 | P1 | DIAG | Snakemakeワイルドカード展開 | テンプレート `{sample}` が SAMPLES リストで展開される様子 | draw.io |

---

### Phase IV: ソフトウェア再現性と大規模計算

#### §15 コンテナによるソフトウェア環境の再現

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-15-01 | **P0** | DIAG | VM vs コンテナ アーキテクチャ比較 | 層構造の違いを示す並列図。現在ASCII art (L71-81)。初心者がコンテナを理解する最重要図 | draw.io |
| fig-15-02 | P1 | DIAG | Dockerfile → Image → Container フロー | 3段階の変換。現在ASCII (L114) | draw.io |
| fig-15-03 | P1 | DIAG | レイヤーキャッシュの最適化 | 悪い順序 vs 良い順序で再ビルド時間がどう変わるか | draw.io |

#### §16 スパコン・クラスタでの大規模計算

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-16-01 | **P0** | DIAG | HPCクラスタアーキテクチャ | ローカルPC→ログインノード→スケジューラ→計算ノード群→共有FS。現在ASCII art (L18-35) | draw.io |

#### §17 コードのパフォーマンス改善

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-17-01 | P1 | PLOT | Amdahlの法則グラフ | ボトルネック割合 $p$ と高速化率 $s$ から全体高速化率をプロット | 新規 `scripts/ch17/plot_amdahl.py` |
| fig-17-02 | P1 | PLOT | プロファイリング結果の可視化 | 関数別処理時間の棒グラフ（ボトルネック特定） | 新規スクリプトまたはsnakeviz出力のスクリーンショット |

---

### Phase V: 共有のためのコード整備

#### §18 コードのドキュメント化

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-18-01 | P1 | SCREEN | Mermaidレンダリング結果 | Mermaidソースと、GitHub上でレンダリングされた図の並列表示 | GitHubスクリーンショット |

#### §19 公共データベースとAPI

| ID | P | 種別 | タイトル | 説明 | 作成方法 |
|----|---|------|---------|------|---------|
| fig-19-01 | P1 | DIAG | DB選択フローチャート | データ種類→適切なDBの決定木。現在ASCII tree (L242-250) | draw.io |

#### §20 セキュリティ・倫理 / §21 共同開発 / 付録A-D

図の必要性が低い。テキスト+既存の表で十分。

---

## 優先度別の集計

| 優先度 | 図数 | 該当ID |
|--------|------|--------|
| **P0 (必須)** | **11** | fig-03-01, fig-07-01, fig-08-01, fig-13-01, fig-13-02, fig-13-03, fig-13-04, fig-13-06, fig-14-01, fig-15-01, fig-16-01 |
| **P1 (推奨)** | **21** | fig-00-01, fig-01-01, fig-02-01, fig-02-02, fig-03-02, fig-04-01, fig-05-01, fig-06-01, fig-07-02, fig-08-02, fig-09-01, fig-10-01, fig-10-02, fig-12-01, fig-12-02, fig-13-05, fig-13-07, fig-13-08, fig-14-02, fig-15-02, fig-15-03, fig-17-01, fig-17-02, fig-18-01, fig-19-01 |
| **P2 (あれば良い)** | **2** | fig-00-02, fig-11-01 |
| **合計** | **34** | |

※ ASCII art のまま維持: 5箇所（§2 ファイルシステムツリー、§5 MCP図、§8 フック処理フロー、§19 URL構造図、§2 パーミッション文字列）

---

## 作成方法別の集計

| 方法 | 図数 | ツール | 対象 |
|------|------|--------|------|
| 既存スクリプト実行 | 4 | matplotlib/seaborn | fig-13-01〜04 |
| 新規Pythonスクリプト | 7 | matplotlib | fig-03-01, fig-03-02, fig-12-01, fig-13-07, fig-13-08, fig-17-01, fig-17-02 |
| **draw.io MCP** | **20** | draw.io MCP → Desktop微調整 → PNG/SVG | 全DIAG図（fig-00-01, fig-01-01, fig-02-01, fig-02-02, fig-04-01, fig-05-01, fig-06-01, fig-07-01, fig-07-02, fig-08-01, fig-08-02, fig-10-01, fig-10-02, fig-12-02, fig-13-06, fig-14-01, fig-14-02, fig-15-01, fig-15-02, fig-15-03, fig-16-01, fig-19-01） |
| スクリーンショット | 3 | OS標準 + draw.io アノテーション | fig-00-02, fig-09-01, fig-11-01 |

---

## ファイル命名規則

```
figures/
├── ch00_orf_comparison.png          # 既存
├── ch03_complexity_growth.png       # fig-03-01
├── ch07_git_three_stages.png        # fig-07-01 (draw.ioからエクスポート)
├── ch08_tdd_cycle.png               # fig-08-01
├── ch13_gc_histogram.png            # fig-13-01
├── ch13_volcano_plot.png            # fig-13-02
├── ch13_expression_heatmap.png      # fig-13-03
├── ch13_violin_plot.png             # fig-13-04
├── ch13_graph_type_decision.png     # fig-13-06
├── ch14_workflow_dag.png            # fig-14-01
├── ch15_vm_vs_container.png         # fig-15-01
├── ch16_hpc_architecture.png        # fig-16-01
├── ...
└── drawio-src/                      # draw.ioソースファイル（再編集用）
    ├── ch07_git_three_stages.drawio
    ├── ch08_tdd_cycle.drawio
    └── ...
```

パターン: `ch{NN}_{snake_case_description}.{png|svg}`
ソース: `drawio-src/ch{NN}_{snake_case_description}.drawio`

---

## 実装フェーズ

### フェーズ0: 環境セットアップ
1. draw.io MCP をClaude Codeに設定: `claude mcp add drawio -- npx -y @drawio/mcp`
2. draw.io Desktop がインストール済みか確認（微調整・エクスポート用）
3. `figures/drawio-src/` ディレクトリを作成

### フェーズA: P0の11図（最優先）
1. ch13のプロット出力 (4図) — テストデータ生成ヘルパー作成、既存スクリプト3本を実行してPNG保存
2. 新規PLOTスクリプト (1図) — `scripts/ch03/plot_complexity.py`
3. draw.io DIAG図 (4図) — fig-07-01, fig-08-01, fig-13-06, fig-14-01
4. draw.io DIAG図 (2図) — fig-15-01, fig-16-01

### フェーズB: P1の21図（出版前）
5. 残りの draw.io 図の作成
6. 残りの新規PLOTスクリプトの作成と実行
7. スクリーンショットの撮影とアノテーション

### フェーズC: P2の2図（時間があれば）
8. 補助的スクリーンショット

---

## 検証方法

1. 各PLOTスクリプトを実行し、`figures/` にPNGが生成されることを確認
2. 各 `.drawio` ファイルが draw.io Desktop で開けること、PNG/SVGエクスポートが正常なことを確認
3. 各章のMarkdownに `![...]` 参照を挿入し、GitHub上でプレビュー表示されることを確認
4. `ls figures/ | wc -l` でファイル数を確認（最終目標: P0完了時 12枚、全完了時 35枚）
