# バイオインフォマティクス教育カリキュラム調査：プログラミング/計算スキルの抽出

## 調査対象一覧

| Tier | # | ソース名 | 種別 |
|------|---|---------|------|
| 1 | 1 | Rosalind.info / Compeau & Pevzner "Bioinformatics Algorithms" | 大学コース/教科書 |
| 1 | 2 | MIT 7.91J Foundations of Computational and Systems Biology | 大学コース |
| 1 | 3 | Harvard MCB112 Biological Sequence Analysis | 大学コース |
| 2 | 4 | CSHL Programming for Biology | トレーニングプログラム |
| 2 | 5 | Canadian Bioinformatics Workshops (CBW) | トレーニングプログラム |
| 2 | 6 | Galaxy Training Network (GTN) | トレーニングプログラム |
| 2 | 7 | EMBL-EBI Training | トレーニングプログラム |
| 3 | 8 | "Bioinformatics Data Skills" (Buffalo, 2015) | 教科書 |
| 3 | 9 | "Practical Computing for Biologists" (Haddock & Dunn, 2011) | 教科書 |
| 3 | 10 | "Python for Biologists" (Jones) | 教科書 |

---

## Source 1: Rosalind.info / Compeau & Pevzner "Bioinformatics Algorithms"

**概要**: Rosalindはバイオインフォマティクスと問題解決を通じてプログラミングを学ぶプラットフォーム（284問題）。Compeau & Pevznerの教科書は UCSD CSE 181/282 の教材（第3版）。

### Rosalind.info トピックカテゴリ（16カテゴリ）

- Alignment（19問）
- Combinatorics（22問）
- Computational Mass Spectrometry（6問）
- Divide-and-Conquer（2問）
- Dynamic Programming（23問）
- Genome Assembly（7問）
- Genome Rearrangements（6問）
- Graph Algorithms（11問）
- Graphs（18問）
- Heredity（6問）
- Phylogeny（19問）
- Population Dynamics（3問）
- Probability（13問）
- Set Theory（3問）
- Sorting（14問）
- String Algorithms（26問）

**Rosalind 問題トラック**:
- Python Village（Python入門）
- Bioinformatics Stronghold（主要問題群）
- Bioinformatics Armory（ツール利用）
- Bioinformatics Textbook Track（教科書連動）
- Algorithmic Heights（アルゴリズム基礎）

### Compeau & Pevzner "Bioinformatics Algorithms" 章構成

| 章 | タイトル | アルゴリズム概念 |
|----|---------|--------------|
| 1 | Where in the Genome Does DNA Replication Begin? | Algorithmic warmup |
| 2 | Which DNA Patterns Play the Role of Molecular Clocks? | Randomized algorithms |
| 3 | How Do We Assemble Genomes? | Graph algorithms |
| 4 | How Do We Sequence Antibiotics? | Brute force algorithms |
| 5 | How Do We Compare Biological Sequences? | Dynamic programming |
| 6 | Are There Fragile Regions in the Human Genome? | Combinatorial algorithms |
| 7 | Which Animal Gave Us SARS? | Phylogeny / tree algorithms |
| 8 | How Did Yeast Become a Wine Maker? | Clustering algorithms |
| 9 | How Do We Locate Disease-Causing Mutations? | Combinatorial pattern matching |
| 10 | Why Have Biologists Still Not Developed an HIV Vaccine? | Hidden Markov Models |
| 11 | Was T. Rex Just a Big Chicken? | Phylogenetic tree reconstruction |

### カテゴリ別分類

| カテゴリ | トピック |
|---------|---------|
| **1. Data management & formats** | FASTA形式、DNA/RNA/タンパク質配列データの読み書き |
| **2. Programming fundamentals** | Python基礎（Python Village）、文字列操作、再帰、ループ |
| **3. Software engineering practices** | （直接扱わない） |
| **4. Analysis pipelines** | 配列アラインメント（BLAST的手法）、ゲノムアセンブリ、質量分析 |
| **5. Infrastructure** | （直接扱わない） |
| **6. Statistics & data analysis** | 確率論、組合せ論、集合論、ソーティング、動的計画法 |
| **7. Bioinformatics-specific** | ゲノムアセンブリ（de Bruijn graph）、配列アラインメント（SW/NW）、系統樹、ゲノム再編成、モチーフ探索、HMM、クラスタリング |
| **8. Collaboration & sharing** | （直接扱わない） |

