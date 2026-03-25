# 原稿レビュー台帳

本ディレクトリは『AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法』の出版前レビューを、章単位かつ再実行可能な形で管理するための台帳である。

## 生成物

- `chapter_review_sheet.csv`: 章ごとのレビュー進捗、観点別担当、機械監査の件数
- `master_issue_log.csv`: 修正すべき問題の一覧。重大度、根拠、修正方針を記録する
- `reference_registry.csv`: URL・外部参照・ローカル参照の台帳
- `section_inventory.csv`: 見出しとアンカーの棚卸し
- `initial_review_report.md`: 初回自動監査の要約

## 更新方法

```bash
python3 scripts/build_review_artifacts.py
```

テスト結果も台帳に反映したい場合は、pytest のログを渡す。

```bash
./.venv/bin/pytest -q > /tmp/ai-biocode-kata-pytest.log 2>&1
python3 scripts/build_review_artifacts.py --pytest-log /tmp/ai-biocode-kata-pytest.log
```

## 運用方針

- `master_issue_log.csv` の `severity=A` を出版前の必須修正とする
- URL・固有名詞・数値比較は `reference_registry.csv` を起点に一次情報で裏取りする
- 生命科学、情報科学、計算機科学、バイオインフォマティクス、実装実務の各観点で `chapter_review_sheet.csv` を埋める
- レビューコメントは感想ではなく、`問題 / 根拠 / 修正案` の形式で残す
