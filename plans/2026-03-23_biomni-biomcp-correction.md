# バイオ向けMCP・Biomni情報の修正

## Context

§0と§19に「bioomni」と記載したが、これは不正確。正しくは以下の2つの別プロジェクト:
- **Biomni**（Stanford大, https://biomni.stanford.edu/）= バイオメディカルAIエージェント。MCPサーバーではない
- **BioMCP**（GenomOncology, https://biomcp.org/）= バイオ系MCPサーバー/CLIツール

§19のPubMed MCPインストールコマンド（`@anthropic-ai/pubmed-mcp`）も架空。

## 修正方針

### 1. `chapters/00_ai_agent.md` — §0 ショーケースの🧬コラム
- 「bioomni」→ BioMCP（MCPサーバー）と Biomni（AIエージェント）を正確に区別して紹介
- MCPの文脈ではBioMCPを中心に、Biomniは「関連するバイオ特化AIエージェント」として言及

### 2. `chapters/19_database_api.md` — §19 🧬コラム（大幅書き換え）
コラムの構成を2部構成に:

**パート1: バイオ系MCPサーバー**
- **BioMCP**: 12種のバイオメディカルエンティティ統一クエリ。`uv tool install biomcp-cli`。具体例: `biomcp search article -g BRAF --limit 5`, `biomcp get gene BRAF pathways`
- **PubMed MCP**: 正しいインストール方法（`npx -y @smithery/cli install @JackKuo666/pubmed-mcp-server --client claude`）。論文検索・メタデータ取得・PDF DL
- その他: GEOmcp（GEOデータセット検索）、UniProt MCP、gget-MCP 等を簡潔に

**パート2: Biomni — バイオメディカルAIエージェント**
- Stanford大 SNAP グループ発（Huang & Leskovec）
- MCPサーバーではなく、150+ツール・59データベースを統合した自律研究エージェント
- MCP対応あり（外部ツール接続をサポート）
- 具体的な実績: ウェアラブルデータからの食後熱産生応答の特定、マルチオミクス遺伝子制御解析、分子クローニングプロトコル設計
- `pip install biomni`、Anthropic APIキー必須
- bioRxiv: https://www.biorxiv.org/content/10.1101/2025.05.30.656746v1
- ベンチマーク: LAB-Bench で専門家と同等の精度

### 3. `chapters/roadmap.md` — §19コラム記述の更新
### 4. `TODO.md` — 文言修正

## 修正するファイル
- `chapters/00_ai_agent.md`
- `chapters/19_database_api.md`
- `chapters/roadmap.md`
- `TODO.md`
