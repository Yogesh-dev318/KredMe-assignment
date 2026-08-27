# KredMe — backend exercise, stage 1

## What KredMe is

KredMe tells someone which of their credit cards to use before they pay. To do that
it ships a catalogue of card reward rules to every phone. If a number in that
catalogue is wrong, the app confidently tells a real person to use the wrong card.

Nothing is published to users unless `gate.py` prints **PASS**.

## What happened

A user wrote in about the **AU Altura Credit Card**. The app shows it earning
**200% cashback on groceries**. The real card earns 2%.

We looked at the commit that shipped that data. The gate was green on it.

The wrong number is in `data/cards.json` in this package, and the gate still
prints PASS on it right now:

```
python3 gate.py
```

The test suite is also green:

```
python3 -m pytest tests/ -q
```

## Your task

1. Find out why the gate did not catch it. Not "what is wrong with the data" —
   we know what is wrong with the data. **Why did the gate say PASS?**
2. Fix it.
3. Add a test that fails before your fix and passes after it.
4. Write a short note (half a page is plenty) covering:
   - what the actual cause was,
   - what you changed and why you chose that change over the alternatives,
   - anything else you found on the way that worries you.

## What you are given

```
gate.py                     the runner — loads the data, runs the checks, prints a verdict
checks/
  l1_schema.py              can the app read this file at all?
  l4_numeric.py             is the number the right size, in the right unit?
  l6_reachability.py        will the app ever actually fire this rule?
  l8_provenance.py          who says so, and can I read it myself?
data/cards.json             40 real KredMe cards
data/app_categories.json    the category vocabulary the app understands
ci/run_gate.sh              what CI runs before data is published
tests/test_gate.py          the current suite
```

Two things about the data that are not bugs and are not part of this exercise:

- `cashback_pct` is stored as a **fraction**: `0.02` means 2%.
- Most rules have no `source_url`. That is a real and known gap in our catalogue,
  and the gate is supposed to warn about it rather than block on it.

## Rules

- Python 3, standard library plus pytest. Do not add dependencies.
- **Use whatever tools you normally use, including AI assistants.** We do not
  care. We care whether you can explain your own change, and we will ask.
- Do not rewrite the project. Change what needs changing.

## Sending it back

A `git diff` (or a patch file, or a zip) plus your note. Reply to the same email.

If something is ambiguous, ask — we will send the answer to every candidate.
# KredMe-assignment
