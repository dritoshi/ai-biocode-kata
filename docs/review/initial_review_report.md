# 原稿レビュー初回監査レポート

## 概要

- 対象ファイル数: 31
- 参照レジストリ件数: 2212
- 現在の指摘件数: 26
- 重大度内訳: S=0, A=0, B=26, C=0

## 指摘カテゴリ内訳

| カテゴリ | 件数 |
|---|---:|
| chapter_reference_missing_in_bib | 26 |

## 章別サマリ

| 章 | 外部参照 | ローカルリンク | 壊れたリンク | 壊れたアンカー | 破損URL | パス参照問題 |
|---|---:|---:|---:|---:|---:|---:|
| 00_ai_agent.md | 173 | 69 | 0 | 0 | 0 | 0 |
| 01_design.md | 23 | 15 | 0 | 0 | 0 | 0 |
| 02_terminal.md | 18 | 10 | 0 | 0 | 0 | 0 |
| 03_cs_basics.md | 47 | 10 | 0 | 0 | 0 | 0 |
| 04_data_formats.md | 48 | 16 | 0 | 0 | 0 | 0 |
| 05_software_components.md | 15 | 36 | 0 | 0 | 0 | 0 |
| 06_dev_environment.md | 23 | 8 | 0 | 0 | 0 | 0 |
| 07_git.md | 50 | 17 | 0 | 0 | 0 | 0 |
| 08_testing.md | 36 | 30 | 0 | 0 | 0 | 0 |
| 09_debug.md | 19 | 25 | 0 | 0 | 0 | 0 |
| 10_deliverables.md | 37 | 26 | 0 | 0 | 0 | 0 |
| 11_cli.md | 27 | 12 | 0 | 0 | 0 | 0 |
| 12_data_processing.md | 22 | 41 | 0 | 0 | 0 | 0 |
| 13_visualization.md | 29 | 27 | 0 | 0 | 0 | 0 |
| 14_workflow.md | 33 | 21 | 0 | 0 | 0 | 0 |
| 15_container.md | 52 | 42 | 0 | 0 | 0 | 0 |
| 16_hpc.md | 20 | 19 | 0 | 0 | 0 | 0 |
| 17_performance.md | 25 | 30 | 0 | 0 | 0 | 0 |
| 18_documentation.md | 31 | 24 | 0 | 0 | 0 | 0 |
| 19_database_api.md | 55 | 26 | 0 | 0 | 0 | 0 |
| 20_security_ethics.md | 92 | 20 | 0 | 0 | 0 | 0 |
| 21_collaboration.md | 33 | 28 | 0 | 0 | 0 | 0 |
| appendix_a_learning_patterns.md | 21 | 12 | 0 | 0 | 0 | 0 |
| appendix_b_cli_reference.md | 11 | 5 | 0 | 0 | 0 | 0 |
| appendix_c_checklist.md | 0 | 27 | 0 | 0 | 0 | 0 |
| appendix_d_agent_vocabulary.md | 1 | 2 | 0 | 0 | 0 | 0 |
| appendix_e_column_index.md | 0 | 88 | 0 | 0 | 0 | 0 |
| author.md | 6 | 0 | 0 | 0 | 0 | 0 |
| glossary.md | 0 | 101 | 0 | 0 | 0 | 0 |
| hajimeni.md | 94 | 3 | 0 | 0 | 0 | 0 |
| notice.md | 0 | 4 | 0 | 0 | 0 | 0 |

## 優先対応候補（先頭20件）

- `AUTO-0001` [B] 03_cs_basics.md:863 `chapter_reference_missing_in_bib`: https://www.unicode.org/versions/Unicode17.0.0/
- `AUTO-0002` [B] 04_data_formats.md:902 `chapter_reference_missing_in_bib`: https://creativecommons.org/licenses/
- `AUTO-0003` [B] 04_data_formats.md:904 `chapter_reference_missing_in_bib`: https://www.doi.org/
- `AUTO-0004` [B] 13_visualization.md:742 `chapter_reference_missing_in_bib`: https://doi.org/10.1371/journal.pbio.1002128
- `AUTO-0005` [B] 16_hpc.md:810 `chapter_reference_missing_in_bib`: https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/
- `AUTO-0006` [B] 16_hpc.md:811 `chapter_reference_missing_in_bib`: https://www.cloudskillsboost.google/
- `AUTO-0007` [B] 19_database_api.md:977 `chapter_reference_missing_in_bib`: https://www.ncbi.nlm.nih.gov/sra/docs/sra-cloud/
- `AUTO-0008` [B] 19_database_api.md:978 `chapter_reference_missing_in_bib`: https://docs.aws.amazon.com/cli/
- `AUTO-0009` [B] 20_security_ethics.md:851 `chapter_reference_missing_in_bib`: https://www.mext.go.jp/content/20210608-mxt_jyohoka01-000015787_06.pdf
- `AUTO-0010` [B] 20_security_ethics.md:853 `chapter_reference_missing_in_bib`: https://www.jst.go.jp/all/about/houshin.html
- `AUTO-0011` [B] 20_security_ethics.md:855 `chapter_reference_missing_in_bib`: https://www.amed.go.jp/koubo/datamanagement.html
- `AUTO-0012` [B] 20_security_ethics.md:857 `chapter_reference_missing_in_bib`: https://www.nedo.go.jp/jyouhoukoukai/other_CA_00003.html
- `AUTO-0013` [B] 20_security_ethics.md:859 `chapter_reference_missing_in_bib`: https://ukhealthdata.org/wp-content/uploads/2020/04/200430-TRE-Green-Paper-v1.pdf
- `AUTO-0014` [B] 20_security_ethics.md:861 `chapter_reference_missing_in_bib`: https://terra.bio/
- `AUTO-0015` [B] 20_security_ethics.md:863 `chapter_reference_missing_in_bib`: https://anvilproject.org/
- `AUTO-0016` [B] 20_security_ethics.md:865 `chapter_reference_missing_in_bib`: https://www.cancergenomicscloud.org/
- `AUTO-0017` [B] 20_security_ethics.md:867 `chapter_reference_missing_in_bib`: https://ukbiobank.dnanexus.com/
- `AUTO-0018` [B] 20_security_ethics.md:869 `chapter_reference_missing_in_bib`: https://www.ddbj.nig.ac.jp/services/ddbj-group-cloud.html
- `AUTO-0019` [B] hajimeni.md:165 `chapter_reference_missing_in_bib`: https://docs.python.org/ja/3/tutorial/
- `AUTO-0020` [B] hajimeni.md:166 `chapter_reference_missing_in_bib`: https://utokyo-ipp.github.io/

## 次のアクション

- 26件は本文に掲載済みの参考URLと BibTeX 台帳の同期候補であり、リンク切れや引用欠落ではない。
- 本文・参考文献の内容改訂とは分離し、`master_issue_log.csv` で後続の書誌正規化候補として管理する。
- 原稿更新後に再レビューする場合は `build_review_artifacts.py` と URL チェックを再実行する。
