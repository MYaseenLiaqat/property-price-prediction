# DEVELOPMENT RULES — PropertyAI Lahore

> These rules govern **how** work is done in this repository. They are binding for human
> developers and AI coding agents. `PROJECT_SCOPE.md` defines **what** the project is and has
> final authority; this document defines **how** to change it safely.

## Rule 1 — Read project instructions first

Before modifying code, an AI coding agent must read:

- `PROJECT_SCOPE.md`
- `PROJECT_ROADMAP.md`
- `ARCHITECTURE.md`
- `DEVELOPMENT_RULES.md`
- `DATA_POLICY.md`
- `DESIGN_GUIDELINES.md`

For phase-specific work, also read the relevant documents inside `docs/`.
Do not begin editing until this is done. If a newer request conflicts with these documents,
apply the Scope Change Rule in `PROJECT_SCOPE.md` rather than ignoring the document.

## Rule 2 — Stay within the current phase

Do not implement future-phase functionality unless explicitly requested. The roadmap defines
entry and exit criteria per phase; if the current phase's exit criteria are not yet met, finish
them first. If a requested task belongs to a later phase, note it and stop.

## Rule 3 — No scope creep

If you notice an unrelated improvement:

- **Do not implement it automatically.**
- Record it as a suggested future item (for example in `docs/DECISIONS.md` or the roadmap).

Examples of scope creep: adding a login page, adding another city, adding a chat assistant,
swapping the model framework, or adding a database — none of these are "small fixes".

## Rule 4 — Inspect before modifying

Before changing a file:

- inspect it
- understand its purpose
- preserve existing working behaviour
- make the smallest appropriate change

Never overwrite a file you have not read. If a file has no tests, at least verify it still runs.

## Rule 5 — Do not rewrite the project unnecessarily

Avoid large rewrites when a targeted change is sufficient. Prefer minimal diffs, and preserve the
formatting and conventions of the surrounding code. A refactor must have a stated reason and must
not change behaviour unless that is the intent.

## Rule 6 — No fake completion

Do not report scaffolding as completed functionality.

**Bad:**

> "Zameen integration completed"

when only a collector skeleton exists.

**Good:**

> "Zameen collector scaffold created; no live data imported."

## Rule 7 — No fabricated data

Never create fake production data. Test fixtures must be clearly labelled as test fixtures (for
example `data/reference/smoke_test.csv`). Never present synthetic values as real market data, and
never write generated rows into a "real" dataset file.

## Rule 8 — Test after changes

Run appropriate validation after modifications, then report:

- what changed
- what was tested
- the test result
- remaining limitations

Do not claim success you did not actually observe. If you cannot run a test, say so explicitly
instead of implying it passed.

## Rule 9 — Preserve provenance

Data source and collection date must not be lost. No transform may drop `source`, `source_url`,
`listing_id` or `date_collected`. If a derived file drops them, it must reference the file that
holds them.

## Rule 10 — Avoid unnecessary dependencies

Only add packages that serve a demonstrated project requirement. Prefer the standard library and
already-present dependencies. If a new dependency is truly required, name it, justify it, and
check it is not already available.

## Rule 11 — Keep secrets out of Git

Never hardcode or commit:

- API keys
- passwords
- tokens
- credentials

Use environment variables or untracked local configuration. Never commit real credentials, even
in examples.

## Rule 12 — Ask before major architectural changes

Do not independently introduce:

- databases
- cloud infrastructure
- microservices
- authentication
- payment systems
- major frameworks

without explicit approval. These are project-shaping decisions, not implementation details:
propose the change, explain the need, and wait.

## Rule 13 — One milestone at a time

Do not continue into the next milestone automatically after completing the current task. Finish,
validate, report, and **stop**. Wait for the next instruction.

## Rule expansions: examples

- **Rule 2 example:** do not add comparable retrieval while working on Phase 4 dataset
  construction.
- **Rule 3 example:** noticing the API lacks error handling is not permission to add it now —
  record it and continue.
- **Rule 5 example:** improving one function is fine; restructuring the training script is not,
  unless asked.

## Working with data and models

- Never mutate a raw file; write a new derived file instead.
- Keep the pipeline scripted under `scripts/` so a result can be reproduced.
- Record dataset rows, date ranges and metrics alongside every model artifact.
- If a result looks "too good", suspect leakage before celebrating.

## When to ask instead of act

Ask (do not assume) when a request would:

- change scope, geography or property type;
- introduce infrastructure, a database or a new framework;
- alter how sale and rent are combined;
- change validation or de-duplication in a way that affects results.

When unsure, propose the smallest step and wait for confirmation.

## Git and repository hygiene

- Prefer small, focused commits.
- Do not commit generated datasets, model binaries or secrets unless the project explicitly
  decides to track them.
- Do not delete files you do not understand; ask first.
- Keep `requirements.txt` in sync when a dependency is approved.

## Definition of Done (for any task)

A task is done only when:

1. it stays within the current phase and scope;
2. the change is the smallest reasonable one;
3. the affected files were inspected before editing;
4. it was validated (tested, or clearly shown to run);
5. the report states changes, tests, results and limitations.

## Never do (without explicit instruction)

- expand to another city or property type
- add synthetic data to a real dataset
- describe asking prices as transaction prices
- add a database, auth, payments or deployment configuration
- redesign the frontend or add CSS/JS ahead of Phase 10
- merge sale and rent into one model
- report scaffolded code as working functionality

## Reporting format

Every completed task should report: changes made, files touched, what was tested, test results and
known limitations. Keep it factual.
