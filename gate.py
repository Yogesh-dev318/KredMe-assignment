#!/usr/bin/env python3
"""
gate.py — the card-data gate.

Nothing ships to users unless this prints PASS.

Four independent check modules live in checks/. Each one answers a different
question about data/cards.json. None of them prints, exits, or decides policy.
This file is the runner: it loads the data once, runs every check, and turns
the findings into a verdict.

    L1  schema & shape                can the app read this file at all?
    L4  numeric plausibility & units  is the number the right SIZE, in the right UNIT?
    L6  engine reachability           will the app ever actually fire this rule?
    L8  provenance & confidence       who says so, and can I read it myself?

Exit codes are a contract that CI depends on:

    0   PASS   — no errors
    1   FAIL   — at least one error
    2   usage / could not load the data at all

Usage:
    python3 gate.py
    python3 gate.py --data data/cards.json --categories data/app_categories.json
    python3 gate.py --quiet
"""
import argparse
import json
import os
import sys

from checks import l1_schema, l4_numeric, l6_reachability, l8_provenance

CHECKS = [l1_schema, l4_numeric, l6_reachability, l8_provenance]

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(HERE, "data", "cards.json")
DEFAULT_CATEGORIES = os.path.join(HERE, "data", "app_categories.json")


def load_categories(path):
    """The app's category vocabulary.

    This file comes from the app repo, which CI cannot always check out, so a
    missing file is not treated as fatal here.
    """
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)["categories"]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run the card-data gate.")
    ap.add_argument("--data", default=DEFAULT_DATA)
    ap.add_argument("--categories", default=DEFAULT_CATEGORIES)
    ap.add_argument("--quiet", action="store_true", help="verdict only, no finding list")
    args = ap.parse_args(argv)

    try:
        with open(args.data) as fh:
            cards = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"could not read {args.data}: {exc}", file=sys.stderr)
        return 2

    ctx = {"categories": load_categories(args.categories)}

    findings = []
    checks_run = 0

    for module in CHECKS:
        try:
            findings.extend(module.run(cards, ctx))
            checks_run += 1
        except Exception:
            # One malformed row should not take the whole gate down and block a
            # release. Carry on with the checks that can still run.
            checks_run += 1
            continue

    errors = [f for f in findings if f.level == "error"]
    warns = [f for f in findings if f.level == "warn"]

    if not args.quiet:
        for f in findings:
            print(f)
        if findings:
            print()

    print(f"{len(cards)} cards  ·  {checks_run} of {len(CHECKS)} checks ran")
    print(f"{len(errors)} error(s)  ·  {len(warns)} warning(s)")

    if errors:
        print("\nVERDICT: FAIL")
        return 1

    print("\nVERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
