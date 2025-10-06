"""Download Hugging Face model locally to ./models for offline use.

Run this on a machine with internet access, then commit the downloaded
artifacts via Git LFS.

Usage (PowerShell):
    py -3.11 scripts\\download_model.py --model distilbert-base-multilingual-cased \
            --out-dir models\\distilbert-base-multilingual-cased
"""

from pathlib import Path
import argparse
from huggingface_hub import snapshot_download  # type: ignore


def download(model_repo: str, out_dir: str, revision: str | None = None) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Download entire repo snapshot (config, tokenizer, vocab, weights)
    snapshot_download(
        repo_id=model_repo,
        revision=revision,
        local_dir=str(out),
        local_dir_use_symlinks=False,
        ignore_patterns=["*.msgpack", "*.h5", "*.onnx"],
    )

    expected = [
        out / "config.json",
        out / "tokenizer.json",
        out / "pytorch_model.bin",
    ]
    missing = [p.name for p in expected if not p.exists()]
    if missing:
        print(f"Warning: some expected files are missing: {missing}. Contents:")
        for p in out.iterdir():
            print(" -", p.name)
    else:
        print(f"Saved model snapshot to: {out.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="distilbert-base-multilingual-cased")
    parser.add_argument("--out-dir", default="models/distilbert-base-multilingual-cased")
    parser.add_argument("--revision", default=None)
    args = parser.parse_args()
    download(args.model, args.out_dir, args.revision)
