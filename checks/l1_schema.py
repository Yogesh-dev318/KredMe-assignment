"""L1 — schema and shape. Can the app read this file at all?"""
from . import Finding

NAME = "L1"
TITLE = "schema & shape"

REQUIRED_CARD_KEYS = ("id", "card_name", "issuer", "network")
REQUIRED_RULE_KEYS = ("rule_name", "reward_type", "reward_rate")


def run(cards, ctx):
    out = []
    for entry in cards:
        card = entry.get("card") or {}
        name = card.get("card_name", "<unnamed>")
        for key in REQUIRED_CARD_KEYS:
            if card.get(key) in (None, ""):
                out.append(Finding("error", NAME, name, "", f"card is missing required key '{key}'"))
        for rule in entry.get("reward_rules") or []:
            for key in REQUIRED_RULE_KEYS:
                if key not in rule:
                    out.append(Finding("error", NAME, name, rule.get("rule_name", "<unnamed>"),
                                       f"reward rule is missing required key '{key}'"))
    return out
