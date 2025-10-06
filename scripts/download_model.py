"""Download Hugging Face model locally to ./models for offline use.

Run this on a machine with internet access, then commit the downloaded
artifacts via Git LFS.

Usage (PowerShell):
    py -3.11 scripts\\download_model.py --model distilbert-base-multilingual-cased \
            --out-dir models\\distilbert-base-multilingual-cased
"""

from pathlib import Path
import argparse
from transformers import AutoTokenizer, AutoModel  # type: ignore


def download(model_name: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Download tokenizer and save locally
    tok = AutoTokenizer.from_pretrained(model_name)
    tok.save_pretrained(out)

    # Download base model (encoder) and save locally
    model = AutoModel.from_pretrained(model_name)
    model.save_pretrained(out)

    print(f"Saved model and tokenizer to: {out.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="distilbert-base-multilingual-cased")
    parser.add_argument("--out-dir", default="models/distilbert-base-multilingual-cased")
    args = parser.parse_args()
    download(args.model, args.out_dir)
