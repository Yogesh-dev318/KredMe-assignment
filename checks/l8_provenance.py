"""L8 — provenance and confidence. Who says so, and can I read it myself?

Two separate questions:
  * is there a source_url pointing at the ISSUER's own document?
  * does the rule carry an explicit `confidence`?

The second one matters more than it looks. The app reads `confidence` with a
default of 'high' (credit_card.dart). A rule that omits the key therefore
presents to the user as high-confidence — so a MISSING confidence is worse than
a low one.
"""
from . import Finding

NAME = "L8"
TITLE = "provenance & confidence"

AGGREGATORS = ("cardexpert", "cardinsider", "paisabazaar", "bankbazaar",
               "creditcardz", "technofino", "wikipedia")


def run(cards, ctx):
    out = []
    for entry in cards:
        card = entry.get("card") or {}
        name = card.get("card_name", "<unnamed>")
        for rule in entry.get("reward_rules") or []:
            rname = rule.get("rule_name", "<unnamed>")
            url = (rule.get("source_url") or "").lower()

            if not url:
                out.append(Finding("warn", NAME, name, rname, "no source_url — nobody can check this rate"))
            elif any(a in url for a in AGGREGATORS):
                out.append(Finding("error", NAME, name, rname,
                                   f"source is an aggregator, not the issuer: {url}"))

            if rule.get("confidence") is None:
                out.append(Finding("warn", NAME, name, rname,
                                   "no confidence key — the app defaults to 'high', so this "
                                   "unverified rule presents to the user as verified"))
    return out
