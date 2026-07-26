"""パイプライン開始前に入力を検証するfail-fastの例."""

from pathlib import Path


def run_pipeline(config: dict[str, str]) -> None:
    """パイプラインの実行. 入力の検証を全て先に行う."""
    # 先に全ての入力を検証する（fail-fast）
    input_path = Path(config["input"])
    reference_path = Path(config["reference"])
    output_dir = Path(config["output_dir"])

    if not input_path.exists():
        raise FileNotFoundError(
            f"入力ファイルが見つかりません: {input_path}"
        )
    if not reference_path.exists():
        raise FileNotFoundError(
            f"リファレンスが見つかりません: {reference_path}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    # 検証を通過してから時間のかかる処理を開始する
    return None
