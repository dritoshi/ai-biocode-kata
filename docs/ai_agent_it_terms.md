# AIコーディングエージェントがよく使うIT用語・略語集

## 開発プロセス・方針

| 略語/用語 | 正式名称 | 意味 |
|---|---|---|
| MVP | Minimum Viable Product | 最小限の機能で動く最初のバージョン |
| POC | Proof of Concept | 技術的に実現可能か検証するための試作 |
| WIP | Work In Progress | 作業中・未完成 |
| PR | Pull Request | コードの変更をレビュー依頼する仕組み |
| MR | Merge Request | PRと同義（GitLab用語） |
| LGTM | Looks Good To Me | レビューOK |
| TDD | Test-Driven Development | テスト駆動開発 |
| BDD | Behavior-Driven Development | 振る舞い駆動開発 |
| CI/CD | Continuous Integration / Continuous Deployment | 継続的インテグレーション/デプロイ |
| E2E | End-to-End | エンドツーエンド（テスト等） |
| UAT | User Acceptance Testing | ユーザー受け入れテスト |
| QA | Quality Assurance | 品質保証 |

## 設計原則・パターン

| 略語/用語 | 正式名称 | 意味 |
|---|---|---|
| DRY | Don't Repeat Yourself | コードの重複を避ける原則 |
| KISS | Keep It Simple, Stupid | シンプルに保つ原則 |
| YAGNI | You Aren't Gonna Need It | 今不要な機能は作らない原則 |
| SOLID | 5つの設計原則の頭文字 | SRP/OCP/LSP/ISP/DIPの総称 |
| SRP | Single Responsibility Principle | 単一責任の原則 |
| DI | Dependency Injection | 依存性注入 |
| IoC | Inversion of Control | 制御の反転 |
| MVC | Model-View-Controller | UI設計パターン |
| MVVM | Model-View-ViewModel | UI設計パターン（React等で言及） |
| DDD | Domain-Driven Design | ドメイン駆動設計 |
| CQRS | Command Query Responsibility Segregation | コマンドクエリ責務分離 |
| DTO | Data Transfer Object | データ転送用オブジェクト |
| ORM | Object-Relational Mapping | オブジェクト関係マッピング |
| OOP | Object-Oriented Programming | オブジェクト指向 |
| FP | Functional Programming | 関数型プログラミング |

## Web・API関連

| 略語/用語 | 正式名称 | 意味 |
|---|---|---|
| API | Application Programming Interface | ソフトウェア間のインターフェース |
| REST | Representational State Transfer | Web APIの設計スタイル |
| CRUD | Create, Read, Update, Delete | データ操作の基本4操作 |
| GraphQL | - | APIクエリ言語 |
| gRPC | Google Remote Procedure Call | 高速RPC通信プロトコル |
| CORS | Cross-Origin Resource Sharing | クロスオリジンリソース共有 |
| JWT | JSON Web Token | 認証トークンの規格 |
| OAuth | Open Authorization | 認可のためのプロトコル |
| RBAC | Role-Based Access Control | ロールベースのアクセス制御 |
| SSR | Server-Side Rendering | サーバーサイドレンダリング |
| CSR | Client-Side Rendering | クライアントサイドレンダリング |
| SSG | Static Site Generation | 静的サイト生成 |
| SPA | Single Page Application | 単一ページアプリケーション |
| HMR | Hot Module Replacement | コード変更の即時反映 |
| CDN | Content Delivery Network | コンテンツ配信ネットワーク |
| SDK | Software Development Kit | 開発キット |
| CLI | Command Line Interface | コマンドラインツール |
| WebSocket | - | 双方向リアルタイム通信 |

## インフラ・DevOps

| 略語/用語 | 正式名称 | 意味 |
|---|---|---|
| K8s | Kubernetes | コンテナオーケストレーション |
| IaC | Infrastructure as Code | インフラのコード管理 |
| SRE | Site Reliability Engineering | サイト信頼性工学 |
| DevOps | Development + Operations | 開発と運用の統合 |
| GitOps | - | Gitベースのインフラ運用 |
| DNS | Domain Name System | ドメイン名解決 |
| SSL/TLS | Secure Sockets Layer / Transport Layer Security | 暗号化通信 |
| SSH | Secure Shell | 暗号化リモート接続 |
| SLA | Service Level Agreement | サービスレベル合意 |
| EOL | End of Life | サポート終了 |

## データベース・データ

| 略語/用語 | 正式名称 | 意味 |
|---|---|---|
| ACID | Atomicity, Consistency, Isolation, Durability | トランザクションの4特性 |
| CAP | Consistency, Availability, Partition tolerance | 分散システムの定理 |
| ETL | Extract, Transform, Load | データの抽出・変換・読み込み |
| NoSQL | Not Only SQL | 非リレーショナルDB |
| KV | Key-Value | キーバリューストア |

## AIエージェント特有のフレーズ

| 用語 | 意味 |
|---|---|
| scaffold / scaffolding | プロジェクトの雛形を自動生成すること |
| boilerplate | 定型的なコードやテンプレート |
| refactor / refactoring | 機能を変えずにコードを整理すること |
| idiomatic | その言語らしい書き方 |
| opinionated | 特定の設計方針を強く推奨するフレームワーク等 |
| convention over configuration | 設定より規約を優先する思想 |
| breaking change | 後方互換性を壊す変更 |
| edge case | 境界条件・例外的なケース |
| footgun | 自分の足を撃つような危険な仕様 |
| bikeshedding | 些末な問題に時間をかけすぎること |
| tech debt | 技術的負債 |
| monorepo | 複数プロジェクトを1リポジトリで管理 |
| middleware | リクエスト処理の中間層 |
| serverless | サーバー管理不要のクラウド実行環境 |
| containerization | コンテナ化（Docker等） |
| observability | 可観測性（ログ・メトリクス・トレース） |
| a11y | Accessibility（アクセシビリティ） |
| i18n | Internationalization（国際化） |
| l10n | Localization（ローカライズ） |
| env | Environment（環境・環境変数） |
| deps | Dependencies（依存ライブラリ） |
| noop / no-op | 何もしない操作 |
| shim / polyfill | 互換性のための補完コード |
| tree-shaking | 未使用コードの除去 |
| lazy loading | 必要時に遅延読み込み |
| hot path | 頻繁に実行される処理経路 |
| escape hatch | フレームワークの制約を回避する手段 |
| guard clause | 早期リターンによる条件チェック |
| happy path | 正常系の処理フロー |
| de facto | 事実上の標準 |
