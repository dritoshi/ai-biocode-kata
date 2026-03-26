# 原稿レビュー初回監査レポート

## 概要

- 対象ファイル数: 29
- 参照レジストリ件数: 1562
- 現在の指摘件数: 4
- 重大度内訳: S=0, A=0, B=1, C=3

## 指摘カテゴリ内訳

| カテゴリ | 件数 |
|---|---:|
| test_coverage_gap | 3 |
| test_warning_future_breakage | 1 |

## 章別サマリ

| 章 | 外部参照 | ローカルリンク | 壊れたリンク | 壊れたアンカー | 破損URL | パス参照問題 |
|---|---:|---:|---:|---:|---:|---:|
| 00_ai_agent.md | 46 | 39 | 0 | 0 | 0 | 0 |
| 01_design.md | 24 | 9 | 0 | 0 | 0 | 0 |
| 02_terminal.md | 14 | 10 | 0 | 0 | 0 | 0 |
| 03_cs_basics.md | 46 | 8 | 0 | 0 | 0 | 0 |
| 04_data_formats.md | 38 | 12 | 0 | 0 | 0 | 0 |
| 05_software_components.md | 14 | 36 | 0 | 0 | 0 | 0 |
| 06_dev_environment.md | 22 | 8 | 0 | 0 | 0 | 0 |
| 07_git.md | 38 | 13 | 0 | 0 | 0 | 0 |
| 08_testing.md | 23 | 16 | 0 | 0 | 0 | 0 |
| 09_debug.md | 18 | 15 | 0 | 0 | 0 | 0 |
| 10_deliverables.md | 23 | 18 | 0 | 0 | 0 | 0 |
| 11_cli.md | 25 | 11 | 0 | 0 | 0 | 0 |
| 12_data_processing.md | 16 | 14 | 0 | 0 | 0 | 0 |
| 13_visualization.md | 29 | 21 | 0 | 0 | 0 | 0 |
| 14_workflow.md | 23 | 11 | 0 | 0 | 0 | 0 |
| 15_container.md | 26 | 33 | 0 | 0 | 0 | 0 |
| 16_hpc.md | 12 | 14 | 0 | 0 | 0 | 0 |
| 17_performance.md | 22 | 16 | 0 | 0 | 0 | 0 |
| 18_documentation.md | 29 | 21 | 0 | 0 | 0 | 0 |
| 19_database_api.md | 50 | 23 | 0 | 0 | 0 | 0 |
| 20_security_ethics.md | 36 | 13 | 0 | 0 | 0 | 0 |
| 21_collaboration.md | 26 | 17 | 0 | 0 | 0 | 0 |
| appendix_a_learning_patterns.md | 9 | 12 | 0 | 0 | 0 | 0 |
| appendix_b_cli_reference.md | 4 | 5 | 0 | 0 | 0 | 0 |
| appendix_c_checklist.md | 0 | 27 | 0 | 0 | 0 | 0 |
| appendix_d_agent_vocabulary.md | 0 | 1 | 0 | 0 | 0 | 0 |
| glossary.md | 0 | 90 | 0 | 0 | 0 | 0 |
| hajimeni.md | 37 | 2 | 0 | 0 | 0 | 0 |
| roadmap.md | 1 | 101 | 0 | 0 | 0 | 0 |

## 優先対応候補（先頭20件）

- `MANUAL-0006` [B] tests/ch10/test_error_handling.py:58 `test_warning_future_breakage`: BiopythonDeprecationWarning による将来破壊の可能性
- `MANUAL-0007` [C] scripts/ch05/mylib/core.py:1 `test_coverage_gap`: ch05 ライブラリ内部モジュールの未カバー
- `MANUAL-0008` [C] scripts/ch05/mylib/utils.py:1 `test_coverage_gap`: ch05 ライブラリ内部モジュールの未カバー
- `MANUAL-0009` [C] scripts/ch11/cli_argparse.py:1 `test_coverage_gap`: argparse 版 CLI デモの未カバー

## 次のアクション

- 残件は B/C 指摘のみである。warning 対応とテスト方針の確定を優先する。
- `master_issue_log.csv` の残件を閉じるため、必要ならテスト追加または受容理由の明文化を行う。
- `chapter_review_sheet.csv` の手動レビュー状態を維持しつつ、残件クローズ後に再確認する。
