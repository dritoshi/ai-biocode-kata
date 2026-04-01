# はじめに

> 「ないんだったら、自分で作ればいいのよ！」
> — 涼宮ハルヒ, 谷川流『涼宮ハルヒの憂鬱』第1巻 (角川スニーカー文庫, 2003)

## コードを書かないプログラミングの時代

2025年から2026年にかけて、AIコーディングエージェントは驚異的な進化を遂げた。Anthropic の Claude Code CLI、OpenAI の Codex CLI に代表されるターミナルベースのAIエージェントは、自然言語による指示だけでコードを読み、書き、実行し、テストまで行う。少なくとも、プログラミングエディタを常時開いていなくても開発を進められる段階に達している。ターミナルを開き、「FASTQファイルからクオリティスコアの低いリードを除去するスクリプトを作って」と指示すれば、エージェントはプロジェクトの構成を理解し、適切なライブラリを選択し、テスト付きのコードを生成する。

この変化の速度は数字が物語っている。SWE-bench Verified[1](https://arxiv.org/abs/2310.06770) [2](https://openai.com/index/introducing-swe-bench-verified/)——実在のGitHubリポジトリから抽出した500のソフトウェア工学課題を解くベンチマーク——において、最先端のAIモデルは2024年半ばの約50%から、2025年末には80%を超える正答率に達した。Claude Opus 4.5が80.9%[3](https://www.anthropic.com/news/claude-opus-4-5)、GPT-5.2が80.0%を記録し[4](https://openai.com/index/introducing-gpt-5-2/)、Anthropicは別の社内評価として、Claude Opus 4 が時間制限付きの性能最適化課題で **most human applicants** を上回ったとも報告している[5](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)。2025年のGitHub上では年間約10億件のコミットが記録され[6](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)、そのうちAIエージェントが直接生成するコミットの割合は急速に増加している。SemiAnalysis は 2026年2月時点の推計として、Claude Code だけで公開GitHubコミットの約4%を生成しており、年末には20%に達する可能性があると述べている[7](https://newsletter.semianalysis.com/p/claude-code-is-the-inflection-point)。GitHub Copilotの利用者は2025年9月22日時点で20M+ usersに達し[8](https://github.blog/ai-and-ml/github-copilot/gartner-positions-github-as-a-leader-in-the-2025-magic-quadrant-for-ai-code-assistants-for-the-second-year-in-a-row/)、GitHubは別の2023年時点の報告として「Copilotが有効なファイルでは平均46%のコードがCopilot由来」と説明している[9](https://github.blog/2023-02-14-github-copilot-now-has-a-better-ai-model-and-new-capabilities/)。

これは「AIがプログラマーを補助する」段階をすでに超え、「AIが実装し、人間がレビュー・判断する」という新しい開発パラダイムへの移行を意味する。

ここで一つの疑問が浮かぶだろう。「ChatGPTのようなブラウザチャットでもコードは生成できるのに、なぜわざわざターミナルのCLIツールを使うのか？」と。確かにブラウザチャットはコードの断片を生成するのに優れている。しかし、プロジェクト全体を「開発」するには——ファイルを作成し、ディレクトリ構造を設計し、テストを実行し、バージョン管理を行う——エージェントがPC上のファイルを直接操作できる環境が必要である。ブラウザチャットではコードをコピー&ペーストで手動転記し、実行結果を貼り付けて往復する必要があるが、CLIエージェントはこれらをすべてターミナル上で完結させる。

安心してほしいのは、CLIエージェントとの対話もブラウザチャットと同じ自然言語であるということだ。操作方法が違うのではなく、エージェントができることの範囲が違う。ブラウザチャットが「相談相手」だとすれば、CLIエージェントは「手を動かせる共同作業者」である。ブラウザチャットとCLIエージェントの具体的な能力の違いについては、[§0 AIエージェントにコードを書かせる](./00_ai_agent.md#なぜcliを使うのか--ブラウザチャットとの違い)で対照表とともに詳しく解説する。

Andrej Karpathyはこの新しいプログラミングスタイルを**Vibe coding**（バイブコーディング）と名付けた[10](https://x.com/karpathy/status/1886192184808149383)。ソースコードを直接読み書きせず、自然言語でAIに指示を出し、生成されたコードの差分すら確認せず結果だけを見て判断する——「コードが存在することすら忘れる」手法である。この用語は瞬く間に広まり、2025年11月にはCollins Dictionaryの Word of the Year にも選ばれた[11](https://www.collinsdictionary.com/us/woty/)。

## 初心者でもコードが書ける——しかし「良いコード」は書けない

AIコーディングエージェントの登場は、プログラミング未経験者にとって福音である。プログラミング言語の文法を一から学ばなくても、自然言語で目的を伝えるだけでプログラムが生成される。この敷居の低さは、とくにバイオインフォマティクスのように、プログラミング教育を体系的に受けていない実験系研究者がコードを必要とする分野において、大きな可能性を秘めている。

しかし、AIが生成したコードは「動く」ことが多い一方で、それが「良い」とは限らない。再現性を欠いた解析パイプライン、テストのない関数、ハードコーディングされたファイルパス、座標系の混同（BEDの0-basedとGFFの1-basedを取り違える等）——こうした問題は、コードが動いてしまうからこそ発見が遅れ、研究の信頼性を損なう原因となる。

こうした問題は印象論ではなく実証的にも裏付けられている。Thorgeirssonらは100名の大学生を対象にVibe codingの能力を測定した[12](https://arxiv.org/abs/2603.14133)。その結果、計算機科学の学業成績と文章力がともにVibe codingの成績を有意に予測し、計算機科学の知識は文章力の約2倍の寄与を示した。この効果は汎用的な推論能力を統制しても消えなかった。つまり「プロンプトの書き方がうまい」だけでは不十分であり、計算機科学の基礎知識こそがAIとの協働の質を左右するのである。

AIに適切な指示を出し、生成されたコードの品質を評価し、プロジェクト全体を設計するには、プログラミングそのものとは異なるレイヤーの知識——ソフトウェア開発の「作法」——が不可欠である。

## 既存の書籍が埋められなかったギャップ

従来のプログラミング学習書は大きく二つの層に分かれていた。一つは初心者向けの「Pythonの文法」「for文の書き方」といったプログラミング言語そのものの入門書。もう一つは上級者向けの「デザインパターン」「テスト駆動開発」「UNIX哲学」といったソフトウェア設計・開発手法の書籍である。

AIコーディングエージェントの登場以前、この二層構造には合理性があった。文法を知らなければコードは書けず、コードが書けなければ設計手法を学ぶ必要もなかったからだ。文法から始め、十分な経験を積んでから設計を学ぶ——この順序は長年にわたって機能してきた。

しかし今、AIエージェントがコーディングそのものを肩代わりする時代になり、この前提は崩れた。文法を深く知らなくてもコードは「書ける」。一方で、テストの書き方、プロジェクトのディレクトリ構成、バージョン管理、環境構築、成果物の公開方法といった「コーディングの周辺知識」は、AIに丸投げできないままに残されている。むしろ、AIと協働するためにこそ、これらの知識が今まで以上に重要になっている。

このギャップを埋める書籍は、これまで存在しなかった。AIコーディングツールの使い方を解説する書籍は近年増えているが、多くはプロンプトの書き方やツール操作の解説に終始している。「AIにどう話しかけるか」は教えてくれるが、「AIが生成したコードの設計が適切かどうかをどう判断するか」は教えてくれない。

## 生命科学——「プログラミング教育を受けていない人がプログラミングをする」分野

生命科学は、この問題がとりわけ先鋭化する分野である。

次世代シーケンサーが生み出す大量のデータ、シングルセル解析、ゲノムワイド関連解析、タンパク質構造予測——現代の生命科学研究において、データ解析は実験と同等の重要性を持つ。しかし多くの実験系研究者は、分子生物学や生化学を専門とし、計算機科学やソフトウェア工学の体系的な教育を受けていない。それでもプログラミングを「しなければならない」状況に日常的に直面する。

この状況はさらに加速している。世界各国がAI for Science（AI4S）——AIを科学研究の加速に活用する取り組み——を国家戦略に位置づけている[13](https://doi.org/10.1038/s41586-023-06221-2)。米国では2025年11月にトランプ大統領が大統領令「Genesis Mission」を発令し、AIによって10年間で米国の科学的生産性を倍増させるという目標を掲げた[14](https://www.whitehouse.gov/presidential-actions/2025/11/launching-the-genesis-mission/)。バイオテクノロジーは最優先分野の一つに指定されている。EUはHorizon Europeを通じてAI駆動の科学研究を推進し、日本では理研がTRIP-AGISプログラムのもとで生命科学・物質材料科学を対象とした科学研究用基盤モデルの開発と研究自動化を進めている[15](https://www.riken.jp/research/labs/trip/agis/)。AlphaFoldによるタンパク質構造予測は2024年のノーベル化学賞を受賞し[16](https://www.nobelprize.org/prizes/chemistry/2024/press-release/)、シングルセル解析の基盤モデル（scGPT[17](https://doi.org/10.1038/s41592-024-02201-0)、Geneformer[18](https://doi.org/10.1038/s41586-023-06139-9)）やゲノム言語モデル（Evo[19](https://doi.org/10.1126/science.ado9336)）が次々と発表されている。こうしたAI4Sの成果を自分の研究データに適用するには、環境構築、パラメータ調整、結果の後処理といったプログラミング作業が不可避である。

さらに、仮説生成から実験設計、データ解析、論文執筆までを自律的に行う研究用AIエージェントが続々と登場している。Sakana AIのAI Scientistは、アイデア生成から論文執筆までの研究サイクルをエンドツーエンドで自動化するシステムであり、その技術的枠組みがNatureに掲載された[20](https://www.nature.com/articles/s41586-026-10265-5)。ただし現時点では新規の科学的発見ではなくネガティブな結果の報告にとどまっており、自律的な科学発見への道のりはまだ長い。Google ResearchのAI co-scientistはGemini 2.0ベースのマルチエージェントシステムで、提案した薬剤候補が実験で検証されている[21](https://arxiv.org/abs/2502.18864)。StanfordのBiomniは105のバイオソフトウェアと59のデータベースを統合した汎用バイオメディカルエージェントであり、創薬から希少疾患診断まで広範なタスクをコードベースで遂行する[22](https://www.biorxiv.org/content/10.1101/2025.05.30.656746v1)。これらのエージェントは強力だが万能ではない——AI Scientistは実験の42%がコーディングエラーで失敗し、Kosmosは1回の実行で42,000行のコードを生成する[23](https://arxiv.org/abs/2511.02824)。エージェントの出力を検証し、自分の研究パイプラインに統合するには、プログラミングの素養が不可欠である。AIが科学を変えつつある時代に、AIが生成するコードを理解し評価できる能力は、すべての生命科学者に求められる基盤能力になりつつある。

こうした研究者がAIコーディングエージェントに頼るのは自然な流れだ。そして実際、多くの場面でAIは驚くほどうまく機能する。しかし、エージェントが「スプリントで分割しましょう」「MVPから始めましょう」「リファクタリングが必要です」と提案してきたとき、これらの用語の意味がわからなければ、提案を評価することも、修正を指示することもできない。パッケージの公開方法を知らなければ、エージェントが生成したpyproject.tomlの内容が適切かどうか判断できない。テスト駆動開発の考え方を知らなければ、テストのないコードの危うさに気づかない。

## 本書の目的——AIプログラミング時代に不可欠な背景知識を届ける

本書は、AIコーディングエージェントとの協働を前提として、プログラミングの「作法」にまつわる背景知識を体系的に提供するものである。

Pythonの文法は教えない。アラインメントアルゴリズムの理論も扱わない。それらはすでに優れた書籍が数多く存在する。本書が扱うのは、その間にある——しかしAI時代になってむしろ重要性を増した——知識の層である。

前述のVibe coding研究[12](https://arxiv.org/abs/2603.14133)が示すとおり、計算機科学の基礎知識はAIとの協働を成功させるうえで最大の予測因子である。本書はプログラミング初心者に対して、この知識を——文法の暗記ではなく、ソフトウェア開発の「考え方」として——提供する。

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

さらに、これらの知識は自分でコードを書く場面だけでなく、既存のオープンソースのバイオインフォマティクスツールのソースコードを読み解く際にも力を発揮する。プロジェクト構成、テスト、設計原則といった「作法」を知っていれば、論文で使われているツールのコードを読み、その挙動や制約を深く理解できるようになる。これは論文の解析手法の妥当性を評価し、自分の研究に適切に応用するための重要なスキルである（[§21 共同開発の実践 — レビュー・質問・OSS参加](./21_collaboration.md)も参照）。

## 本書が前提とする知識

本書は文法の入門書ではない。AIエージェントがコードを生成する時代に、そのコードをレビューし判断するための「作法」を教える本である。以下の知識は本書の中では詳しく扱わないため、不安がある場合は先に学んでおくことを勧める。

### Pythonの基本文法

変数、関数定義（`def`）、制御構文（`if` / `for` / `while`）、リスト・辞書の操作、`import`文が読めること。自分でゼロから書ける必要はないが、AIエージェントが生成したコードを読んで「何をしているか」がわかるレベルを想定する。

- **Python公式チュートリアル**（日本語）[24](https://docs.python.org/ja/3/tutorial/) — §3「形式ばらない入門」から§6「モジュール」までが本書の前提範囲。無料
- **東京大学「Pythonプログラミング入門」**[25](https://utokyo-ipp.github.io/) — 大学1年生向けの講義資料。Jupyter Notebook形式で手を動かしながら学べる。無料
- **改訂 独習Pythonバイオ情報解析**（実験医学別冊, 羊土社, 2025）[26](https://www.yodosha.co.jp/yodobook/book/9784758122788/) — 生命科学研究者向けにJupyter、NumPy、pandas、Scanpyの基礎を解説。本書と併読すると効果的

### ターミナルとLinuxの基本操作

ターミナル（macOSのTerminal.app、WindowsのWSL / PowerShell等）を起動したことがあり、コマンドを入力した経験があること。`cd`、`ls`、`pwd` の意味がわかること。本書の§2で詳しく扱うが、ターミナルの起動方法自体は前提とする。

- **Linux標準教科書**（LPI-Japan）[27](https://linuc.org/textbooks/linux/) — 無料でダウンロードできる初学者向けLinux学習教材。LinuCレベル1対応
- **MIT "The Missing Semester of Your CS Education"**[28](https://missing.csail.mit.edu/) — Shell、Git、エディタなど「大学で教えないが開発に必要なスキル」を扱う。日本語訳あり。無料

### 生命科学の基礎用語

DNA、RNA、タンパク質、遺伝子、ゲノムといった用語の意味がわかること。次世代シーケンサーが何をするものかを概念レベルで知っていること。自分で配列解析をしたことがなくても構わないが、「FASTQファイルはシーケンサーの出力」「BAMファイルはリファレンスゲノムへのマッピング結果」程度の理解は§4以降で前提となる。

- **統合TV**[29](https://togotv.dbcls.jp/) — バイオインフォマティクスの動画チュートリアル集。日本語。無料
- **坊農秀雅『生命科学データベース・ウェブツール — 図解と動画で使い方がわかる! 研究がはかどる定番18選』**（メディカル・サイエンス・インターナショナル, 2018）[30](https://www.amazon.co.jp/dp/4815701431) — 生命科学のデータベースとウェブツールの使い方を統合TVの動画と連携して解説。初心者に最適
- **坊農秀雅『Dr. Bonoの生命科学データ解析』**（メディカル・サイエンス・インターナショナル, 2017）[31](https://www.amazon.co.jp/dp/4895929019) — データ解析の基礎を生命科学の文脈で解説。本書の前段階として推奨

本書を読み進める中で「この章はまだ難しい」と感じたら、各章の冒頭に示す前提知識を確認し、必要に応じて上記の資料に戻ることを勧める。通読する必要はない——必要な部分だけ拾い読みすればよい。

## 本書が目指すもの

AIコーディングエージェントは、コードを「書く」作業を劇的に効率化した。しかし、何を作るべきか、どのような構造にすべきか、どう届けるべきか、どう検証すべきか——これらの判断は依然として人間の仕事である。本書は、まさにこの「判断するための知識」を提供する。

この本を通じて、実験系の生命科学者がAIコーディングエージェントを真のパートナーとして使いこなし、再現性があり、保守可能で、他の研究者と共有できるソフトウェアを自律的に開発できるようになることを願っている。それは単なるプログラミングスキルの向上ではなく、研究の生産性と信頼性の本質的な向上を意味するはずだ。

なお、AIコーディングエージェントの能力は急速に進化しており、本書で取り上げた具体的なツールや操作方法は今後変わりうる。しかし、本書が扱うソフトウェア開発の「作法」——テスト、バージョン管理、設計原則、プロジェクト構成——は、ツールの世代交代に左右されない普遍的な知識基盤である。読者には、最新のツール動向を継続的にフォローしつつ、本書で身につけた知識を土台として活用してほしい。

## 謝辞

本書の執筆にあたり、多くの方々にお世話になった。

研究室のみなさまに感謝する。特に、実験系生物科学者の立場から本書の企画に刺激を与えてくれた笹川洋平准教授と矢野実氏には、本書を書くきっかけそのものをいただいた。また、実験系のメンバーが日々の研究で本当に必要としていることは何かを常に意識しながら執筆を進めた。すべてのメンバーに感謝する。

また、千葉大学の大田達郎准教授には本書のレビューをして頂きいくつもの有益なコメントを頂いたことに感謝する。

本書の執筆やレビューは、Claude Code CLI (Claude Opus 4.5, effort: high) および Codex CLI (GPT-5.4, reasoning: xhigh) の支援のもとで行った。これらのAIコーディングエージェントの開発者のみなさまに感謝する。


<div align="right">

*——長い孤独な探究の時代が終わり、人類知と人工知能が共に歩む新たな旅の門出に*

2026年4月  
二階堂 愛
東京科学大学 / 理化学研究所

</div>

## 参考文献

- [1](https://arxiv.org/abs/2310.06770) Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., Narasimhan, K. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?". *Proceedings of the Twelfth International Conference on Learning Representations (ICLR)*, 2024. https://arxiv.org/abs/2310.06770
- [2](https://openai.com/index/introducing-swe-bench-verified/) OpenAI. "Introducing SWE-bench Verified". https://openai.com/index/introducing-swe-bench-verified/ (参照日: 2026-03-17)
- [3](https://www.anthropic.com/news/claude-opus-4-5) Anthropic. "Introducing Claude Opus 4.5". https://www.anthropic.com/news/claude-opus-4-5 (参照日: 2026-03-17)
- [4](https://openai.com/index/introducing-gpt-5-2/) OpenAI. "Introducing GPT-5.2". https://openai.com/index/introducing-gpt-5-2/ (参照日: 2026-03-17)
- [5](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations) Anthropic Engineering. "AI-resistant technical evaluations". https://www.anthropic.com/engineering/AI-resistant-technical-evaluations (参照日: 2026-03-17)
- [6](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/) GitHub. "Octoverse 2025: A new developer joins GitHub every second as AI leads TypeScript to #1". https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/ (参照日: 2026-03-17)
- [7](https://newsletter.semianalysis.com/p/claude-code-is-the-inflection-point) O'Laughlin, D., Ontiveros, J. E., Nanos, J., Patel, D., Nishball, D. "Claude Code is the Inflection Point". *SemiAnalysis*. https://newsletter.semianalysis.com/p/claude-code-is-the-inflection-point (参照日: 2026-03-17)
- [8](https://github.blog/ai-and-ml/github-copilot/gartner-positions-github-as-a-leader-in-the-2025-magic-quadrant-for-ai-code-assistants-for-the-second-year-in-a-row/) GitHub. "Gartner positions GitHub as a Leader in the 2025 Magic Quadrant for AI Code Assistants for the second year in a row". https://github.blog/ai-and-ml/github-copilot/gartner-positions-github-as-a-leader-in-the-2025-magic-quadrant-for-ai-code-assistants-for-the-second-year-in-a-row/ (参照日: 2026-03-25)
- [9](https://github.blog/2023-02-14-github-copilot-now-has-a-better-ai-model-and-new-capabilities/) GitHub. "GitHub Copilot now has a better AI model and new capabilities". https://github.blog/2023-02-14-github-copilot-now-has-a-better-ai-model-and-new-capabilities/ (参照日: 2026-03-25)
- [10](https://x.com/karpathy/status/1886192184808149383) Karpathy, A. "There's a new kind of coding I call 'vibe coding'...". X (formerly Twitter), 2025-02-02. https://x.com/karpathy/status/1886192184808149383 (参照日: 2026-03-19)
- [11](https://www.collinsdictionary.com/us/woty/) Collins Dictionary. "The Collins Word of the Year 2025 is...". https://www.collinsdictionary.com/us/woty/ (参照日: 2026-03-25)
- [12](https://arxiv.org/abs/2603.14133) Thorgeirsson, S., Weidmann, T. B., Su, Z. "Computer Science Achievement and Writing Skills Predict Vibe Coding Proficiency". *Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems (CHI '26)*, 2026. https://arxiv.org/abs/2603.14133
- [13](https://doi.org/10.1038/s41586-023-06221-2) Wang, H., Fu, T., Du, Y., et al. "Scientific discovery in the age of artificial intelligence". *Nature*, 620, 47–60, 2023. https://doi.org/10.1038/s41586-023-06221-2
- [14](https://www.whitehouse.gov/presidential-actions/2025/11/launching-the-genesis-mission/) The White House. "Launching the Genesis Mission". Executive Order, 2025-11-24. https://www.whitehouse.gov/presidential-actions/2025/11/launching-the-genesis-mission/ (参照日: 2026-03-27)
- [15](https://www.riken.jp/research/labs/trip/agis/) 理化学研究所. "科学研究基盤モデル開発プログラム（AGIS）". https://www.riken.jp/research/labs/trip/agis/ (参照日: 2026-03-27)
- [16](https://www.nobelprize.org/prizes/chemistry/2024/press-release/) The Nobel Foundation. "The Nobel Prize in Chemistry 2024". https://www.nobelprize.org/prizes/chemistry/2024/press-release/ (参照日: 2026-03-27)
- [17](https://doi.org/10.1038/s41592-024-02201-0) Cui, H., Wang, C., Maan, H., et al. "scGPT: toward building a foundation model for single-cell multi-omics using generative AI". *Nature Methods*, 21, 1470–1480, 2024. https://doi.org/10.1038/s41592-024-02201-0
- [18](https://doi.org/10.1038/s41586-023-06139-9) Theodoris, C. V., Xiao, L., Chopra, A., et al. "Transfer learning enables predictions in network biology". *Nature*, 618, 616–624, 2023. https://doi.org/10.1038/s41586-023-06139-9
- [19](https://doi.org/10.1126/science.ado9336) Nguyen, E., Poli, M., Durrant, M. G., et al. "Sequence modeling and design from molecular to genome scale with Evo". *Science*, 386(6723), 2024. https://doi.org/10.1126/science.ado9336
- [20](https://www.nature.com/articles/s41586-026-10265-5) Lu, C., Lu, C., Lange, R. T., et al. "Towards end-to-end automation of AI research". *Nature*, 2026. https://www.nature.com/articles/s41586-026-10265-5
- [21](https://arxiv.org/abs/2502.18864) Gottweis, J., Weng, W.-H., Darber, A., et al. "Towards an AI co-scientist". arXiv: 2502.18864, 2025. https://arxiv.org/abs/2502.18864
- [22](https://www.biorxiv.org/content/10.1101/2025.05.30.656746v1) Li, M., Zheng, Z., Huang, K., et al. "Biomni: A General-Purpose Biomedical AI Agent". bioRxiv, 2025. https://www.biorxiv.org/content/10.1101/2025.05.30.656746v1
- [23](https://arxiv.org/abs/2511.02824) Schmidgall, S., et al. "Kosmos: An AI Scientist for Autonomous Discovery". arXiv: 2511.02824, 2025. https://arxiv.org/abs/2511.02824
- [24](https://docs.python.org/ja/3/tutorial/) Python Software Foundation. "Pythonチュートリアル". https://docs.python.org/ja/3/tutorial/ (参照日: 2026-03-31)
- [25](https://utokyo-ipp.github.io/) 東京大学. "Pythonプログラミング入門". https://utokyo-ipp.github.io/ (参照日: 2026-03-31)
- [26](https://www.yodosha.co.jp/yodobook/book/9784758122788/) 先進ゲノム解析研究推進プラットフォーム. "改訂 独習Pythonバイオ情報解析". 実験医学別冊, 羊土社, 2025. https://www.yodosha.co.jp/yodobook/book/9784758122788/
- [27](https://linuc.org/textbooks/linux/) LPI-Japan. "Linux標準教科書". https://linuc.org/textbooks/linux/ (参照日: 2026-03-31)
- [28](https://missing.csail.mit.edu/) MIT. "The Missing Semester of Your CS Education". https://missing.csail.mit.edu/ (参照日: 2026-03-31)
- [29](https://togotv.dbcls.jp/) DBCLS. "統合TV". https://togotv.dbcls.jp/ (参照日: 2026-03-31)
- [30](https://www.amazon.co.jp/dp/4815701431) 坊農秀雅. "生命科学データベース・ウェブツール — 図解と動画で使い方がわかる! 研究がはかどる定番18選". メディカル・サイエンス・インターナショナル, 2018. https://www.amazon.co.jp/dp/4815701431
- [31](https://www.amazon.co.jp/dp/4895929019) 坊農秀雅. "Dr. Bonoの生命科学データ解析". メディカル・サイエンス・インターナショナル, 2017. https://www.amazon.co.jp/dp/4895929019

