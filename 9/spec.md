# Fix spec — derivation engine applies laws deterministically (non-random, non-optional)

**Filed:** 2026-11-15 · **Number:** snea-lib#9 · **Filing side:** `Brothertown-Language/brothertown-language-com` intake (per developer instruction)
**Source of record:** developer directive, brothertown-language-com session 2026-11-15: "file a fix spec for the non-random non-optional requirement for sound change continuum rules. if the results change by part of speech, that is expected." Framing of record, same session: "why are you treating sound change laws as optional? that makes no sense. why would I want sound laws with randomized stages?"

## Split provenance

This spec is the **engine side of a two-repo split** resolved by the sibling spec's fresh-context validation dispatch (round 1, 2026-11-15): the derivation tooling of record lives in this repository, under `snea-phonetics`' chain as a registered submodule — the validator verified `.gitmodules` (submodule `snea-lib` → `git@github.com:Brothertown-Language/snea-lib.git`). **Sibling (record side): Brothertown-Language/snea-phonetics#177** — the record states the corrected laws; this engine applies them. The seam: this spec's corrected outputs are the inputs of #177's SC-3/SC-4 (record-side surface diff and comparison re-run); #177's corrected law statements are the semantics this engine encodes.

## Problem

The engine carries the continuum's retired class in code and data:

