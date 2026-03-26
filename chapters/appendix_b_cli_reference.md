# 付録B. Claude Code CLI / Codex CLI クイックリファレンス対照表

> **本付録の記述は 2026年3月時点の各ツールの仕様に基づく。**
> AIコーディングエージェントのCLIツールは頻繁にアップデートされるため、最新の仕様は各ツールの公式ドキュメントを参照されたい。

概念で理解し、ツール固有の操作は以下を参照する。

**情報源**

| ツール | 公式ドキュメント |
|-------|----------------|
| Claude Code CLI | https://code.claude.com/docs [1] |
| Codex CLI | https://github.com/openai/codex [2] |

## セットアップ

| | Claude Code CLI | Codex CLI |
|--|----------------|-----------|
| インストール | native install（推奨; `curl -fsSL https://claude.ai/install.sh | bash`）、`brew install --cask claude-code`、または非推奨の `npm install -g @anthropic-ai/claude-code` | `npm install -g @openai/codex` または `brew install --cask codex` |
| 起動 | `claude` | `codex` |
| 認証 | Claude アカウントでのサインイン または Anthropic APIキー | ChatGPT アカウントでのサインイン または OpenAI APIキー |
| プロジェクト設定 | `CLAUDE.md` | `AGENTS.md` |
| ユーザー設定 | `~/.claude/` | `~/.codex/config.toml` |

## 権限制御

| 目的 / 設定軸 | Claude Code | Codex CLI |
|----------------|-------------|-----------|
| 調査と計画に限定 | Plan Mode (`Shift+Tab` or `/plan`) | `-s read-only` |
| 人が確認しながら編集 | Normal Mode | `-s workspace-write -a untrusted` または `-a on-request` |
| サンドボックス内で自動実行 | Auto-Accept Mode (`Shift+Tab`) | `--full-auto` |
| 危険な完全無保護 | — | `--dangerously-bypass-approvals-and-sandbox` |
| 権限設定の軸 | `/permissions` | `approval_policy` + `sandbox_mode` |

## モデルと推論

| | Claude Code | Codex CLI |
|--|-------------|-----------|
| 最高精度 | Opus 4.6 | GPT-5.4 |
| バランス | Sonnet 4.6 | GPT-5.3-Codex |
| 高速・低コスト | Haiku 4.5 | GPT-5.3-Codex-Spark |
| モデル切替 | `/model` | `/model` |
| 推論の深さ | Extended Thinking (`Alt+T` / `Option+T`) | Reasoning Effort (None〜Extra High) |
| 推論深さ設定 | Opus 4.6: adaptive（自動調節） | `-c model_reasoning_effort="high"` |
| 計画時の推論 | Plan Mode + Extended Thinking | `plan_mode_reasoning_effort` |

## セッション管理

| 操作 | Claude Code | Codex CLI |
|-----|-------------|-----------|
| コンテキスト圧縮 | `/compact` | （自動管理） |
| セッション再開 | `/resume` | `codex resume` / `codex resume --last` |
| Undo | `Esc Esc` (`/rewind`) | git revertで対応 |
| 計画をエディタで編集 | `Ctrl+G` | — |
| 非対話実行 | `claude -p "..."` | `codex exec "..."` |
| MCP追加 | `claude mcp add` | `codex mcp add` |

## カスタマイズ

| | Claude Code | Codex CLI | 本書での解説 |
|--|-------------|-----------|-------------|
| カスタムコマンド | `.claude/commands/` にMDファイル | `$skill-name`（SKILL.mdベース） | [§11-1](./11_cli.md#カスタムコマンドagent-skills--エージェント向けのテンプレート) |
| フック | `.claude/settings.json` の `hooks` | —（2026年3月時点では一般向け安定機能として扱わない） | [§8-3](./08_testing.md#エージェントフック--ツール実行前後の自動チェック) |
| MCP統合 | `claude mcp add` | `codex mcp add` | [§5-5](./05_software_components.md#5-5-mcpmodel-context-protocol-エージェントの能力を拡張する) |
| 階層設定 | ディレクトリごとに `CLAUDE.md` | ディレクトリごとに `AGENTS.md` | [§10-3](./10_deliverables.md#設定ファイルの階層構造--ディレクトリ単位のルール設定) |
| プロファイル | — | `--profile dev` (config.tomlの`[profiles]`) | — |
| バイオ向けMCP | PubMed MCP, BioMCP等 | 同左 | [§19-2](./19_database_api.md) |

## 参考文献

[1] Anthropic. "Claude Code overview". https://code.claude.com/docs (参照日: 2026-03-25)

[2] OpenAI. "Codex CLI". https://github.com/openai/codex (参照日: 2026-03-25)

---

本付録の内容は 2026年3月 時点の情報に基づく。
