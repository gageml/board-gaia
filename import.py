import argparse
import json
import logging
import os
import sys
import tempfile

from datasets import load_dataset

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)
log = logging.getLogger()

model = None
eval_results = "gaia-benchmark/results_public"
year_version = "2023"

CACHE_DIR = os.path.join(tempfile.gettempdir(), "gage-board-gaia-data")


def main():
    args = _parse_args()
    log.info("Loading GAIA benchmark results")
    data = load_dataset(eval_results, year_version, cache_dir=CACHE_DIR)
    if args.list_models:
        _show_models_and_exit(data)
    assert args.model
    result = _model_result(args.model, data)
    log.info("Saving results for '%s'", args.model)
    save_summary(result)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-m", "--model", default=model, help="Model to import")
    p.add_argument(
        "-l", "--list-models", action="store_true", help="List available models"
    )
    args = p.parse_args()
    if not args.model and not args.list_models:
        raise SystemExit("Specify either --model or --list-models")
    return args


def _show_models_and_exit(data):
    for name in sorted(row["model"] for row in data["test"]):
        print(name)
    raise SystemExit()


def _model_result(model_name, data):
    for row in data["test"]:
        if row["model"].strip() == model_name:
            return row
    raise SystemExit(f"Model '{model_name}' not found")


def save_summary(result):
    summary = {
        "run": {"label": model},
        "metrics": {
            "score": result["score"] * 100,
            "score_level1": result["score_level1"] * 100,
            "score_level2": result["score_level2"] * 100,
            "score_level3": result["score_level3"] * 100,
        },
        "attributes": {
            "model": result["model"].strip(),
            "organisation": result["organisation"],
            "url": result["url"],
            "model_family": result["model_family"],
        },
    }
    with open("summary.json", "w") as f:
        json.dump(summary, f)


if __name__ == "__main__":
    main()
