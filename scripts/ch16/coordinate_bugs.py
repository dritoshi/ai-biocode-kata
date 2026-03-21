"""座標変換のバグ版・修正版 — Off-by-one エラーのデモ."""


def bed_to_gff_buggy(
    chrom: str, bed_start: int, bed_end: int
) -> tuple[str, int, int]:
    """BED座標をGFF座標に変換する（バグあり版）.

    BEDは0-based半開区間、GFFは1-based閉区間。
    このバグ版は start の +1 を忘れている。

    Parameters
    ----------
    chrom : str
        染色体名。
    bed_start : int
        BED形式の開始位置（0-based）。
    bed_end : int
        BED形式の終了位置（半開区間）。

    Returns
    -------
    tuple[str, int, int]
        (染色体名, GFF開始, GFF終了)。ただし開始が正しくない。
    """
    # バグ: BED→GFF変換で start に +1 しなければならないのを忘れている
    gff_start = bed_start  # 本来は bed_start + 1
    gff_end = bed_end
    return (chrom, gff_start, gff_end)


def bed_to_gff_correct(
    chrom: str, bed_start: int, bed_end: int
) -> tuple[str, int, int]:
    """BED座標をGFF座標に正しく変換する.

    BED: 0-based半開区間 [start, end)
    GFF: 1-based閉区間 [start, end]

    例: BED (0, 10) → GFF (1, 10)
        BED (5, 6)  → GFF (6, 6)  ← 1塩基の場合

    Parameters
    ----------
    chrom : str
        染色体名。
    bed_start : int
        BED形式の開始位置（0-based）。
    bed_end : int
        BED形式の終了位置（半開区間）。

    Returns
    -------
    tuple[str, int, int]
        (染色体名, GFF開始, GFF終了)。
    """
    gff_start = bed_start + 1
    gff_end = bed_end
    return (chrom, gff_start, gff_end)


def gff_to_bed_correct(
    chrom: str, gff_start: int, gff_end: int
) -> tuple[str, int, int]:
    """GFF座標をBED座標に正しく変換する.

    GFF: 1-based閉区間 [start, end]
    BED: 0-based半開区間 [start, end)

    例: GFF (1, 10) → BED (0, 10)
        GFF (6, 6)  → BED (5, 6)

    Parameters
    ----------
    chrom : str
        染色体名。
    gff_start : int
        GFF形式の開始位置（1-based）。
    gff_end : int
        GFF形式の終了位置（閉区間）。

    Returns
    -------
    tuple[str, int, int]
        (染色体名, BED開始, BED終了)。
    """
    bed_start = gff_start - 1
    bed_end = gff_end
    return (chrom, bed_start, bed_end)


def extract_subsequence(
    sequence: str,
    start: int,
    end: int,
    coordinate_system: str = "bed",
) -> str:
    """座標系を指定して部分配列を抽出する.

    Parameters
    ----------
    sequence : str
        全体の塩基配列。
    start : int
        開始位置。
    end : int
        終了位置。
    coordinate_system : str
        "bed"（0-based半開）または "gff"（1-based閉）。

    Returns
    -------
    str
        抽出された部分配列。

    Raises
    ------
    ValueError
        不明な座標系が指定された場合。
    """
    if coordinate_system == "bed":
        # BED: 0-based半開 → Pythonスライスとそのまま対応
        return sequence[start:end]
    elif coordinate_system == "gff":
        # GFF: 1-based閉 → Pythonスライスに変換
        return sequence[start - 1 : end]
    else:
        msg = f"不明な座標系: {coordinate_system!r}（'bed' または 'gff' を指定）"
        raise ValueError(msg)


def validate_coordinates(
    start: int,
    end: int,
    seq_length: int,
    coordinate_system: str = "bed",
) -> bool:
    """座標が有効範囲内かを検証する.

    Parameters
    ----------
    start : int
        開始位置。
    end : int
        終了位置。
    seq_length : int
        配列の全長。
    coordinate_system : str
        "bed" または "gff"。

    Returns
    -------
    bool
        座標が有効なら True。

    Raises
    ------
    ValueError
        座標が範囲外または不正な場合。
    """
    if coordinate_system == "bed":
        if start < 0:
            msg = f"BED start は 0 以上: {start}"
            raise ValueError(msg)
        if end > seq_length:
            msg = f"BED end が配列長 {seq_length} を超過: {end}"
            raise ValueError(msg)
        if start > end:
            msg = f"BED start ({start}) > end ({end})"
            raise ValueError(msg)
    elif coordinate_system == "gff":
        if start < 1:
            msg = f"GFF start は 1 以上: {start}"
            raise ValueError(msg)
        if end > seq_length:
            msg = f"GFF end が配列長 {seq_length} を超過: {end}"
            raise ValueError(msg)
        if start > end:
            msg = f"GFF start ({start}) > end ({end})"
            raise ValueError(msg)
    else:
        msg = f"不明な座標系: {coordinate_system!r}"
        raise ValueError(msg)
    return True
