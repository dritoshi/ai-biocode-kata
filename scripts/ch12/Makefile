# リファレンスゲノムの取得とインデックス構築
# 小規模パイプラインでのmake活用例

GENOME_URL := https://ftp.ensembl.org/pub/release-111/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
GENOME_DIR := data/raw/genome
GENOME_FA := $(GENOME_DIR)/GRCh38.fa
GENOME_INDEX := $(GENOME_DIR)/GRCh38.fa.fai

.PHONY: all clean

all: $(GENOME_INDEX)

# ゲノムFASTAのダウンロード
$(GENOME_FA).gz:
	mkdir -p $(GENOME_DIR)
	curl -L -o $@ $(GENOME_URL)

# 解凍
$(GENOME_FA): $(GENOME_FA).gz
	gunzip -k $<

# samtools indexの構築
$(GENOME_INDEX): $(GENOME_FA)
	samtools faidx $<

clean:
	rm -f $(GENOME_FA) $(GENOME_FA).gz $(GENOME_INDEX)
