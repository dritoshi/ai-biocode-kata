# 原稿レビュー初回監査レポート

## 概要

- 対象ファイル数: 29
- 参照レジストリ件数: 1546
- 現在の指摘件数: 9
- 重大度内訳: S=0, A=5, B=1, C=3

## 指摘カテゴリ内訳

| カテゴリ | 件数 |
|---|---:|
| stale_external_reference | 5 |
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

- `MANUAL-0002` [A] 16_hpc.md:700 `stale_external_reference`: Australian BioCommons HPC ガイドの旧URL
- `MANUAL-0001` [A] references/ch04.bib:150 `stale_external_reference`: CrowdFlower 2016 Data Science Report の旧 Figure Eight URL
- `MANUAL-0003` [A] references/ch16.bib:52 `stale_external_reference`: CISA 参考文献の旧URL
- `MANUAL-0004` [A] references/ch16.bib:59 `stale_external_reference`: Australian BioCommons HPC ガイドの旧URL
- `MANUAL-0005` [A] references/ch17.bib:41 `stale_external_reference`: memory_profiler の旧 GitHub URL
- `MANUAL-0006` [B] tests/ch10/test_error_handling.py:58 `test_warning_future_breakage`: BiopythonDeprecationWarning による将来破壊の可能性
- `MANUAL-0007` [C] scripts/ch05/mylib/core.py:1 `test_coverage_gap`: ch05 ライブラリ内部モジュールの未カバー
- `MANUAL-0008` [C] scripts/ch05/mylib/utils.py:1 `test_coverage_gap`: ch05 ライブラリ内部モジュールの未カバー
- `MANUAL-0009` [C] scripts/ch11/cli_argparse.py:1 `test_coverage_gap`: argparse 版 CLI デモの未カバー

## 次のアクション

- `master_issue_log.csv` の A 指摘から順に修正する。
- `reference_registry.csv` を使い、外部URLと固有名詞の一次情報確認を進める。
- 生命科学・情報科学・計算機科学・バイオインフォ・実装実務の各観点で `chapter_review_sheet.csv` を埋める。
