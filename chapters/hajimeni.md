# はじめに

## コードを書かないプログラミングの時代

2025年から2026年にかけて、AIコーディングエージェントは驚異的な進化を遂げた。Anthropic の Claude Code CLI、OpenAI の Codex CLI に代表されるターミナルベースのAIエージェントは、自然言語による指示だけでコードを読み、書き、実行し、テストまで行う。もはやプログラミングエディタすら必要としない。ターミナルを開き、「FASTQファイルからクオリティスコアの低いリードを除去するスクリプトを作って」と指示すれば、エージェントはプロジェクトの構成を理解し、適切なライブラリを選択し、テスト付きのコードを生成する。

この変化の速度は数字が物語っている。SWE-bench Verified[1](https://arxiv.org/abs/2310.06770) [2](https://openai.com/index/introducing-swe-bench-verified/)——実在のGitHubリポジトリから抽出した500のソフトウェア工学課題を解くベンチマーク——において、最先端のAIモデルは2024年半ばの約50%から、2025年末には80%を超える正答率に達した。Claude Opus 4.5が80.9%[3](https://www.anthropic.com/news/claude-opus-4-5)、GPT-5.2 Codexが80.0%を記録し[4](https://openai.com/index/introducing-gpt-5-2/)、これはAnthropicの社内エンジニア採用試験を受験した全ての人間の候補者を上回る水準だという[5](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)。2025年のGitHub上では年間約10億件のコミットが記録され[6](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)、そのうちAIエージェントが直接生成するコミットの割合は急速に増加している。SemiAnalysisの分析によれば、2026年2月時点でClaude Codeだけで公開GitHubコミットの約4%を生成しており、年末には20%に達する可能性があると予測されている[7](https://newsletter.semianalysis.com/p/claude-code-is-the-inflection-point)。GitHub Copilotの利用者は2025年7月時点で累計2000万人を超え、開発者が書くコードの平均46%がAIによって生成されているという統計もある[8](https://techcrunch.com/2025/07/30/github-copilot-crosses-20-million-all-time-users/)。

これは「AIがプログラマーを補助する」段階をすでに超え、「AIが実装し、人間がレビュー・判断する」という新しい開発パラダイムへの移行を意味する。

ここで一つの疑問が浮かぶだろう。「ChatGPTのようなブラウザチャットでもコードは生成できるのに、なぜわざわざターミナルのCLIツールを使うのか？」と。確かにブラウザチャットはコードの断片を生成するのに優れている。しかし、プロジェクト全体を「開発」するには——ファイルを作成し、ディレクトリ構造を設計し、テストを実行し、バージョン管理を行う——エージェントがPC上のファイルを直接操作できる環境が必要である。ブラウザチャットではコードをコピー&ペーストで手動転記し、実行結果を貼り付けて往復する必要があるが、CLIエージェントはこれらをすべてターミナル上で完結させる。

安心してほしいのは、CLIエージェントとの対話もブラウザチャットと同じ自然言語であるということだ。操作方法が違うのではなく、エージェントができることの範囲が違う。ブラウザチャットが「相談相手」だとすれば、CLIエージェントは「手を動かせる共同作業者」である。ブラウザチャットとCLIエージェントの具体的な能力の違いについては、[§0 AIエージェントにコードを書かせる](./00_ai_agent.md#なぜcliを使うのか--ブラウザチャットとの違い)で対照表とともに詳しく解説する。

Andrej Karpathyはこの新しいプログラミングスタイルを**Vibe coding**（バイブコーディング）と名付けた[9](https://x.com/karpathy/status/1886192184808149383)。ソースコードを直接読み書きせず、自然言語でAIに指示を出し、生成されたコードの差分すら確認せず結果だけを見て判断する——「コードが存在することすら忘れる」手法である。この用語は瞬く間に広まり、2025年11月にはCollins English Dictionaryの「Word of the Year」に選ばれた。

## 初心者でもコードが書ける——しかし「良いコード」は書けない

AIコーディングエージェントの登場は、プログラミング未経験者にとって福音である。プログラミング言語の文法を一から学ばなくても、自然言語で目的を伝えるだけでプログラムが生成される。この敷居の低さは、とくにバイオインフォマティクスのように、プログラミング教育を体系的に受けていない実験系研究者がコードを必要とする分野において、大きな可能性を秘めている。

しかし、AIが生成したコードは「動く」ことが多い一方で、それが「良い」とは限らない。再現性を欠いた解析パイプライン、テストのない関数、ハードコーディングされたファイルパス、座標系の混同（BEDの0-basedとGFFの1-basedを取り違える等）——こうした問題は、コードが動いてしまうからこそ発見が遅れ、研究の信頼性を損なう原因となる。

こうした問題は印象論ではなく実証的にも裏付けられている。Thorgeirssonらは100名の大学生を対象にVibe codingの能力を測定した[10](https://arxiv.org/abs/2603.14133)。その結果、計算機科学の学業成績と文章力がともにVibe codingの成績を有意に予測し、計算機科学の知識は文章力の約2倍の寄与を示した。この効果は汎用的な推論能力を統制しても消えなかった。つまり「プロンプトの書き方がうまい」だけでは不十分であり、計算機科学の基礎知識こそがAIとの協働の質を左右するのである。

AIに適切な指示を出し、生成されたコードの品質を評価し、プロジェクト全体を設計するには、プログラミングそのものとは異なるレイヤーの知識——ソフトウェア開発の「作法」——が不可欠である。

## 既存の書籍が埋められなかったギャップ

従来のプログラミング学習書は大きく二つの層に分かれていた。一つは初心者向けの「Pythonの文法」「for文の書き方」といったプログラミング言語そのものの入門書。もう一つは上級者向けの「デザインパターン」「テスト駆動開発」「UNIX哲学」といったソフトウェア設計・開発手法の書籍である。

AIコーディングエージェントの登場以前、この二層構造には合理性があった。文法を知らなければコードは書けず、コードが書けなければ設計手法を学ぶ必要もなかったからだ。文法から始め、十分な経験を積んでから設計を学ぶ——この順序は長年にわたって機能してきた。

しかし今、AIエージェントがコーディングそのものを肩代わりする時代になり、この前提は崩れた。文法を深く知らなくてもコードは「書ける」。一方で、テストの書き方、プロジェクトのディレクトリ構成、バージョン管理、環境構築、成果物の公開方法といった「コーディングの周辺知識」は、AIに丸投げできないままに残されている。むしろ、AIと協働するためにこそ、これらの知識が今まで以上に重要になっている。

このギャップを埋める書籍は、これまで存在しなかった。AIコーディングツールの使い方を解説する書籍は近年増えているが、多くはプロンプトの書き方やツール操作の解説に終始している。「AIにどう話しかけるか」は教えてくれるが、「AIが生成したコードの設計が適切かどうかをどう判断するか」は教えてくれない。

## 生命科学——「プログラミング教育を受けていない人がプログラミングをする」分野

生命科学は、この問題がとりわけ先鋭化する分野である。

次世代シーケンサーが生み出す大量のデータ、シングルセル解析、ゲノムワイド関連解析、タンパク質構造予測——現代の生命科学研究において、データ解析は実験と同等の重要性を持つ。しかし多くの実験系研究者は、分子生物学や生化学を専門とし、計算機科学やソフトウェア工学の体系的な教育を受けていない。それでもプログラミングを「しなければならない」状況に日常的に直面する。

こうした研究者がAIコーディングエージェントに頼るのは自然な流れだ。そして実際、多くの場面でAIは驚くほどうまく機能する。しかし、エージェントが「スプリントで分割しましょう」「MVPから始めましょう」「リファクタリングが必要です」と提案してきたとき、これらの用語の意味がわからなければ、提案を評価することも、修正を指示することもできない。パッケージの公開方法を知らなければ、エージェントが生成したpyproject.tomlの内容が適切かどうか判断できない。テスト駆動開発の考え方を知らなければ、テストのないコードの危うさに気づかない。

## 本書の目的——AIプログラミング時代に不可欠な背景知識を届ける

本書は、AIコーディングエージェントとの協働を前提として、プログラミングの「作法」にまつわる背景知識を体系的に提供するものである。

Pythonの文法は教えない。アラインメントアルゴリズムの理論も扱わない。それらはすでに優れた書籍が数多く存在する。本書が扱うのは、その間にある——しかしAI時代になってむしろ重要性を増した——知識の層である。

前述のVibe coding研究[10](https://arxiv.org/abs/2603.14133)が示すとおり、計算機科学の基礎知識はAIとの協働を成功させるうえで最大の予測因子である。本書はプログラミング初心者に対して、この知識を——文法の暗記ではなく、ソフトウェア開発の「考え方」として——提供する。

具体的には以下の領域をカバーする:
- AIコーディングエージェントとの効果的な協働ワークフロー（計画→実装→レビュー）
- ターミナル操作とシェルの基本（AIエージェントの動作環境の理解）
- ソフトウェア設計の原則（KISS、DRY、UNIX哲学）と開発手法の用語
- データ構造と計算量、浮動小数点の精度、乱数再現性などの計算機科学の基礎
- バイオインフォマティクスで使われるデータフォーマットの選び方
- 開発環境の構築（conda、仮想環境、パッケージマネージャ）
- バージョン管理（Git/GitHub）とセマンティックバージョニング
- テスト駆動開発とコード品質管理
- デバッグの技術（tracebackの読み方、最小再現例の作成）
- CLIツールの設計（コマンドライン引数、ロギング、プログレス表示）
- データ処理と可視化の実践（NumPy、pandas、matplotlib等）
- 解析パイプラインの自動化（Snakemake、Nextflow）
- コンテナ（Docker、Apptainer）とHPCでの大規模計算
- コードのドキュメント化、公共データベースの活用、セキュリティと倫理
- 成果物の公開と共同開発の実践

題材はDNA配列解析を中心としたバイオインフォマティクスだが、機械学習の環境構築やGPU計算、実験管理についてもコラムとして取り上げた。本書で紹介する知識の大部分は、分野を問わず研究プログラミング全般に適用できるものである。

さらに、これらの知識は自分でコードを書く場面だけでなく、既存のオープンソースのバイオインフォマティクスツールのソースコードを読み解く際にも力を発揮する。プロジェクト構成、テスト、設計原則といった「作法」を知っていれば、論文で使われているツールのコードを読み、その挙動や制約を深く理解できるようになる。これは論文の解析手法の妥当性を評価し、自分の研究に適切に応用するための重要なスキルである（[§21 チーム開発とコミュニティ参加](./21_collaboration.md)も参照）。

## 本書が目指すもの

AIコーディングエージェントは、コードを「書く」作業を劇的に効率化した。しかし、何を作るべきか、どのような構造にすべきか、どう届けるべきか、どう検証すべきか——これらの判断は依然として人間の仕事である。本書は、まさにこの「判断するための知識」を提供する。

この本を通じて、実験系の生命科学者がAIコーディングエージェントを真のパートナーとして使いこなし、再現性があり、保守可能で、他の研究者と共有できるソフトウェアを自律的に開発できるようになることを願っている。それは単なるプログラミングスキルの向上ではなく、研究の生産性と信頼性の本質的な向上を意味するはずだ。

なお、AIコーディングエージェントの能力は急速に進化しており、本書で取り上げた具体的なツールや操作方法は今後変わりうる。しかし、本書が扱うソフトウェア開発の「作法」——テスト、バージョン管理、設計原則、プロジェクト構成——は、ツールの世代交代に左右されない普遍的な知識基盤である。読者には、最新のツール動向を継続的にフォローしつつ、本書で身につけた知識を土台として活用してほしい。

## 参考文献

- [1](https://arxiv.org/abs/2310.06770) Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., Narasimhan, K. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?". *Proceedings of the Twelfth International Conference on Learning Representations (ICLR)*, 2024. https://arxiv.org/abs/2310.06770
- [2](https://openai.com/index/introducing-swe-bench-verified/) OpenAI. "Introducing SWE-bench Verified". https://openai.com/index/introducing-swe-bench-verified/ (参照日: 2026-03-17)
- [3](https://www.anthropic.com/news/claude-opus-4-5) Anthropic. "Introducing Claude Opus 4.5". https://www.anthropic.com/news/claude-opus-4-5 (参照日: 2026-03-17)
- [4](https://openai.com/index/introducing-gpt-5-2/) OpenAI. "Introducing GPT-5.2". https://openai.com/index/introducing-gpt-5-2/ (参照日: 2026-03-17)
- [5](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations) Anthropic Engineering. "AI-resistant technical evaluations". https://www.anthropic.com/engineering/AI-resistant-technical-evaluations (参照日: 2026-03-17)
- [6](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/) GitHub. "Octoverse 2025: A new developer joins GitHub every second as AI leads TypeScript to #1". https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/ (参照日: 2026-03-17)
- [7](https://newsletter.semianalysis.com/p/claude-code-is-the-inflection-point) O'Laughlin, D., Ontiveros, J. E., Nanos, J., Patel, D., Nishball, D. "Claude Code is the Inflection Point". *SemiAnalysis*. https://newsletter.semianalysis.com/p/claude-code-is-the-inflection-point (参照日: 2026-03-17)
- [8](https://techcrunch.com/2025/07/30/github-copilot-crosses-20-million-all-time-users/) TechCrunch. "GitHub Copilot crosses 20M all-time users". https://techcrunch.com/2025/07/30/github-copilot-crosses-20-million-all-time-users/ (参照日: 2026-03-17)
- [9](https://x.com/karpathy/status/1886192184808149383) Karpathy, A. "There's a new kind of coding I call 'vibe coding'...". X (formerly Twitter), 2025-02-02. https://x.com/karpathy/status/1886192184808149383 (参照日: 2026-03-19)
- [10](https://arxiv.org/abs/2603.14133) Thorgeirsson, S., Weidmann, T. B., Su, Z. "Computer Science Achievement and Writing Skills Predict Vibe Coding Proficiency". *Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems (CHI '26)*, 2026. https://arxiv.org/abs/2603.14133

2026年3月　二階堂 愛
