"""L6 — engine reachability. Will the app ever actually fire this rule?

A bonus rule only fires when its `category_ref` resolves to a category the app
knows about. The app's vocabulary is a short canonical list; anything the
pipeline writes that is not in that list is dead weight — the rule ships, the
user never earns it, and nothing anywhere reports a problem.

The vocabulary lives in the app repo, so ctx supplies it.
"""
from . import Finding

NAME = "L6"
TITLE = "engine reachability"


def run(cards, ctx):
    out = []
    vocabulary = ctx["categories"]
    if vocabulary is None:
        # No app checkout (every scheduled CI run). Documented as non-fatal:
        # skip the check rather than crash.
        return out
    known = {c.lower() for c in vocabulary}

    for entry in cards:
        card = entry.get("card") or {}
        name = card.get("card_name", "<unnamed>")
        for rule in entry.get("reward_rules") or []:
            ref = rule.get("category_ref")
            if not ref:
                continue
            if ref.strip().lower() not in known:
                out.append(Finding("warn", NAME, name, rule.get("rule_name", "<unnamed>"),
                                   f"category_ref {ref!r} is not one of the app's "
                                   f"{len(known)} categories — this rule can never fire"))
    return out
