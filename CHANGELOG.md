# Changelog

本書『AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法』のリリース履歴。
書式は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に準拠し、バージョニングは [Semantic Versioning](https://semver.org/lang/ja/) を用いる。

## [Unreleased]

### Known Issues
- PDF 出力で表の列幅が要素文字列に対して狭すぎる箇所が複数残存（§1-10-1, §4-2, §5-1, §5.5, §7.3, §14.3, §15.4, §16.x, §17.1, §19.x, §20-1-2, §21-2-4, 付録B 他。詳細は [TODO.md](./TODO.md) 参照）。EPUB 側は CSS で対応済み
- drawio 図のフォントサイズが A4 想定で小さく、B5 向け再エクスポートが必要
- 各コラム直前への HTML アンカー (`<a id="..."></a>`) 挿入（GitHub レンダリング版でのコラム単位リンク対応）が未実施
- 「jargon を減らせ」とエージェントに指示することの記述が未追加

## [0.4.0] — 2026-04-25

§0 の Claude Opus 4.7 / Codex GPT-5.5 世代対応、全章への演習問題（85問）と図表（P0/P1）追加、用語集拡充（65語）と付録D新設、PDF/EPUB ビルドパイプライン整備、表紙デザイン確定までを含む大規模アップデート。PDF/EPUB 成果物は表レイアウト問題が残存するためリリース対象外とする。

### Added
- §0 に Deep Research 活用サブセクション、TogoMCP コラム、ハーネスエンジニアリングコラム、ベンチマーク・スキャフォールド・再現性のサブセクションを追加
- §0-5 / §7-1 に git worktree とブランチの違いを補足
- §3-1 に Counter / defaultdict / heapq / bisect とバイオインフォ向けコラム
- §4 に FAIR 原則、データライセンス（CC0 / CC-BY / CC-BY-SA）、DOI 概念解説、機械学習・数値計算データフォーマットコラム
- §10 に Web アプリ・静的サイトのホスティングガイド（GitHub Pages / S3 等）
- §11 用語集に fallback / failover / failback / fault-tolerant
- §13 にゲノムトラック作成とブラウザ可視化の🧬コラム
- §14 に Snakemake / Nextflow と同水準の CWL 解説
- §16 に VPN/MFA コラム、クラウドコンピューティング基礎コラム、tmux エージェントセッションの注記
- §19 に S3/GCS 直接ダウンロード手段
- §20 に TRE / Terra / AnVIL コラム、KAKENHI DMP・JST/AMED/NEDO 要件・データレポジトリ選択ガイド
- 全22章に演習問題（合計85問）と「さらに学びたい読者へ」セクション
- 付録D（用語集）を新設し、用語集を65用語まで拡充
- 全章にエピグラフを追加
- 図表を多数追加: P0 図表11枚、P1 DIAG 15枚、P1 PLOT 5枚、SCREEN 4枚、§19 DB選択フローチャート他
- 著者プロフィール（`hajimeni.md` および `author.md`）と謝辞拡充
- 免責事項を `notice.md` として独立化、プライバシーポリシー記載
- 表紙・裏表紙デザイン（Phase 3、Black weight CJK フォント、`\includepdf` 統合）
- PDF ビルドパイプライン: pandoc + Eisvogel テンプレート、TeX Live 2026、HaranoAji、JetBrains Mono、絵文字 LaTeX 変換 Lua フィルタ、`fix-crossref.lua` による章間リンク修正
- KDP 向け統合 EPUB ビルドパイプライン、Vivliostyle PDF ビルド設定
- 文字数カウントスクリプトの全角対応・コード行カウント・読了時間推定機能
- README に CC BY-NC-ND 4.0 ライセンス表記、推定読了時間表

### Changed
- §0 と付録を Claude Opus 4.7 仕様に更新
- Codex CLI 関連記述を GPT-5.5 世代に更新し、Opus 4.7 ベンチマークを補強
- §0-2 Deep Research コラムを GPT-5.2 アップグレードに対応
- 節番号を全章 1-スタートに統一（§4-0→§4-1, §19-0→§19-1）
- Snakemake / Nextflow / CWL を統合された比較節に再構成
- Git と GitHub の区別を §7-2 で明確化
- 付録構成を旧 A〜D から新 A〜C に整理し、付録A を全面改稿、付録B をブラッシュアップ
- 「はじめに」にモデル・課金プランの変動と再現性への但し書きを追加
- README を新タイトル・新サブタイトルに合わせて更新

### Fixed
- §4 Oct4 コラムの科学表記誤変換を修正、引用[7] を一次ソースに差し替え
- §3 引用[13] の重複を解消（Altschul を [14] に再番号付けしカスケード修正）
- ハーネスエンジニアリングコラムの太字レンダリング不具合
- §3・§12 のカッコ内 URL のリンク崩れ
- 「さらに学びたい読者へ」セクション内の URL 表記とハイパーリンク不足
- BiopythonDeprecationWarning と関連テスト不備（MANUAL-0006〜0009）
- §0 承認モード図の日本語文字化け（英語テキスト化）
- §17 プロファイリング図の矢印文字、Amdahl 図のアノテーション位置

### Removed
- 旧 `roadmap.md`（README.md 目次に統合、統計表は `docs/chapter_stats.md` へ分離）
- `AGENTS.md` 実体（`CLAUDE.md` へのシンボリックリンクに置換）
- Phase 1 ビルドファイル群（Eisvogel 移行に伴い `archive/` へ）

## [0.3.0-alpha] — 2026-03-23

タグ: `v0.3-alpha-release`

最初のアルファリリース。図表検討タスクの整理と `private/` ディレクトリの非追跡化。

## [0.2.0] — 2026-03-22

タグ: `v0.2-new-titles`

新タイトル・新構成への移行。README / TODO / CLAUDE.md / docs の旧タイトル参照を新構成に更新。

## [0.1.0] — 2026-03-22

タグ: `v0.1-old-structure`

旧構成での初期スナップショット。カリキュラム分析ファイルを `docs/` に整理し、残タスクを `TODO.md` に集約。

[Unreleased]: https://github.com/dritoshi/ai-biocode-kata/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/dritoshi/ai-biocode-kata/compare/v0.3-alpha-release...v0.4.0
[0.3.0-alpha]: https://github.com/dritoshi/ai-biocode-kata/compare/v0.2-new-titles...v0.3-alpha-release
[0.2.0]: https://github.com/dritoshi/ai-biocode-kata/compare/v0.1-old-structure...v0.2-new-titles
[0.1.0]: https://github.com/dritoshi/ai-biocode-kata/releases/tag/v0.1-old-structure
