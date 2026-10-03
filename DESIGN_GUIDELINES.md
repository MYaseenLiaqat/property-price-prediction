# DESIGN GUIDELINES — PropertyAI Lahore

> Future UI/UX reference. This is **not** an instruction to build the frontend now. Frontend work
> belongs to Phase 10 (`PROJECT_ROADMAP.md`). Do not add CSS, JS or a frontend framework during
> earlier phases.

## Product identity

- **Product:** PropertyAI Lahore.
- **Direction:** a professional real-estate analytics / valuation office.
- It should feel like a serious property intelligence platform — closer to a valuation desk or a
  market-research terminal than a generic SaaS template.

## Core UX areas

1. **Valuation Desk** — the primary workflow: describe a property, get an asking-price range.
2. **Comparable Properties** — real, locality-aware comparables behind the estimate.
3. **Market Intelligence** — locality-level summaries backed by data.
4. **Property Search** — filter and explore listings/reference data.
5. **Property Profile** — a single property's details, evidence and estimate.
6. **Market Trends** — asking-price movement over time.
7. **Data Quality** — coverage, freshness, provenance and limitations.

## Valuation workflow inputs (planned)

The main workflow should eventually accept:

- purpose (sale / rent)
- property type
- locality, society, phase, block
- area (with unit)
- bedrooms, bathrooms, floors
- condition
- parking, basement, servant quarter
- furnished
- corner, main road, park facing
- utilities where reliable (and "Unknown" when not known)

Do not force a user to guess values they cannot know; allow "Unknown".

## Output emphasis (planned)

Output should emphasise:

- estimated **asking-price range**
- point estimate
- comparable count
- data freshness
- confidence / data quality
- relevant market context

**Avoid false precision.** Never show a single confident number with no range, no data basis and
no caveats. Make uncertainty visible rather than hidden.

## Tone and presentation principles

- Show the evidence behind a number, not just the number.
- Label data as historical/current and by date.
- Never present an asking price as a transaction price.
- Make limitations visible to the user.
- Prefer clarity over decoration.

## Currency and units

- Currency: **PKR**.
- Support the units the market actually uses (Marla, Kanal, square feet) and show conversions.

## Layout direction (non-binding)

- A valuation form that reads top-to-bottom like a professional assessment.
- Results as a clear card/section: range, point estimate, comparables (if any), data freshness and
  a short market note.
- Locality and market views as scannable tables and trends rather than dense dashboards.
- Consistent terminology with the underlying data model (locality, society, phase, block).

## Accessibility and robustness

- Legible contrast and readable type sizes.
- Keyboard-usable forms.
- Works at mobile widths, since many users search on phones.
- Clear error and empty states ("no comparables found" is a valid, honest result).

## What to avoid

- Generic SaaS landing-page filler.
- Fake precision and unexplained single numbers.
- Gamified or marketing-style claims of "guaranteed" valuations.
- Dark-pattern urgency, stock imagery and invented testimonials.

## States and feedback

- **Loading** — never show a bare blank; indicate that data is being fetched.
- **Empty** — "no comparables in this locality yet" is an acceptable, honest result.
- **Low confidence** — show a wider range and a note rather than a precise-looking number.
- **Stale data** — surface the collection date prominently when data is old.

## Terminology (user-facing)

Use consistent, plain terms: estimated asking price, range, comparables, locality, data freshness.
Avoid "market price", "sold price" and "valuation guaranteed" unless the underlying data supports
that claim.

## Not decided yet

- No frontend framework is chosen.
- No visual design system, colours or typography are fixed.
- No CSS or JS will be written during documentation/governance phases.

These will be decided at Phase 10 against these guidelines.
