# Lab 5 — Reflection

> **Note:** the supplied handout PDF has no reflection section, so the four standard
> questions for this lab are answered below. Replace the prompts if the instructor
> circulates his own list.

## 1. Which tool produced the most useful findings, and why?

Bandit, because it was the only one that reported a **High**-severity issue. Pylint and
Flake8 between them produced more than twenty findings, but almost all were cosmetic —
names, docstrings, line lengths. Bandit flagged the MD5 use in `observer_id()` (B324), which
neither of the other tools considered a problem and which I had read past twice: the code
looks innocent because it is only deriving a short display ID, not storing passwords.
That is exactly the point — a broken hash is a broken hash regardless of how small the
output is, and a collision on a 6-character ID could let one observer's records be
attributed to another. Bandit's severity ordering also did the triage for me: fix the
High, then the Medium (SQL injection), then the Low.

## 2. Which fix was hardest, and why?

The `conn` shadowing fix (Pylint W0621) was harder than it looks. Pylint reported it on
three lines, but the real cost was deciding *which* `conn` should survive. The module
created a connection at import, and then every function also demanded one be passed in —
so there were two competing designs in the same file, and any caller could pass a
different database than the one the schema was created on. Removing the parameter and
keeping a single module-level `DB` was a three-line change that altered the signature of
every function, so `main()` had to be updated in four places too. It is the only fix that
touched more than the line it was reported on, which is a fair reminder that static
analysis reports symptoms, not designs.

The mutable default argument (`extras={}`) was the most instructive fix, even though it
was trivial to apply. It is a silent bug: `log_sighting("Leopard", ...)` returns a dict
that still holds every species logged by previous calls, so totals accumulate across the
whole process lifetime. Nothing in the output looks wrong until you call the function in
two unrelated places and compare.

## 3. What did the tools catch that reading the code did not?

The MD5 finding, mainly, and the `assert` one. Reading `assert len(totals) == 3` it is not
obvious that the check silently disappears under `python -O` — the code still runs, the
assertion just stops being a check, which is the worst failure mode: it fails open. Bandit
B101 names that mechanism explicitly.

The reverse also happened: reading the code found something no tool flagged. `rarest()`
calls `min()` on the result of a `GROUP BY`, so on an empty table it raises `ValueError`
instead of returning nothing. No tool reports this, because `min()` on a possibly-empty
list is not a lint rule. I added a guard and documented it in `issues.md` as a behavioural
change rather than an "issue fixed", to keep the table honest.

What Pylint contributed was volume and consistency — 17 messages on a 40-line file. Most
were trivial, but the score is a useful blunt instrument: 3.46/10 told me immediately that
the file was far from finished, before I had read a single message.

## 4. How would this change your workflow?

I would run Bandit and a syntax-level check (Flake8) on every save or pre-commit, and
Pylint in CI rather than in the loop — the style chatter per keystroke is noise, but the
security findings are never noise. The key change is ordering: fix security and
correctness first, then naming and formatting last, because renaming functions before
fixing the SQL injection would have meant resolving conflicts in lines I was about to
rewrite anyway.

Two things I would not do again: chase the Pylint score to 10.00 by suppressing messages,
and treat "the program runs" as evidence of correctness. Every security issue in this file
ran perfectly happily — SQL injection and MD5 produce output that looks entirely normal.
