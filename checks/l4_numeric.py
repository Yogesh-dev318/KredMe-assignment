"""L4 — numeric plausibility and units.

Is the number the right SIZE, in the right UNIT?

cashback_pct is stored as a FRACTION: 0.02 means 2%. A value of 2.0 in that
field means 200% and is almost always someone typing the percentage into a
fraction field.

points_per_spend is stored as points earned per `reward_unit_spend` rupees.
The per-rupee rate is what has to be plausible, so the rate is normalised by
the unit before it is judged.
"""
from . import Finding

NAME = "L4"
TITLE = "numeric plausibility & units"

MAX_CASHBACK_FRACTION = 0.30      # 30% back is already extraordinary
MAX_POINTS_PER_RUPEE = 1.0
MAX_MULTIPLIER = 20.0


def run(cards, ctx):
    out = []
    for entry in cards:
        card = entry.get("card") or {}
        name = card.get("card_name", "<unnamed>")

        base = card.get("base_reward_rate")
        if not base:
            out.append(Finding("error", NAME, name, "",
                               "base_reward_rate is 0 or absent — the app renders this card as "
                               "'0.00% base' and ranks it last"))

        for rule in entry.get("reward_rules") or []:
            rname = rule.get("rule_name", "<unnamed>")
            rate = rule.get("reward_rate")
            rtype = rule.get("reward_type")

            if rtype in ("cashback_pct", "points_per_spend", "multiplier") and not isinstance(rate, (int, float)):
                out.append(Finding("error", NAME, name, rname,
                                   f"reward_rate is {rate!r} — not a number, so its size cannot be judged"))
                continue

            if rtype == "cashback_pct":
                if rate > MAX_CASHBACK_FRACTION:
                    out.append(Finding("error", NAME, name, rname,
                                       f"cashback_pct is {rate} — the field is a FRACTION, so this "
                                       f"renders as {rate * 100:.0f}%"))

            elif rtype == "points_per_spend":
                unit = rule.get("reward_unit_spend")
                if not isinstance(unit, (int, float)) or not unit:
                    out.append(Finding("error", NAME, name, rname,
                                       f"reward_unit_spend is {unit!r} — the rate cannot be normalised"))
                    continue
                per_rupee = rate / unit
                if per_rupee > MAX_POINTS_PER_RUPEE:
                    out.append(Finding("error", NAME, name, rname,
                                       f"{rate} points per Rs{unit} = {per_rupee:.2f} points per rupee"))

            elif rtype == "multiplier":
                if rate > MAX_MULTIPLIER:
                    out.append(Finding("error", NAME, name, rname, f"{rate}x multiplier is implausible"))

    return out
