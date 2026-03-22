# 付録B. Claude Code CLI / Codex CLI クイックリファレンス対照表

> **本付録の記述は 2026年3月時点の各ツールの仕様に基づく。**
> AIコーディングエージェントのCLIツールは頻繁にアップデートされるため、最新の仕様は各ツールの公式ドキュメントを参照されたい。

概念で理解し、ツール固有の操作は以下を参照する。

**情報源**

| ツール | 公式ドキュメント |
|-------|----------------|
| Claude Code CLI | https://docs.anthropic.com/en/docs/claude-code [1] |
| Codex CLI | https://github.com/openai/codex [2] |

## セットアップ

| | Claude Code CLI | Codex CLI |
|--|----------------|-----------|
| インストール | `npm install -g @anthropic-ai/claude-code` | `npm install -g @openai/codex` |
| 起動 | `claude` | `codex` |
| 認証 | Claude Pro/Max or APIキー | ChatGPT Plus/Pro or APIキー |
| プロジェクト設定 | `CLAUDE.md` | `AGENTS.md` |
| ユーザー設定 | `~/.claude/` | `~/.codex/config.toml` |

## 承認モード

| 安全レベル | Claude Code | Codex CLI |
|-----------|-------------|-----------|
| 読み取り専用 | Plan Mode (`Shift+Tab`×2 / `/plan`) | `-s read-only` |
| 承認あり（デフォルト） | Normal Mode | Auto（デフォルト） |
| 全自動 | Auto-Accept Mode (`Shift+Tab`) | `--full-auto` |
| 権限設定 | `/permissions` | `sandbox_mode` in config.toml |

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

| | Claude Code | Codex CLI |
|--|-------------|-----------|
| カスタムコマンド | `.claude/commands/` にMDファイル | `$skill-name`（SKILL.mdベース） |
| フック | `.claude/hooks/` | hooks in config.toml |
| MCP統合 | `claude mcp add` | `codex mcp add` |
| プロファイル | — | `--profile dev` (config.tomlの`[profiles]`) |

## 参考文献

[1] Anthropic. "Claude Code documentation". https://docs.anthropic.com/en/docs/claude-code (参照日: 2026-03-17)

[2] OpenAI. "Codex CLI". https://github.com/openai/codex (参照日: 2026-03-17)

---

本付録の内容は 2026年3月 時点の情報に基づく。
