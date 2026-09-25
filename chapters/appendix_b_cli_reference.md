# 付録B. Claude Code CLI / Codex CLI クイックリファレンス対照表

> **本付録の記述は 2026年7月時点の各ツールの仕様に基づく。** Codex CLIのセットアップ・権限制御・モデル・フックと、Claude Codeのモデル欄は2026年9月25日時点に更新した。
> AIコーディングエージェントのCLIツールは頻繁にアップデートされるため、最新の仕様は各ツールの公式ドキュメントを参照されたい。

概念で理解し、ツール固有の操作は以下を参照する。

**情報源**

| ツール | 公式ドキュメント |
|-------|----------------|
| Claude Code CLI | https://code.claude.com/docs [1](https://code.claude.com/docs) |
| Codex CLI | https://developers.openai.com/codex/cli [2](https://developers.openai.com/codex/cli) |

## セットアップ

| | Claude Code CLI | Codex CLI |
|--|----------------|-----------|
| インストール | native install（推奨; `curl -fsSL https://claude.ai/install.sh | bash`）、`brew install --cask claude-code`、または非推奨の `npm install -g @anthropic-ai/claude-code` | standalone installer（推奨; `curl -fsSL https://chatgpt.com/codex/install.sh | sh`）、`npm install -g @openai/codex`、または `brew install --cask codex` [2](https://developers.openai.com/codex/cli) |
| 起動 | `claude` | `codex` |
| 認証 | Claude アカウントでのサインイン または Anthropic APIキー | ChatGPT アカウントでのサインイン または OpenAI APIキー |
| プロジェクト設定 | `CLAUDE.md` | `AGENTS.md` |
| ユーザー設定 | `~/.claude/` | `~/.codex/config.toml` |

## 権限制御

| 目的 / 設定軸 | Claude Code | Codex CLI |
|----------------|-------------|-----------|
| 調査と計画に限定 | Plan Mode (`Shift+Tab` or `/plan`) | `-s read-only -a on-request` [6](https://developers.openai.com/codex/agent-approvals-security) |
| 標準の安全設定 | Normal Mode（編集前に確認） | Auto preset (`-s workspace-write -a on-request`) [6](https://developers.openai.com/codex/agent-approvals-security) |
| 承認質問なしでサンドボックス内を実行 | Auto-Accept Mode (`Shift+Tab`) | `-s workspace-write -a never` [6](https://developers.openai.com/codex/agent-approvals-security) |
| 危険な完全無保護 | — | `--dangerously-bypass-approvals-and-sandbox` [6](https://developers.openai.com/codex/agent-approvals-security) |
| 権限設定の軸 | `/permissions` | `approval_policy` + `sandbox_mode` |

## モデルと推論

| | Claude Code | Codex CLI |
|--|-------------|-----------|
| 最高精度 | Fable 5.1 / Opus 5.5（バイオ用途では Opus 5 へ自動再ルーティング）[3](https://code.claude.com/docs/en/model-config) | GPT-6 Astra [5](https://learn.chatgpt.com/docs/models) |
| バランス | Sonnet 5 | GPT-6 Sol [5](https://learn.chatgpt.com/docs/models) |
| 高速・低コスト | Haiku 4.5 | GPT-6 Luna [5](https://learn.chatgpt.com/docs/models) |
| 生物学カテゴリ | Fable 5.1・Fable 5・Opus 5.5はOpus 5で再実行。Opus 5はフォールバックせず拒否[3](https://code.claude.com/docs/en/model-config) | — |
| モデル切替 | `/model` | `/model` |
| 推論モード | Adaptive thinking（Opus 5.5 と Fable モデルは thinking を無効化できない。Opus 5 は既定で有効で、`Alt+T` / `Option+T` でセッション中に切り替え）[3](https://code.claude.com/docs/en/model-config) | Reasoning Effort（Low〜Ultra。LunaはMaxまで）[5](https://learn.chatgpt.com/docs/models) |
| 推奨開始値 | `low` / `medium` / `high` / `xhigh` / `max`（Opus 5.5は `medium`、Opus 5などは `high`）[4](https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5) | AstraはLow、SolはMedium、LunaはHigh [5](https://learn.chatgpt.com/docs/models) |
| Adaptive 対応 | Fable 5.1・Fable 5・Sonnet 5・Opus 4.7 以降は常時 Adaptive reasoning | — |
| 計画時の推論 | Plan Mode + 高い effort（`opusplan`） | `plan_mode_reasoning_effort` [8](https://developers.openai.com/codex/config-reference) |
| タスク予算（beta） | `task-budgets-2026-03-13` ヘッダで `task_budget` を指定可能 | — |

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
| カスタムコマンド／スキル | `.claude/skills/<name>/SKILL.md`（旧 `.claude/commands/*.md` も後方互換で動作） | `.agents/skills/<name>/SKILL.md`（`$skill-name` で呼び出し） | [§11-1](./11_cli.md#カスタムコマンドagent-skills--エージェント向けのテンプレート) |
| フック | `.claude/settings.json` の `hooks` | 対応（セッション・ツール・圧縮・サブエージェント等のライフサイクルイベント）[7](https://developers.openai.com/codex/hooks) | [§8-3](./08_testing.md#エージェントフック--ツール実行前後の自動チェック) |
| MCP統合 | `claude mcp add` | `codex mcp add` | [§5-5](./05_software_components.md#5-5-mcpmodel-context-protocol-エージェントの能力を拡張する) |
| 階層設定 | ディレクトリごとに `CLAUDE.md` | ディレクトリごとに `AGENTS.md` | [§10-3](./10_deliverables.md#設定ファイルの階層構造--ディレクトリ単位のルール設定) |
| プロファイル | — | `--profile <name>`（`$CODEX_HOME/<name>.config.toml` を重ねる） | — |
| バイオ向けMCP | PubMed MCP, BioMCP等 | 同左 | [§19-3](./19_database_api.md) |

## 参考文献

[1] Anthropic. "Claude Code overview". https://code.claude.com/docs (参照日: 2026-03-25)

[2] OpenAI. "Codex CLI". https://developers.openai.com/codex/cli (参照日: 2026-09-25)

[3] Anthropic. "Model configuration". https://code.claude.com/docs/en/model-config (参照日: 2026-09-25)

[4] Anthropic. "What's new in Claude Opus 5.5". https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5 (参照日: 2026-09-25)

[5] OpenAI. "Models — Codex". https://learn.chatgpt.com/docs/models (参照日: 2026-09-25)

[6] OpenAI. "Agent approvals & security". https://developers.openai.com/codex/agent-approvals-security (参照日: 2026-09-25)

[7] OpenAI. "Hooks". https://developers.openai.com/codex/hooks (参照日: 2026-09-25)

[8] OpenAI. "Configuration Reference". https://developers.openai.com/codex/config-reference (参照日: 2026-09-25)

---

本付録の内容は原則として2026年7月時点、上記の更新対象は2026年9月25日時点の情報に基づく。
