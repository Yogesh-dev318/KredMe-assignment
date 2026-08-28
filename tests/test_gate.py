"""Tests for the card-data gate.

These pass today. That is the point of the exercise.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from checks import Finding, l1_schema, l4_numeric, l8_provenance  # noqa: E402


def load_cards():
    with open(os.path.join(ROOT, "data", "cards.json")) as fh:
        return json.load(fh)


def ctx():
    with open(os.path.join(ROOT, "data", "app_categories.json")) as fh:
        return {"categories": json.load(fh)["categories"]}


def test_l1_accepts_the_shipped_catalogue():
    findings = l1_schema.run(load_cards(), ctx())
    assert [f for f in findings if f.level == "error"] == []


def test_l4_flags_a_percentage_typed_into_a_fraction_field():
    card = {"card": {"card_name": "Test", "base_reward_rate": 0.01},
            "reward_rules": [{"rule_name": "2% back", "reward_type": "cashback_pct", "reward_rate": 2.0}]}
    findings = l4_numeric.run([card], ctx())
    assert any("FRACTION" in f.message for f in findings)


def test_l4_accepts_a_normal_cashback_rate():
    card = {"card": {"card_name": "Test", "base_reward_rate": 0.01},
            "reward_rules": [{"rule_name": "2% back", "reward_type": "cashback_pct", "reward_rate": 0.02}]}
    findings = l4_numeric.run([card], ctx())
    assert [f for f in findings if f.level == "error"] == []


def test_l8_flags_an_aggregator_source():
    card = {"card": {"card_name": "Test"},
            "reward_rules": [{"rule_name": "r", "confidence": "high",
                              "source_url": "https://www.cardexpert.in/some-card/"}]}
    findings = l8_provenance.run([card], ctx())
    assert any("aggregator" in f.message for f in findings)


def test_l4_reports_bad_rows_even_when_a_later_rule_is_malformed():
    # Regression for the Altura incident: a string reward_rate on one card used
    # to crash L4 mid-run, silently discarding the 200%-cashback error it had
    # already found on an earlier card.
    cards = [
        {"card": {"card_name": "Altura-like", "base_reward_rate": 0.01},
         "reward_rules": [{"rule_name": "200% back", "reward_type": "cashback_pct", "reward_rate": 2.0}]},
        {"card": {"card_name": "Scapia-like", "base_reward_rate": 0.01},
         "reward_rules": [{"rule_name": "string rate", "reward_type": "cashback_pct", "reward_rate": "2%"}]},
    ]
    findings = l4_numeric.run(cards, ctx())
    assert any("FRACTION" in f.message for f in findings)
    assert any("not a number" in f.message for f in findings)


def test_gate_fails_closed_when_a_check_crashes(tmp_path):
    # Data of a shape no check anticipates must yield FAIL, never a silent PASS.
    bad = tmp_path / "cards.json"
    bad.write_text(json.dumps(["not a card entry at all"]))
    proc = subprocess.run([sys.executable, "gate.py", "--quiet", "--data", str(bad)],
                          cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "FAIL" in proc.stdout


def test_gate_blocks_the_shipped_catalogue():
    # The shipped catalogue contains known-bad rows (Altura 200% cashback,
    # Scapia's "2%" string, zero base rates). The gate must block it.
    proc = subprocess.run([sys.executable, "gate.py", "--quiet"], cwd=ROOT,
                          capture_output=True, text=True)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "FAIL" in proc.stdout


def test_finding_renders_readably():
    f = Finding("error", "L4", "Some Card", "Some rule", "something is wrong")
    assert "Some Card :: Some rule" in str(f)
