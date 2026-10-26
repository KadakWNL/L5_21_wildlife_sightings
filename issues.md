# Lab 5 — Static Code Analysis: Issue Log

**File analysed:** `wildlife_sightings.py`
**Tools:** Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1 (Python 3.13.15)
**Line numbers refer to the original file** (commit `fd57197`).

## Before / after

| Tool | Before | After |
|---|---|---|
| Pylint | 3.46/10, 17 messages | **10.00/10**, 0 messages |
| Bandit | 3 issues (1 High, 1 Medium, 1 Low) | **0 issues** |
| Flake8 | 6 violations | **0 violations** |

Raw output is in [`reports/before/`](reports/before/) and [`reports/after/`](reports/after/).

## Issues found and fixed

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Weak MD5 hash (Bandit B324) | Security | 15 | `hashlib.md5()` derives the public observer ID. MD5 is broken for collision and preimage resistance, so IDs could be forged or collided. | Replaced with `hashlib.sha256(observer.encode("utf-8")).hexdigest()[:6]`. The 6-hex-digit output format is unchanged. |
| SQL injection (Bandit B608) | Security | 9 | The INSERT was built by `.format()`-ing `species`, `zone` and `count` straight into the SQL text. A value such as `x'); DROP TABLE sightings;--` executes as SQL. | Used a parameterised query — `VALUES (?, ?, ?)` with a tuple — so SQLite treats the values as data, never as code. |
| Mutable default argument (Pylint W0102) | Bug | 8 | `extras={}` is created once at function definition and reused by every call, so totals leaked between unrelated calls. | Default changed to `None`, then `if extras is None: extras = {}` inside the function. |
| `assert` used for control flow (Bandit B101) | Bug | 36 | `assert len(totals) == 3` is stripped when the file is run with `python -O`, silently disabling the check. | Replaced with `if len(totals) != 3: raise ValueError(...)`, which survives optimisation. |
| Parameter shadows module `conn` (Pylint W0621) | Bug / maintainability | 8, 18, 26 | Each function took a `conn` parameter that shadowed the module-level `conn`, making it ambiguous which database a call touched. | Removed the parameter and kept one module-level connection, named `DB`. |
| Unnecessary `else` after `return` (Pylint R1705) | Style | 20–23 | The `else` branch only ran when the `if` had already returned, adding a level of nesting for no reason. | De-indented the `return row[0]` to follow the `if` directly. |
| camelCase function names (Pylint C0103) | Style | 8, 14, 18 | `logSighting`, `observerId`, `zoneSummary` break PEP 8's `snake_case` convention for functions. | Renamed to `log_sighting`, `observer_id`, `zone_summary`. |
| Missing docstrings (Pylint C0114, C0116) | Style | 1, 8, 14, 18, 26, 32 | No module docstring and no docstring on any of the six functions. | Added a module docstring and a one-line docstring per function stating purpose, not restating the code. |
| `%`/`.format` string building (Pylint C0209) | Style | 9 | The query was assembled with `.format()` rather than an f-string or parameters. | Resolved by the parameterised query — nothing is formatted into the SQL text at all. |
| Lines over the limit (Pylint C0301, Flake8 E501) | Style | 5, 9, 19, 27 | Lines of 103, 117, 93 and 96 characters exceeded Pylint's 100 and Flake8's 79. | Rewrapped the schema into a triple-quoted string and split the remaining calls across lines. |
| Ambiguous variable name `l` (Flake8 E741) | Style | 28 | Single-letter `l` is visually indistinguishable from `1` in most fonts. | Renamed to `lowest`. |
| Missing whitespace around `=` (Flake8 E225) | Style | 28 | `l=min(...)` had no spaces around the assignment. | Spaced correctly when the line was rewritten. |

## Behavioural changes (intentional)

Not flagged by the tools, but worth stating because the output is no longer byte-identical:

- **Observer ID changes** — `observer_id("Arun")` now prints `e753d3` instead of `5455c3`, because SHA-256 replaced MD5. Length and format are the same; only the digest differs.
- **`rarest()` on an empty table** — previously `min()` raised `ValueError` on an empty result set; it now returns `None`, matching the `or None if empty` contract in its docstring.
- **`main()` guarded** — moved under `if __name__ == "__main__":` so importing the module no longer runs the demo.
