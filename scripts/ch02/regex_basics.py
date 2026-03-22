"""正規表現の基本操作 — バイオインフォマティクスでの実例."""

import re


def extract_accession(header: str) -> str | None:
    """FASTAヘッダからアクセッション番号を抽出する.

    ``re.search()`` を使い、``>`` の直後に続く
    「英数字＋ピリオド＋数字」のパターンを探す。

    Parameters
    ----------
    header : str
        FASTAヘッダ行（例: ``">NM_007294.4 Homo sapiens BRCA1"``）。

    Returns
    -------
    str | None
        アクセッション番号。マッチしなければ None。
    """
    match = re.search(r">(\w+\.\d+)", header)
    return match.group(1) if match else None


def extract_gene_id(attribute: str) -> str | None:
    """GFF3/GTF attribute文字列からgene_idを抽出する.

    ``gene_id "..."`` のパターンから引用符内の値を取得する。

    Parameters
    ----------
    attribute : str
        GFF3/GTFの第9カラム（attributes）文字列。

    Returns
    -------
    str | None
        gene_idの値。マッチしなければ None。
    """
    match = re.search(r'gene_id "([^"]+)"', attribute)
    return match.group(1) if match else None


def extract_all_accessions(fasta_text: str) -> list[str]:
    """FASTA文字列全体から全アクセッション番号を一括抽出する.

    ``re.findall()`` を使い、キャプチャグループにマッチした
    文字列のリストを返す。

    Parameters
    ----------
    fasta_text : str
        複数レコードを含むFASTA形式の文字列。

    Returns
    -------
    list[str]
        アクセッション番号のリスト。
    """
    return re.findall(r">(\w+\.\d+)", fasta_text)


def convert_chrom_ucsc_to_ensembl(chrom: str) -> str:
    """染色体名をUCSC形式からEnsembl形式に変換する.

    ``re.sub()`` で先頭の ``chr`` を除去する（例: ``"chr1"`` → ``"1"``）。

    Parameters
    ----------
    chrom : str
        UCSC形式の染色体名（例: ``"chr1"``, ``"chrX"``）。

    Returns
    -------
    str
        Ensembl形式の染色体名。``chr`` がなければそのまま返す。
    """
    return re.sub(r"^chr", "", chrom)


def convert_chrom_ensembl_to_ucsc(chrom: str) -> str:
    """染色体名をEnsembl形式からUCSC形式に変換する.

    先頭に ``chr`` がなければ付加する（例: ``"1"`` → ``"chr1"``）。

    Parameters
    ----------
    chrom : str
        Ensembl形式の染色体名（例: ``"1"``, ``"X"``）。

    Returns
    -------
    str
        UCSC形式の染色体名。既に ``chr`` で始まっていればそのまま返す。
    """
    if re.match(r"^chr", chrom):
        return chrom
    return f"chr{chrom}"
