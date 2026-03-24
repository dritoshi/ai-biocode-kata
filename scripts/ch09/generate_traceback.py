"""§9 デバッグの技術 — Tracebackのサンプル生成.

意図的にエラーを発生させ、典型的なtracebackを出力する。
"""


def parse_bed_line(line: str) -> tuple[str, int, int]:
    """BED形式の1行をパースする."""
    fields = line.strip().split("\t")
    chrom = fields[0]
    start = int(fields[1])
    end = int(fields[2])
    return chrom, start, end


def load_bed_file(path: str) -> list[tuple[str, int, int]]:
    """BEDファイルを読み込む."""
    records = []
    with open(path) as f:
        for line in f:
            record = parse_bed_line(line)
            records.append(record)
    return records


def calculate_lengths(records: list[tuple[str, int, int]]) -> list[int]:
    """各レコードの長さを計算する."""
    return [end - start for _, start, end in records]


if __name__ == "__main__":
    # 存在しないファイルを読み込もうとしてエラーを発生させる
    records = load_bed_file("data/regions.bed")
    lengths = calculate_lengths(records)
    print(f"Average length: {sum(lengths) / len(lengths):.1f}")
