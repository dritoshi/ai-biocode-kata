# 執筆 TODO

## はじめに

## 各章へ
- [x] workflowの章にCWLについて書く
- [x] データのライセンス (creative commons とか)を記載する場所を決めて執筆する
- [x] doi自体の説明を加える。思想や定義、利用方法やその制限など
- [x] 科研費のデータ共有記載義務化始まったので、Zenodoなどのデータレポジトリの話をどこかに入れる
- [x] クラウドについての基礎知識をどこかにいれる。バイオインフォに関連あるサービスの仕組みやサービス内容(S3など)について記載する
- [x] AIエージェントで作ったSPA (single page application) のデプロイ先にみんな困るので GitHub pages や S3で static なファイルホスティングができるよという話を加える。アプリケーションの公開、クラウドかgitのあたりにいれる？
- [x] gitとgithubの違いについて誤解が生まれないように記載を修正する
- [x] 本書が前提とする知識を具体的に明記する。それらの知識を学ぶための教科書やドキュメントを記載する
- [x] git worktreeの仕組みやAIコーディングの関連 → §0-5と§7-1にブランチとの違いを補足追加
- [ ] jargonを減らせと指示することをどこかに書く
- [ ] 各コラム直前にHTMLアンカー (`<a id="..."></a>`) を挿入し、GitHubレンダリング版でもコラム単位でリンクできるようにする（レビュアー向け引用・読者ナビゲーション両用）

## 用語集と付録D
- [x] Codexがよく言う単語
  - [x] プランを立案中によく言う用語: do定義、explicit context
  - [x] その他頻出用語: scaffold, spike, happy path, guard clause, dry run, idempotent, regression, entrypoint, acceptance criteria
  - [ ] jargon

## 仕上げ
- [x] タイトルページのサブタイトルを検討する（現在: 「配列解析から機械学習まで、環境構築・テスト・設計・公開のベストプラクティス」）
- [ ] 上下巻に分けるか検討する。上下巻にする場合はそれぞれにはじめや付録などが必要になるか検討する。
- [x] roadmap.mdをアーカイブし、README.mdに目次+節構成を統合。統計表はdocs/chapter_stats.mdに分離

## PDF/EPUBデザイン
- [ ] §3-1のデータ構造表のカラム幅が不均等（1,2列目が狭く3,4列目が広い）。HTMLテーブルへの置換で対処
- [ ] drawio図のフォントサイズがA4想定で小さい。B5向けに再エクスポート
- [x] 章間リンクがPDF内で機能しない → fix-crossref.lua で統合PDF内部リンクに変換済み
- [ ] PDF 側の表で列幅が要素の文字列に比べて狭すぎる問題が複数の表にある (EPUB側はCSSで対応済み)。問題のある表の場所:
  - 1-10-1
  - 4-2
  - 5-1 (静的リンクと動的リンク)
  - 5.5 (pip install のアナロジーで理解する)
  - 5.5 (MCPサーバーの追加方法)
  - 7.3 (大規模データの共有 — Git LFS を超える選択肢)
  - 14.3 (コラム: 機械学習パイプラインのワークフロー管理)
  - 15.4 (4段階のスペクトラム)
  - 16.1 (キューとパーティション)
  - 16.2 (Slurmの基本コマンド)
  - 16.4. ストレージの使い分け
  - 17.1 (コラム: macOSでの環境確認 — BSDとLinuxの違い)
  - 19.0 (用語整理)
  - 19.0 (データアクセスの2つのアプローチ)
  - 19-2. (HTTPの仕組み — API利用に必要な最低限)
  - 20-1-2. (最小権限の原則)
  - 21-2-4 (ライセンス互換性)
  - 付録B (モデルと推論)
  - (カスタマイズ)

## レビュー
- [x] LLMによる剽窃をチェックする。引用を超えるレベルであればリライト、引用のレベルであれば適切な引用をする。iThenticateでチェックする
- [x] PDF/EPUB 生成の仕組みを作る
- [x] 人間にレビューを依頼する
- [x] 書影作成する
- [ ] xで公開

## 開発環境・再現性（コードサンプル）
- [x] Phase 1: ルート `pyproject.toml`（依存・§8のruff設定・pytest設定）と `uv.lock` を整備し、`uv sync` → `uv run pytest` でclone後に再現実行できるようにする。README に手順追記。`tests/ch06` のpip前提テストをpytest前提に修正（760 passed / 2 skipped）
- [x] Phase 2-a: 実CI（`.github/workflows/test.yml`）を追加し、push/PR で `uv sync` → `ruff check` → `pytest` を走らせる（uv ベース。`ch07/ci_minimal.yml` の実体化）
- [x] Phase 2-b: リポジトリ全体を ruff で通す（660→0）。tests は D（docstring）を per-file-ignores で除外、裏方ツール（scripts直下・review/）は D と E501 を除外（F等は維持）。教材サンプル・testsのロジック/行長は実修正。F821実バグ（ch13 seaborn_biodist の Path 未import）を本文準拠に修正。CI に ruff check ゲート追加済み
- [ ] Phase 2-c: `ruff format`（現状71ファイルが要整形）。掲載教材コードも整形対象になるため、本文との同期方針を決めてから実施。決定までCIゲートには入れない
- [ ] mypy 用の型スタブ（types-requests, pandas-stubs, types-PyYAML 等）を dev 依存に追加し、`uv run mypy scripts/` を通す。完了後 CI に mypy ゲート追加
- [ ] §8 に D グループの扱い（テストは per-file-ignores で docstring 必須を緩めるのが実務的、という両論）を加筆 ← repo の per-file-ignores と本文を整合させるため