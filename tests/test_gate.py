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


def test_gate_exit_code_is_zero_when_the_catalogue_is_clean():
    proc = subprocess.run([sys.executable, "gate.py", "--quiet"], cwd=ROOT,
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PASS" in proc.stdout


def test_finding_renders_readably():
    f = Finding("error", "L4", "Some Card", "Some rule", "something is wrong")
    assert "Some Card :: Some rule" in str(f)