1. `src/snea_lib/derivation/engine.py` ll. 3–12 — the binding-discipline docstring: "optional/gradient laws are **noted, not applied** — the output flags, never invents."
2. `src/snea_lib/derivation/engine.py` ll. 720–726 — the Law-13 arm hardcoded: `note="law13-never-applied"` with a flag emitted per BL output ending in š.
3. `src/snea_lib/derivation/rules/forward_laws.yaml` ll. 13–14 (discipline preamble), ll. 93 (`discipline: noted-not-applied`), ll. 131–136 (law 13's "gradient, language-particular" cross-language rate string), ll. 155 (law 16).
4. Committed tests enforce the retired semantics: `test/test_conservative_discipline.py` ll. 3–8 ("the four negative arms, mechanically: Law 13 never applies; Law 8 is noted-not-applied; gap-marked environments flag-not-fill"), `test_law13_never_applies` (ll. 24–32), `test_gap_environment_flags_not_fills` (ll. 55–61 — asserting the unreduced person row `*ǝrǝnīw` with the never-filled Law 16(ii) aphaeresis gap flag), `test_forward_chain.py` ll. 65.

A sound change law is a regular, environment-obligatory statement; no derivation may depend on a discretion or a "never applies" posture for a law whose stated environment is met.

## Repo scope (engine side: Brothertown-Language/snea-lib)

| Path | Surface | Role |
|------|---------|------|
| `src/snea_lib/derivation/engine.py` | ChainEngine | binding-discipline docstring; Law-13 arm + flag emission; noted-not-applied paths |
| `src/snea_lib/derivation/rules/forward_laws.yaml` | rule data | discipline preamble; law-13/law-16 entries; peer entries carrying the class |
| `test/test_conservative_discipline.py`, `test/test_forward_chain.py`, peers | enforcing tests | the retired-semantics assertions, updated in the same cycle as the behavior change |
| build/derivation outputs | chain outputs | corrected outputs the record side consumes |

## Requirements

- **R-1.** Every law the engine applies is deterministic wherever its stated environment is met — same inputs, same output; no step depends on discretion or a "never applies" posture for a law whose conditioning is stated.
- **R-2.** The noted-not-applied class is retired from code and rule data: Law 13 and Law 16 entries carry per-variety environments (the sources' own per-variety facts — e.g., "obligatory in Unquachog", "nonexistent in Massachusett") and the engine applies a law where its environment is met.
- **R-3.** Where the record cannot state a process's conditioning for a variety, the engine carries an **OPEN-environment marking** (named, source-cited, pending linguist adjudication) — not a gap flag that silently preserves the old output, and never an "optional" classification.
- **R-4.** Candidate-law review marks (hypothetical/provisional) persist as machine-readable statuses — a review mark is not a non-application discipline.
- **R-5.** Corrected outputs carry their law bases; the person-root chain yields the law-applied form under the stated environments (the record-side surfaces diff against this output — #177 SC-3/SC-4).

**Accepted outcome (developer-stated, 2026-11-15, verbatim):** "if the results change by part of speech, that is expected." A POS class carries its own stated environments; POS-conditioned output differences under the corrected application are not regressions.

## Success criteria

| ID | Criterion | Class | Instrument |
|----|-----------|-------|------------|
| SC-1 | No optional/gradient noted-not-applied discipline in engine code or rule data; affected entries carry per-variety environments or OPEN-environment markings | structural | audit — grep/read `engine.py` and `rules/*.yaml` for the retired classes and arms; each surviving instance states an environment or an OPEN marking |
| SC-2 | The engine's derivation is deterministic | behavioral | derivation re-run + identical-inputs second run (`pytest` fixture); output equality asserted |
| SC-3 | Corrected outputs carry law bases; the person-root chain yields the law-applied form under the stated environments | structural | engine build-output diff + the outputs' law-basis fields |
| SC-4 | The enforcing test suite passes under the corrected semantics, with every retired-semantics test updated in the same cycle | behavioral | `uv run pytest test/` green; retired-semantics tests deleted or rewritten to the corrected behavior |
| SC-5 | Review marks (hypothetical/provisional) persist as machine-readable statuses in rule data and outputs | structural | rule-data/flag audit — marks present in `forward_laws.yaml` B-series entries and carried by outputs |

## Acceptance framing

- Results changing by part of speech are the developer's stated expected outcome — no criterion demands cross-POS uniformity; each POS class carries its own stated environments.
- Review marks are preserved as marks; they never license non-deterministic application.

## Non-goals

- Orthographic rendering conventions for reduced shapes beyond what the stated environments determine — linguist-review surface.
- Record-side surfaces — the continuum record md, paper master, lexicon, docs/research inventories, primer tsv: sibling spec `snea-phonetics#177`.
- Site-side edits in `brothertown-language-com`.

## Verification instruments (detail)

1. **SC-1** — grep/read across `engine.py` + `rules/*.yaml` for the retired classes ("optional/gradient", "noted, not applied", "never applies", "noted-not-applied") and the Law-13 arm; every surviving instance resolves to a stated per-variety environment or an OPEN marking, each with citation.
2. **SC-2** — the derivation tooling's own test fixture runs a worked chain twice on identical inputs; the outputs compare identical.
3. **SC-3** — the chain's build outputs diffed against the prior recorded outputs; every changed output carries its law basis; the person-root row's corrected form identified.
4. **SC-4** — the enforcing suite runs green under the corrected semantics: `uv run pytest test/`; every retired-semantics test either rewritten to assert corrected behavior or deleted with the behavior's replacement covered.
5. **SC-5** — read of the B-series entries in `forward_laws.yaml` + the output status fields: hypothetical/provisional marks present.

## Edge cases & boundary conditions

- The engine's BL-side flags (e.g., law13-never-applied on š-final outputs) change class under the correction — the corrected semantic replaces the flag with the law-applied form or an OPEN marking where conditioning is unstateable; the flag taxonomy's consumers (record-side build notes) are updated by the record-side spec's own cycle.
- POS classes carry different applied-environment sets — differences are the accepted outcome.
- Where the corrected application leaves a rendering choice (how a reduced form is written), that choice is stated OPEN with its basis rather than silently taken.

## Boundaries

- The filing side (`brothertown-language-com`) never commits snea-lib or snea-phonetics content; the fix's implementation belongs to this repository's own workflow and gates.
- The record-side law statements (snea-phonetics#177) govern the semantics; where engine data and record disagree at implementation time, the record-side correction lands first and this engine follows it.

---

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
