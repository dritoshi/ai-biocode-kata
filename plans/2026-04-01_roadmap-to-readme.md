# roadmap.md → README.md 移行 + AGENTS.md統合

実施日: 2026-04-01
状態: 完了

## 目的

roadmap.md（2028行）のメンテナンスコストを解消し、書籍の全体構造をREADME.mdで一元管理する。AGENTS.mdとCLAUDE.mdの重複も解消する。

## 検討した3案

| | A. アーカイブ | B. 現状維持 | C. Essential版 |
|---|---|---|---|
| メンテコスト | ゼロ | 高い | 低い |
| トークン効率 | 悪い（20万+） | 良い（8000） | 最良（1000） |
| 採用 | — | — | ✅ |

## 実施内容

1. **README.md**: 章テーブルを目次+節構成リストに書き換え。統計表は別ファイルにリンク
2. **docs/chapter_stats.md**: 読了時間+文字数の統合テーブルを新規作成
3. **chapters/roadmap.md**: `docs/archive/roadmap-2026-04-01.md` にアーカイブ
4. **CLAUDE.md**: roadmap.md参照をREADME.md参照に更新
5. **AGENTS.md**: CLAUDE.mdへのシンボリックリンクに置き換え（55行の重複解消）