**Sources:**
- [Rosalind.info Problems](https://rosalind.info/problems/list-view/)
- [Rosalind.info Topics](https://rosalind.info/problems/topics/)
- [Bioinformatics Algorithms Textbook](https://compeau.cbd.cmu.edu/online-education-projects/bioinformatics-algorithms-an-active-learning-approach/)

---

## Source 2: MIT 7.91J Foundations of Computational and Systems Biology

**概要**: MITの大学院レベル計算生物学入門コース。核酸・タンパク質の配列・構造解析の基礎と複雑な生物学システムの解析。Spring 2014。Python使用。

### 講義トピック（全22回 + 試験2回 + 発表2回）

**Genomic Analysis（L1-L4）**
- L1: Course Introduction; History of Computational Biology
- L2: Local Alignment (BLAST) and Statistics
- L3: Global Alignment of Protein Sequences (NW, SW, PAM, BLOSUM)
- L4: Comparative Genomic Analysis of Gene Regulation

**Next Gen Sequencing（L5-L8）**
- L5: Library Complexity and Short Read Alignment (Mapping)
- L6: Genome Assembly
- L7: ChIP-seq Analysis; DNA-protein Interactions
- L8: RNA-sequence Analysis: Expression, Isoforms

**Modeling Biological Function（L9-L11）**
- L9: Modeling and Discovery of Sequence Motifs (Gibbs Sampler, Alternatives)
- L10: Markov and Hidden Markov Models of Genomic and Protein Features
- L11: RNA Secondary Structure — Biological Functions and Prediction

**Proteomics（L12-L14）**
- L12: Introduction to Protein Structure; Structure Comparison and Classification
- L13: Predicting Protein Structure
- L14: Predicting Protein Interactions

**Regulatory Networks（L15-L18）**
- L15: Gene Regulatory Networks
- L16: Protein Interaction Networks
- L17: Logic Modeling of Cell Signaling Networks
- L18: Analysis of Chromatin Structure

**Computational Genetics（L19-L22）**
- L19: Discovering Quantitative Trait Loci (QTLs)
- L20: Human Genetics, SNPs, and Genome Wide Association Studies (GWAS)
- L21: Synthetic Biology: From Parts to Modules to Therapeutic Systems
- L22: Causality, Natural Computing, and Engineering Genomes

### カテゴリ別分類

| カテゴリ | トピック |
|---------|---------|
| **1. Data management & formats** | 配列データ、ChIP-seqデータ、RNA-seqデータ |
| **2. Programming fundamentals** | Python基礎（前提知識/recitationで指導） |
| **3. Software engineering practices** | （直接扱わない） |
| **4. Analysis pipelines** | BLAST、ショートリードマッピング、ゲノムアセンブリ、ChIP-seq解析、RNA-seq解析 |
| **5. Infrastructure** | （直接扱わない） |
| **6. Statistics & data analysis** | アラインメントスコアの統計学、確率モデル、マルコフモデル、HMM、ネットワークモデリング |
| **7. Bioinformatics-specific** | 配列アラインメント（局所/大域）、置換行列（PAM/BLOSUM）、モチーフ探索（Gibbs Sampler）、タンパク質構造予測、タンパク質相互作用予測、遺伝子制御ネットワーク、RNA二次構造予測、QTL解析、GWAS、合成生物学 |
| **8. Collaboration & sharing** | （直接扱わない） |

**Sources:**
- [MIT OCW 7.91J Course Page](https://ocw.mit.edu/courses/7-91j-foundations-of-computational-and-systems-biology-spring-2014/)
- [MIT OCW 7.91J Calendar](https://ocw.mit.edu/courses/7-91j-foundations-of-computational-and-systems-biology-spring-2014/pages/calendar/)

---

## Source 3: Harvard MCB112 Biological Sequence Analysis

**概要**: バクテリオファージゲノム配列解析を一貫した題材として計算手法を教える。Python（NumPy, SciPy, Pandas, Jupyter）使用。12週の週次データ解析問題。シミュレーションによる計算的陽性/陰性対照実験を重視。

### 週次トピック（Spring 2026）

| 週 | トピック |
|----|---------|
| Week 01 | Molecular biology of phage genomes |
| Week 02 | Probability, entropy, and information |
| Week 03 | P-values and statistical significance tests |
| Week 04 | （情報未取得） |
| Week 05 | Sequence comparison and alignment |
| Week 06 | Probability, likelihood, and Bayesian inference |
| Week 07 | Expectation-maximization algorithms |
| Week 08 | Hidden Markov models |
| Week 09 | Mixture models and k-means clustering |
| Week 10 | Regression fitting |
| Week 11 | Principal components analysis (PCA) |
| Week 12 | Phylogenetic inference |

### カテゴリ別分類

| カテゴリ | トピック |
|---------|---------|
| **1. Data management & formats** | ゲノム配列データ |
| **2. Programming fundamentals** | Python, NumPy, SciPy, Pandas, Jupyter Notebook |
| **3. Software engineering practices** | シミュレーションによる計算実験（陽性/陰性対照実験） |
| **4. Analysis pipelines** | 配列比較・アラインメント |
| **5. Infrastructure** | （直接扱わない） |
| **6. Statistics & data analysis** | 確率論、エントロピー・情報量、P値・統計的有意性検定、ベイズ推論、尤度、EMアルゴリズム、HMM、混合モデル、k-meansクラスタリング、回帰、PCA（主成分分析） |
| **7. Bioinformatics-specific** | 配列アラインメント、系統推定、HMM（バイオ文脈） |
| **8. Collaboration & sharing** | （直接扱わない） |

**Sources:**
- [MCB112 Course Website](http://mcb112.org/)
- [MCB112 Schedule](http://mcb112.org/schedule.html)
- [Harvard QRD - MCB112](https://qrd.college.harvard.edu/directory/mcb-112/)

---

## Source 4: CSHL Programming for Biology

**概要**: ラボ研究者向け約2.5週間の集中コース（Cold Spring Harbor Laboratory）。プログラミング未経験者対象。Python使用。2025年は10月12-28日開催。

### カリキュラム構成

**Week 1: Unix & Git 基礎**
- Unix Overview, The Basics, Advanced Unix
- Text editors
- Git for beginners, GitHub, VSCode setup

**Week 1-2: Python 基礎（10モジュール）**
- Python I: Overview, execution, syntax, data types and variables
- Python II: Operators, boolean logic, numeric operations
- Python III: Sequence manipulation, string handling
- Python IV: Lists, tuples, iteration loops
- Python V: Dictionary and set data structures
- Python VI: File input/output operations
- Python VII: Regular expression patterns
- Python VIII: Advanced data structure design
- Python IX: Exception handling mechanisms
- Python X: Functions, variable scope, module architecture

**Week 2: 上級 Python**
- Python XI: Classes（オブジェクト指向）
- BioPython introduction and applications

**Week 3: バイオインフォマティクス & ツール**
- Bioinformatics 1: Python Pipelines
- Mamba package manager
- HPC workflow integration
- AI-assisted coding techniques
- Debugging strategies with AI tools

**Week 3-4: 専門トピック**
- Transcriptomes and RNAseq（Part 1 & 2）
- Sequence Similarity（Part 1 & 2）
- Gene homology analysis
- Scoring matrix problem-solving

**Week 4: キャップストーンプロジェクト**
- Group project organization and execution
- Final presentations（20分/グループ）

### カテゴリ別分類

| カテゴリ | トピック |
|---------|---------|
| **1. Data management & formats** | ファイルI/O、配列データ形式 |
| **2. Programming fundamentals** | Python（変数、データ型、演算子、ブール論理、文字列、リスト、タプル、辞書、集合、ループ、関数、スコープ、モジュール、正規表現、例外処理、クラス） |
| **3. Software engineering practices** | Git/GitHub、VSCode、デバッグ戦略、AI支援コーディング |
| **4. Analysis pipelines** | Python pipelines、RNA-seq解析、配列類似性解析、遺伝子ホモロジー解析 |
| **5. Infrastructure** | Unix/シェル基礎・応用、テキストエディタ、Mamba パッケージマネージャ、HPC ワークフロー統合 |
| **6. Statistics & data analysis** | スコアリング行列 |
| **7. Bioinformatics-specific** | BioPython、トランスクリプトーム解析、RNA-seq、配列類似性、遺伝子ホモロジー |
| **8. Collaboration & sharing** | Git/GitHub、グループプロジェクト |

**Sources:**
- [Programming for Biology 2025](https://programmingforbiology.org/)
- [CSHL Programming for Biology](https://meetings.cshl.edu/courses.aspx?course=C-INFO)

---

## Source 5: Canadian Bioinformatics Workshops (CBW)

**概要**: カナダのバイオインフォマティクス・ワークショップシリーズ。年間15前後のワークショップを提供。2024年は15ワークショップ + 4つの新規パイロット。

### ワークショップ一覧（2023-2026年の統合リスト）

**基礎スキル系**
- Introduction to R
- Analysis Using R
- Help! What Statistical Model Should I Use?
- Reproducible Research: Essentials for Managing Your Data

**オミクス解析系**
- RNA-seq Analysis
- Single-Cell RNA-seq Analysis
- Metabolomics Analysis
- Epigenomics Analysis
- Proteomics

**ゲノミクス系**
- Infectious Disease Genomic Epidemiology
- Pharmacogenomics Data Analysis
- Introductory Spatial 'Omics Analysis (Visium HD)
- Bridging Pathology and Genomics: NGS for Pathologists

**データ統合・ネットワーク系**
- Pathway and Network Analysis
- Machine Learning
- Machine Learning for Medical Imaging Analysis

**マイクロバイオーム系**
- Beginner Microbiome Analysis
- Advanced Microbiome Analysis

### カテゴリ別分類

| カテゴリ | トピック |
|---------|---------|
| **1. Data management & formats** | Reproducible Research: Essentials for Managing Your Data |
| **2. Programming fundamentals** | Introduction to R, Analysis Using R |
| **3. Software engineering practices** | 再現性のある研究 |
| **4. Analysis pipelines** | RNA-seq解析、scRNA-seq解析、メタボロミクス解析、エピゲノミクス解析、プロテオミクス解析、感染症ゲノム疫学、空間オミクス解析、薬理ゲノミクスデータ解析 |
| **5. Infrastructure** | （直接扱わない） |
| **6. Statistics & data analysis** | Help! What Statistical Model Should I Use?、Machine Learning、Machine Learning for Medical Imaging |
| **7. Bioinformatics-specific** | パスウェイ・ネットワーク解析、マイクロバイオーム解析、NGS、空間オミクス、薬理ゲノミクス |
| **8. Collaboration & sharing** | 再現可能なデータ管理 |

**Sources:**
- [CBW Current Workshops](https://bioinformatics.ca/workshops/current-workshops/)
- [CBW 2024 Announcement (BioStars)](https://www.biostars.org/p/9588799/)
- [CBW GitHub Pages](https://bioinformaticsdotca.github.io/)

---

## Source 6: Galaxy Training Network (GTN)

**概要**: 世界のGalaxyコミュニティが開発・保守するオープントレーニング教材リポジトリ。370以上のチュートリアル、330名以上のインストラクター。CC-BY-SA ライセンス。

### トピックカテゴリ

**Start Here**
- Introduction to Galaxy Analyses（15チュートリアル）
- Using Galaxy and Managing your Data（27チュートリアル）

**Scientific Fields**
- Climate / Computational Chemistry / SARS-CoV-2 / Foundations of Data Science / Digital Humanities / Ecology / Evolution / FAIR Data, Workflows & Research / Genome Annotation / Imaging / Materials Science / Microbiome / One Health / Plants / Statistics and Machine Learning / Visualization

**Methodologies**
- Assembly / ELIXIR / Epigenetics / GMOD / Metabolomics / Proteomics / Sequence Analysis / Single Cell / Synthetic Biology / Transcriptomics / Variant Analysis

**Developer/Admin Track**
- Galaxy Server Administration（55チュートリアル）
- Development in Galaxy（39チュートリアル）

**Community & Contribution**
- Galaxy Community Building（8チュートリアル）
- Contributing to Training Material（23チュートリアル）
- Teaching and Hosting Galaxy Training（17チュートリアル）

### Foundations of Data Science チュートリアル詳細

**Data Manipulation**
- Data Manipulation Olympics / Data Visualisation Olympics (R) / Data Manipulation Olympics (SQL) / Data Manipulation Olympics (JQ)

**Bash/CLI**
- Advanced CLI in Galaxy / CLI Educational Game (Bashcrawl) / CLI basics

**Python（基礎〜応用、モジュール構成）**
- Introduction to Python / Advanced Python / Plotting in Python
- Python modules: Math, Functions, Basic Types & Type Conversion, Lists & Strings & Dictionaries, Flow Control, Loops, Files & CSV, Try & Except, Introductory Graduation, Argparse, Testing, Type annotations, Globbing, Subprocess
- Conda/Virtual Environments For Software Development

### Sequence Analysis チュートリアル詳細
- Mapping / Quality Control
- Sanger sequence management / NCBI BLAST+ / Primer design
- Quality and contamination control in bacterial isolate
- Removal of human reads from sequencing data
- Viral sample alignment and variant visualization
- Screening assembled genomes for contamination (NCBI FCS)

### カテゴリ別分類

| カテゴリ | トピック |
|---------|---------|
| **1. Data management & formats** | Managing Data in Galaxy、FAIR Data/Workflows/Research、データ操作（SQL, JQ） |
| **2. Programming fundamentals** | Python基礎〜応用（Math, Functions, Types, Lists, Dictionaries, Flow Control, Loops, Files, CSV, Argparse, Globbing, Subprocess）、CLI/Bash基礎、R |
| **3. Software engineering practices** | Testing, Type annotations, Conda/Virtual Environments, Galaxy Development |
| **4. Analysis pipelines** | Assembly、Transcriptomics、Variant Analysis、Proteomics、Metabolomics、Sequence Analysis（マッピング、QC、BLAST）、Single Cell |
| **5. Infrastructure** | Galaxy Server Administration、CLI基礎、Conda/Virtual Environments |
| **6. Statistics & data analysis** | Statistics and Machine Learning、Data Visualization（R, Python）|
| **7. Bioinformatics-specific** | Genome Annotation、Epigenetics、Microbiome、Variant Analysis、Single Cell、Evolution、Synthetic Biology |
| **8. Collaboration & sharing** | Community Building、Contributing to Training Material、Teaching and Hosting Galaxy Training、FAIR principles |

**Sources:**
- [Galaxy Training Network](https://training.galaxyproject.org/training-material/)
- [GTN Foundations of Data Science](https://training.galaxyproject.org/training-material/topics/data-science/)
- [GTN Sequence Analysis](https://training.galaxyproject.org/training-material/topics/sequence-analysis/)

---

## Source 7: EMBL-EBI Training

**概要**: 欧州分子生物学研究所-欧州バイオインフォマティクス研究所のトレーニングプログラム。無料オンライン自習コース + ライブウェビナー + 実習コース。

### オンラインコース一覧

**入門コース**
- Bioinformatics for the Terrified
- What is Bioinformatics?
- Introduction to EMBL-EBI Resources
- A Journey Through Bioinformatics
- Methods in Bioinformatics
- Bioinformatics for Principal Investigators
- Introductory Bioinformatics Pathway（キュレーションセット）

**機能ゲノミクス**
- Functional Genomics I: Introduction and Design
- Functional Genomics II: Common Technologies and Data Analysis Methods
  - Real-time PCR
  - Microarrays（feature extraction, QC, normalization, differential expression, biological interpretation, submission to public repositories）
  - Next Generation Sequencing（Illumina, 454, Ion Torrent, Nanopore, SMRT sequencing）
  - RNA sequencing（experimental design, replicates, library preparation, QC, read mapping/alignment, quantification, differential expression analysis）
  - Epigenetic modifications（histone modifications）
  - DNA/RNA-protein interactions

**リソース別コース**
- AlphaFold（タンパク質3D構造予測）
- Ensembl（ゲノムブラウザ、臨床ゲノミクス向けアノテーション）
- UniProt（タンパク質配列・機能情報）
- Expression Atlas（遺伝子発現データ）
- IntAct（タンパク質相互作用）
- ChEMBL（化合物データ）
- Complex Portal（タンパク質複合体）
- PDBe / EMDB（タンパク質構造データベース）
- MGnify（メタゲノミクス）
- MetaboLights（メタボロミクス）
- Europe PMC（文献検索）

**専門コース**
- Metagenomics Bioinformatics（メタゲノミクスデータ解析ワークフロー）
- Proteomics Bioinformatics（mass spectrometry, search engines, quantitative approaches, MS data repositories）
- Next Generation Sequencing Bioinformatics（assembly, re-sequencing, variant calling）
- Genome Bioinformatics: Short to Long-read Sequencing

### カテゴリ別分類

| カテゴリ | トピック |
|---------|---------|
| **1. Data management & formats** | 公共データベース（primary/secondary databases）、リポジトリへのデータ提出、オントロジーによる制御語彙 |
| **2. Programming fundamentals** | （直接扱わない — ツール利用が中心） |
| **3. Software engineering practices** | （直接扱わない） |
| **4. Analysis pipelines** | RNA-seq解析ワークフロー（QC→マッピング→定量→差次的発現解析）、マイクロアレイ解析、NGSデータ解析、メタゲノミクスワークフロー、プロテオミクスワークフロー |
| **5. Infrastructure** | （直接扱わない） |
| **6. Statistics & data analysis** | 差次的発現解析、正規化、QC、定量手法 |
| **7. Bioinformatics-specific** | AlphaFold（構造予測）、ゲノムブラウジング（Ensembl）、タンパク質解析（UniProt, PDBe）、メタゲノミクス（MGnify）、エピジェネティクス、variant calling、NGSテクノロジー（Illumina, Nanopore, SMRT等） |
| **8. Collaboration & sharing** | 公共リポジトリへのデータ提出、オープンアクセスデータベースの利用 |

**Sources:**
- [EMBL-EBI Training](https://www.ebi.ac.uk/training/)
- [Introductory Bioinformatics Pathway](https://www.ebi.ac.uk/training/online/courses/introductory-bioinformatics-pathway/)
- [Functional Genomics II](https://www.ebi.ac.uk/training/online/courses/functional-genomics-ii-common-technologies-and-data-analysis-methods/)
- [AlphaFold Course](https://www.ebi.ac.uk/training/online/courses/alphafold/)
- [Metagenomics Bioinformatics](https://www.ebi.ac.uk/training/online/courses/metagenomics-bioinformatics/)

---

## Source 8: "Bioinformatics Data Skills" (Vince Buffalo, 2015)

**概要**: O'Reilly Media刊。538ページ、700以上のコード例。再現可能でロバストなバイオインフォマティクス研究のためのオープンソースツール。

### 章構成

| 章 | タイトル | 主な内容 |
|----|---------|---------|
| Preface | — | — |
| 1 | How to Learn Bioinformatics | 導入・学習姿勢 |
| 2 | Setting Up and Managing a Bioinformatics Project | プロジェクト構成・ディレクトリ設計 |
| 3 | Remedial Unix Shell | Unix/シェル基礎 |
| 4 | Working with Remote Machines | SSH、リモートサーバ接続 |
| 5 | Git for Scientists | バージョン管理（リポジトリ作成、追跡、ステージング、コミット、リモート） |
| 6 | Bioinformatics Data | データ形式・データの特性 |
| 7 | Unix Data Tools | パイプ、grep、sed、awk等のデータ処理 |
| 8 | A Rapid Introduction to the R Language | 探索的データ分析（EDA） |
| 9 | Working with Range Data | IRanges, GenomicRanges, BEDTools |
| 10 | Working with Sequence Data | FASTA/FASTQ処理 |
| 11 | Working with Alignment Data | SAM/BAMファイル処理 |
| 12 | Bioinformatics Shell Scripting, Writing Pipelines, and Parallelizing Tasks | パイプライン構築・並列化 |
| 13 | Out-of-Memory Approaches | BGZF/Tabix、SQLite、大規模データ処理 |
| Conclusion | — | — |

### カテゴリ別分類

| カテゴリ | トピック |
|---------|---------|
| **1. Data management & formats** | バイオインフォマティクスプロジェクトの設計と管理、FASTA/FASTQ/SAM/BAM形式、ゲノミックレンジデータ（BED形式）、タブ区切りファイル、SQLite、BGZF/Tabix |
| **2. Programming fundamentals** | R言語入門、Unix shell |
| **3. Software engineering practices** | Git（リポジトリ作成、ファイル追跡、ステージング、コミット、リモートリポジトリ）、プロジェクト構成、再現可能な研究 |
| **4. Analysis pipelines** | シェルスクリプティング、パイプライン構築、タスクの並列化、配列データ処理、アラインメントデータ処理 |
| **5. Infrastructure** | Unix shell基礎、リモートマシンでの作業（SSH等） |
| **6. Statistics & data analysis** | 探索的データ分析（R）、ゲノミックレンジ操作（IRanges, GenomicRanges） |
| **7. Bioinformatics-specific** | 配列データ処理、アラインメントデータ処理、ゲノミックレンジ操作（BEDTools）、大規模ゲノムデータのout-of-memoryアプローチ |
| **8. Collaboration & sharing** | Git/バージョン管理、再現可能な研究の実践 |

**Sources:**
- [Bioinformatics Data Skills - Author's Page](https://vincebuffalo.com/book/)
- [O'Reilly Book Page](https://www.oreilly.com/library/view/bioinformatics-data-skills/9781449367480/)
- [GitHub Supplementary Files](https://github.com/vsbuffalo/bds-files)

---

## Source 9: "Practical Computing for Biologists" (Haddock & Dunn, 2011)

**概要**: 実験系生物学者向けの計算基礎教科書。22章、6部構成。バイオインフォ特化ではなく汎用的な計算スキルが中心。

### 章構成

**Part I: Text Files**
- Ch 1: Getting Set Up
- Ch 2: Regular Expressions: Powerful Search and Replace
- Ch 3: Exploring the Flexibility of Regular Expressions

**Part II: The Shell**
- Ch 4: Command-line Operations: The Shell
- Ch 5: Handling Text in the Shell
- Ch 6: Scripting with the Shell

**Part III: Programming**
- Ch 7: Components of Programming
- Ch 8: Beginning Python Programming
- Ch 9: Decisions and Loops
- Ch 10: Reading and Writing Files
- Ch 11: Merging Files
- Ch 12: Modules and Libraries
- Ch 13: Debugging Strategies

**Part IV: Combining Methods**
- Ch 14: Selecting and Combining Tools
- Ch 15: Relational Databases
- Ch 16: Advanced Shell and Pipelines

**Part V: Graphics**
- Ch 17: Graphical Concepts
- Ch 18: Working with Vector Art
- Ch 19: Working with Pixel Images

**Part VI: Advanced Topics**
- Ch 20: Working on Remote Computers
- Ch 21: Installing Software
- Ch 22: Electronics: Interacting with the Physical World

### カテゴリ別分類

| カテゴリ | トピック |
|---------|---------|
| **1. Data management & formats** | テキストファイル操作、正規表現によるデータ処理、ファイルのマージ、リレーショナルデータベース |
| **2. Programming fundamentals** | Python基礎（変数、分岐、ループ、ファイルI/O）、モジュールとライブラリ、プログラミングの構成要素 |
| **3. Software engineering practices** | デバッグ戦略、ツールの選択と組合せ |
| **4. Analysis pipelines** | 高度なシェルとパイプライン、ツールの統合 |
| **5. Infrastructure** | シェル操作基礎、リモートコンピュータでの作業、ソフトウェアのインストール |
| **6. Statistics & data analysis** | データの視覚化（グラフィカルコンセプト、ベクターアート、ピクセル画像） |
| **7. Bioinformatics-specific** | （バイオ特有のトピックは少ない — 汎用的な計算スキルが中心） |
| **8. Collaboration & sharing** | （直接扱わない） |

**Sources:**
- [OUP Book Page](https://global.oup.com/academic/product/practical-computing-for-biologists-9780878933914)
- [Practical Computing Website](https://practicalcomputing.org/)

---

## Source 10: "Python for Biologists" + "Advanced Python for Biologists" (Martin Jones)

**概要**: 生物学者向けPython入門書 + 上級編。バイオインフォマティクスの具体例でPythonを教える。

### "Python for Biologists" 章構成

| 章 | タイトル | 主要トピック |
|----|---------|------------|
| 1 | Introduction and Environment | Python環境のセットアップ |
| 2 | Printing and Manipulating Text | DNA/タンパク質配列の文字列操作、AT含量計算、イントロンスプライシング |
| 3 | Reading and Writing Files | ファイルパス、FASTA形式、ゲノムDNA分割 |
| 4 | Processing Data | 配列操作の高度なツール、アダプター配列のトリミング、エクソン連結 |
| 5 | Functions | 関数定義、引数、カプセル化、関数テスト |
| 6 | Conditional Tests | if/else/elif、whileループ、複合条件 |
| 7 | Regular Expressions | 生物学におけるパターン、モジュール、パターン検索 |
| 8 | Dictionaries | ペアデータの格納、辞書の作成と反復 |
| 9 | Integration and Polish | 既存ツールとの統合、k-merカウント、DNA配列の長さ別ビニング |

### "Advanced Python for Biologists" 章構成

| 章 | タイトル | 主要トピック |
|----|---------|------------|
| 4 | Object Oriented Python | DNAシーケンスクラス、コンストラクタ、継承、オーバーライド、ポリモーフィズム |
| 5 | Functional Python | 状態と可変性、副作用、高階関数（map, filter, sorted, reduce） |
| 6 | Iterators, Comprehensions & Generators | リスト/辞書/集合内包表記、イテレータ、ジェネレータ |
| 7 | Exception Handling | 例外捕捉、特定エラー捕捉、else/finally、例外の伝播、カスタム例外型 |

### カテゴリ別分類

| カテゴリ | トピック |
|---------|---------|
| **1. Data management & formats** | FASTAファイル読み書き、ファイルパス操作、CSV/テキストファイル処理 |
| **2. Programming fundamentals** | Python基礎（変数、文字列、リスト、辞書、条件分岐、ループ、関数、正規表現）、上級Python（OOP、関数型プログラミング、内包表記、ジェネレータ、例外処理） |
| **3. Software engineering practices** | 関数テスト、カプセル化、プログラムの統合と仕上げ |
| **4. Analysis pipelines** | 既存ツールとの統合 |
| **5. Infrastructure** | Python環境セットアップ |
| **6. Statistics & data analysis** | （直接扱わない） |
| **7. Bioinformatics-specific** | DNA/タンパク質配列操作、AT含量計算、イントロンスプライシング、アダプタートリミング、エクソン連結、k-merカウント、FASTA処理 |
| **8. Collaboration & sharing** | （直接扱わない） |

**Sources:**
- [Python for Biologists - Amazon](https://www.amazon.com/Python-Biologists-complete-programming-beginners/dp/1492346136)
- [Advanced Python for Biologists - Amazon](https://www.amazon.com/Advanced-Python-Biologists-Martin-Jones/dp/1495244377)

---

## クロスソース集計：カテゴリ別トピック出現頻度

### 1. Data management & formats

| トピック | 出現ソース |
|---------|-----------|
| FASTA/FASTQ形式 | 1, 8, 10 |
| SAM/BAM形式 | 8 |
| BED/ゲノミックレンジ形式 | 8 |
| リレーショナルデータベース（SQLite等） | 8, 9 |
| ファイルI/O | 4, 9, 10 |
| 正規表現によるデータ処理 | 4, 9, 10 |
| プロジェクト構成・管理 | 8 |
| 公共データベース利用 | 7 |
| FAIR data principles | 6 |
| 再現可能なデータ管理 | 5 |
| タブ区切りファイル/圧縮（BGZF/Tabix） | 8 |
| オントロジー/制御語彙 | 7 |

### 2. Programming fundamentals

| トピック | 出現ソース |
|---------|-----------|
| Python基礎（変数、型、演算子） | 1, 3, 4, 6, 9, 10 |
| 文字列操作 | 4, 10 |
| リスト/辞書/集合 | 4, 6, 10 |
| 条件分岐・ループ | 4, 6, 9, 10 |
| 関数 | 4, 6, 10 |
| 正規表現 | 4, 9, 10 |
| 例外処理 | 4, 10 |
| オブジェクト指向プログラミング | 4, 10 |
| 関数型プログラミング（内包表記、ジェネレータ） | 10 |
| R言語 | 5, 8 |
| Unix shell | 4, 8, 9 |
| NumPy/SciPy/Pandas | 3 |
| Jupyter Notebook | 3 |

### 3. Software engineering practices

| トピック | 出現ソース |
|---------|-----------|
| Git/GitHub/バージョン管理 | 4, 8 |
| デバッグ戦略 | 4, 9 |
| テスト（単体テスト） | 6, 10 |
| 型注釈 | 6 |
| AI支援コーディング | 4 |
| プロジェクト構成 | 8 |
| カプセル化 | 10 |
| 再現可能な研究 | 5, 8 |
| Conda/仮想環境 | 6 |

### 4. Analysis pipelines

| トピック | 出現ソース |
|---------|-----------|
| 配列アラインメント（BLAST, SW, NW） | 1, 2, 3 |
| RNA-seq解析 | 2, 4, 5, 7 |
| ゲノムアセンブリ | 1, 2 |
| ChIP-seq解析 | 2 |
| シェルパイプライン | 8, 9 |
| タスクの並列化 | 8 |
| 配列データ処理 | 8, 10 |
| メタゲノミクスワークフロー | 7 |
| プロテオミクスワークフロー | 5, 7 |
| scRNA-seq解析 | 5 |
| Variant calling | 6, 7 |
| メタボロミクス解析 | 5 |
| エピゲノミクス解析 | 5 |

### 5. Infrastructure (environment setup, HPC, cloud)

| トピック | 出現ソース |
|---------|-----------|
| Unix/シェル基礎 | 4, 8, 9 |
| リモートマシン/SSH | 8, 9 |
| ソフトウェアインストール | 9 |
| HPC ワークフロー統合 | 4 |
| パッケージマネージャ（Mamba/Conda） | 4, 6 |
| Python環境セットアップ | 10 |
| Galaxy Server Administration | 6 |
| テキストエディタ/IDE（VSCode） | 4 |

### 6. Statistics & data analysis

| トピック | 出現ソース |
|---------|-----------|
| 確率論 | 1, 3 |
| 統計的検定（P値、有意性） | 3 |
| ベイズ推論 | 3 |
| HMM（Hidden Markov Models） | 2, 3 |
| EMアルゴリズム | 3 |
| クラスタリング（k-means） | 3 |
| 回帰 | 3 |
| PCA（主成分分析） | 3 |
| 探索的データ分析（R） | 8 |
| データ可視化 | 6, 9 |
| 動的計画法 | 1 |
| 組合せ論 | 1 |
| 正規化 | 7 |
| 差次的発現解析 | 7 |
| 機械学習 | 5, 6 |
| 情報量・エントロピー | 3 |
| ネットワークモデリング | 2 |
| スコアリング行列（PAM, BLOSUM） | 2, 4 |

### 7. Bioinformatics-specific concepts

| トピック | 出現ソース |
|---------|-----------|
| 配列アラインメント（局所/大域） | 1, 2, 3 |
| ゲノムアセンブリ（de Bruijn graph） | 1, 2 |
| 系統樹/系統推定 | 1, 2, 3 |
| モチーフ探索（Gibbs Sampler等） | 1, 2 |
| タンパク質構造予測 | 2, 7 |
| タンパク質相互作用予測/ネットワーク | 2, 7 |
| 遺伝子制御ネットワーク | 2 |
| RNA二次構造予測 | 2 |
| GWAS/QTL | 2 |
| 合成生物学 | 2, 6 |
| エピジェネティクス | 5, 6, 7 |
| マイクロバイオーム | 5, 6 |
| NGSテクノロジー（Illumina, Nanopore等） | 7 |
| BioPython | 4 |
| DNA/タンパク質配列操作 | 10 |
| AT含量/GC含量 | 1, 10 |
| ゲノミックレンジ操作（BEDTools） | 8 |
| Variant Analysis | 6, 7 |
| Single Cell解析 | 5, 6 |
| 空間オミクス | 5 |
| 薬理ゲノミクス | 5 |
| AlphaFold | 7 |
| メタゲノミクス | 6, 7 |
| 質量分析 | 1, 7 |

### 8. Collaboration & sharing

| トピック | 出現ソース |
|---------|-----------|
| Git/GitHub | 4, 8 |
| グループプロジェクト | 4 |
| コミュニティビルディング | 6 |
| トレーニング教材への貢献 | 6 |
| 公共リポジトリへのデータ提出 | 7 |
| FAIR principles | 6 |
| 再現可能な研究の実践 | 5, 8 |

---

## 全体的な観察

### カバレッジが厚いカテゴリ（多くのソースで扱われている）
1. **Programming fundamentals** — 10ソース中8ソースが直接扱う（Python基礎が圧倒的多数）
2. **Analysis pipelines** — 10ソース中9ソースが具体的ワークフローを含む（RNA-seqが最頻出）
3. **Bioinformatics-specific concepts** — 全ソースが何らかの形で扱う（配列アラインメントが最頻出）
4. **Statistics & data analysis** — 大学コース（Sources 1-3）が特に手厚い

### カバレッジが薄いカテゴリ（少数のソースでのみ扱われている）
1. **Software engineering practices** — 4ソースのみ（CSHL, GTN, Buffalo, Jones）がGit/テスト/デバッグを明示的に扱う
2. **Infrastructure** — 4ソースのみがUnix/HPC/環境構築を明示的に扱う
3. **Collaboration & sharing** — 3ソースのみがFAIR/公開リポジトリ/チーム開発を明示的に扱う

### 本書（AIエージェントと学ぶバイオインフォマティクスプログラミングの作法）との関係
上記調査から、既存カリキュラムでは以下が体系的に不足していることが確認された:
- **Software engineering practices**（テスト、デバッグ、リンター、型注釈、CI/CD）— 既存教育では断片的
- **Infrastructure**（環境構築、パッケージ管理、コンテナ、HPC/クラウド）— 既存教育では付随的
- **Collaboration & sharing**（Git、コードレビュー、ドキュメンテーション、コード公開）— 既存教育では周辺的
- **AIエージェントとの協働** — 全10ソースで体系的に扱うものは皆無（CSHLが2025年にAI-assisted codingを1セッション導入した程度）

これらはまさに本書の主要テーマであり、既存の教育資源との明確な補完関係を示している。
