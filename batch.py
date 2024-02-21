import argparse
import logging
import os
import subprocess

limit = None
preview = False

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)
log = logging.getLogger()


def main():
    args = _parse_args()
    for model in _iter_models(args):
        _import_results(model, args)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--limit",
        metavar="N",
        help="Limit batch to N models",
        type=int,
        default=limit,
    )
    p.add_argument(
        "--preview",
        help="show models without importing them",
        action="store_true",
        default=preview,
    )
    return p.parse_args()


def _iter_models(args):
    count = 0
    for model in _evaluated_models():
        if args.limit is not None and args.limit == count:
            log.info("Reached limit of %s, stopping", args.limit)
            break
        yield model
        count += 1


def _evaluated_models():
    p = subprocess.Popen(
        "python import.py --list-models",
        stdout=subprocess.PIPE,
        shell=True,
        text=True,
    )
    assert p.stdout
    return [line.strip() for line in p.stdout.readlines()]


def _import_results(model, args):
    if args.preview:
        log.info("Will import results for %s", model)
        return
    log.info("Importing results for %s", model)
    try:
        subprocess.check_output(
            f"gage run import model='{model}' -y",
            shell=True,
            text=True,
            stderr=subprocess.STDOUT,
            cwd=os.getenv("PARENT_PWD"),
        )
    except subprocess.CalledProcessError as e:
        log.error(e.output)


if __name__ == "__main__":
    main()
