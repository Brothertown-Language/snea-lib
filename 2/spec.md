# Spec — Library v1 derivation modules: rule-data package, segment engine, composition subsystem, forward PA→BL chain, inverse daughter→PSNEA→BL chain

- **Parent**: Brothertown-Language/snea-phonetics#134 (library-content
  requirements, decomposed for this repository)
- **Sibling**: the consumer-side spec filed in snea-phonetics (submodule pin,
  `bl_ipa` migration, validator re-pointing, data-layer wiring, record-level
  certification)
- **Stage**: spec (awaiting the developer's approval for plan/implement)
- **Record of record**: parent #134 §2–§3; the continuum paper
  (`paper-side`: `docs/research/pa-pea-psnea-sound-continuum.tex`, Tables 1–3
  correspondence cells, Tables 4–6 worked derivations, `sec:brothertown-laws`
  B1–B7 with tie-breaker ladder and weights, `sec:brothertown-weights`);
  `docs/research/sound-law-rule-inventory.yaml` (verified forward laws);
  `docs/research/psnea-reversed-rule-inventory.yaml` (inverse cells and
  worked reconciliations); `docs/research/data/bt-starter-lexicon.yaml`
  (chain-derived and attestation-derived rows, B5 pending-ratification
  flags). All tracked in the parent repository `snea-phonetics`.

## 1. Problem

Parent spec #134 defined a shared derivation library and this repository as
its home. The library must now be built. This spec owns the library-side
execution: the initial modules `snea-lib` v1 carries, such that the consumer
spec in `snea-phonetics` can pin the submodule pointer, re-point its
validators to the migrated `bl_ipa`, wire the corpus and record data layers,
and stand up the record-level certification tests against the paper and
lexicon.

## 2. Scope

Library-side only: rule data as versioned package data (`snea_lib/derivation/rules/`),
the segment engine, the composition subsystem, the forward chain
(PA→PEA→PSNEA→BL), the inverse chain (daughter→PSNEA), the `bl_ipa`
migration home producing three-face BL output, and the cross-verification
marking surface. Data access is injected everywhere — the library stays
corpus-agnostic and never touches the parent's corpus submodule or record
files directly.

The B5 applications are carried exactly as the record states them:
recommendations on record with pending-ratification flags (parent #134 §3
R-2; validator-verified wording) — the library never treats them as ratified.

## 3. Requirements

- **R-L1 (rule data as package data).** The rule data SHALL live as versioned
  package data under `snea_lib/derivation/rules/`:
  (a) the extracted forward-table correspondence cells (paper Tables 1–3);
  (b) the verified forward laws as data;
  (c) B1–B7 with the tie-breaker ladder and combined weights
      (~0.24 Y-complex vs ~0.11 Narragansett from `sec:brothertown-weights`);
  (d) the Law-10 trigger list (the attested *i-context class, house/chief);
  (e) the †-class 'good'/-ew analogical exception data (Goddard 1981:83
      class, per the parent record);
  (f) the B5 applications as recorded recommendations with
      pending-ratification flags.
  No `.md` source-layer document feeds the engine (the `.md` twin of the
  paper is stale and excluded by construction — parent #134 §2).
- **R-L2 (segment engine).** A token-based segment representation
  (phoneme, length, boundary) with an ordered stage-wise rule pipeline.
  Table-driven; regex prohibited everywhere in the conversion layer
  (parent R-14; the research cards' standing convention). Every derivation
  records stage forms, applied laws, holds, and flags in its trace.
- **R-L3 (forward chain).** PA→PEA→PSNEA→BL ordered application with the
  conservative discipline mechanical (parent R-3/R-4): environment-obligatory
  laws step; Law 8 is recorded-not-applied; Law 13 is never applied;
  gap-marked environments are flagged, never filled — the output flags, never
  invents.
- **R-L4 (Law 10 policy).** Palatalization SHALL apply unconditionally before
  PEA *ē, and in PA *i-contexts only from the attested trigger list (seeded
  with the house/chief class); unlisted *i-context *k SHALL NOT palatalize
  and SHALL flag; the †-class 'good'/-ew paradigms override the law as
  exception data (parent R-5).
- **R-L5 (composition subsystem).** Whole-word PA forms and their
  morphological parse (initial/medial/final/inflection boundaries) SHALL be
  assembled from component-shaped inputs (Component Type, Allomorph-A/B/C
  variants, Condition fields) plus injected standard PA inflection data,
  with provenance marking (cited-PA vs composed-PA) and every assembly choice
  (final selected, allomorph taken, inflection attached) in the trace
  (parent R-6/R-7). Composition output feeds the forward engine with the
  parse its position-sensitive laws consume (parent #134 §6: the
  teeth/suffix *r contrast — same string-final PSNEA *r, stem-level via B1
  → y vs word-final via B2 → š — is resolved by the parse).
- **R-L6 (edge laws + confidence).** Word-edge laws (Law 6, Law 12, the
  disyllable rule) apply only at true word edges; hyphen-marked morpheme
  boundaries hold and flag. Every output carries a confidence class
  (fully-derived / partial / lookup-governed / flagged) and an
  attested/chain-derived/composed status (parent R-8). Lawless segments —
  the proto-laryngeal — carry and flag lawless (parent #134 §6).
- **R-L7 (inverse subsystem).** Daughter attestations SHALL convert to PSNEA
  candidate sets: table-driven per-daughter inverses from the reversed-rule
  record, merger inversion as candidate sets, resolution by multi-cognate
  intersection and the recorded tie-breaker ladder, daughter-own developments
  gap-marked (parent R-10). The v1 source registry is the exercised set:
  Williams 1643 (Nr + Ms-side Chart-B), Prince-Speck 1904 (Mp), Wood 1634 and
  Trumbull 1903 (Ms-side), Edwards 1787 (Mh, calibration only); Winslow 1624
  and Anonymous 1647 join only when conversion-layer certification anchors
  exist (parent R-11).
- **R-L8 (BL faces + bl_ipa home).** `snea_lib.bl_ipa` SHALL be the single
  home of the BL orthography/IPA machinery, migrated behavior-unchanged from
  the parent's `src/bl_ipa.py` at migration time; BL output carries three
  faces — starred phonemic form, Costa orthography, IPA (parent R-9). The
  stress rule is owned by this module (reuse covers it; parent out-of-scope).
- **R-L9 (cross-verification surface).** The library SHALL expose the
  forward/inverse comparison so a consumer marks a forward PSNEA confirmed
  (inside its cognates' inverse intersection) or flagged (outside)
  (parent R-12) — the library performs the set comparison; the dual-route
  record that exercises it lives in the parent.
- **R-L10 (library tests are fixture-fed).** Library-level tests SHALL use
  injected fixtures only — no corpus submodule dependency in this repo; the
  record-level certification that binds the library to the paper and lexicon
  is the consumer spec's territory (stacked after this work).

## 4. Success criteria

| ID | Criterion | Class | Instrument |
|----|-----------|-------|------------|
| SC-L1 | The rule-data package resolves and loads: `snea_lib.derivation.rules` imports, every `rules/*.yaml` parses, the `.md` layer is absent from the package | structural | import test + file-manifest check |
| SC-L2 | The conservative discipline holds mechanically: Law 13 never applies; Law 8 noted-not-applied; gap-marked environments flag-not-fill; unlisted Law-10 *i-context *k does not palatalize and flags | behavioral | pytest negative vectors |
| SC-L3 | Word-edge laws hold at true word edges and hold+flag at hyphen boundaries; the stem-final vs suffix-final *r contrast resolves by the supplied parse (B1 → y as stem-level, B2 → š as word-final) | behavioral | pytest vectors (teeth-class vs suffix-class) |
| SC-L4 | The forward engine reproduces recorded worked-derivation forms on parent-record-derived single-form fixtures (e.g., the Table 6 PA inputs: *wi·pitali, *wi·kiwa·Hmi, *sa·kima·wa, *-ali, *mete·hi, *neʔθwi, *elenyiwa, *menahanwi) | behavioral | pytest vectors generated from the recorded YAML, never hand-typed |
| SC-L5 | Composition produces the recorded parse and trace entries (final selected, allomorph taken, inflection attached, provenance flag) on unit fixtures | behavioral | pytest vectors |
| SC-L6 | Inverse mechanics behave per the recorded reconciliations: merger→candidate-set inversion, intersection resolution, tie-breaker order, daughter-own gap-marking | behavioral | pytest vectors |
| SC-L7 | `snea_lib.bl_ipa` output is identical to the parent's `src/bl_ipa.py` output over the parent's recorded test inputs at migration time | behavioral | parity run captured in the migration PR (consumer spec) |
| SC-L8 | The conversion layer imports no `re` | structural | static check test |
| SC-L9 | pytest, ruff, and pyright all green in this repo at the composed state | behavioral | command output |

Fixtures for SC-L4/5/6 are unit-scale, derived from the parent record, and
injected; they are not the record-level certification.

## 5. Edge cases carried from parent #134 §6

- *H (proto-laryngeal): no tracked law; carried and flagged lawless.
- *ʔ: cluster coda only in PA shapes.
- The teeth/suffix contrast: same string-final PSNEA *r → stem-level via B1
  vs word-final via B2 — resolved by the morphological parse, never by the
  phonological string.
- Cross-boundary conditioning (Law 10 before a neighbor component's *ē/*i;
  Law 14 N+stop clusters spanning seams): invisible in component-only
  derivation — flagged there, resolved via composition.

## 6. Impact

- New modules and tests under `src/snea_lib/` and `test/`; packaging updated
  for the rules package data. No repository-settings changes (furniture
  complete; PR #1 merged; main at `d9d82d0`).
- `bl_ipa` migrates here; the parent's copy deletion and validator
  re-pointing ride the consumer spec's PR — stacked after this work (the
  library lands first, the consumer pointer follows).
- MIT; SPDX headers and AI-attribution docstrings per repo conventions.

## 7. Out of scope

- Corpus wiring, fixture extraction from the Nisinoon datasets, record-level
  certification tests — consumer spec (snea-phonetics side).
- CI pipelines; PyPI publication.
- Winslow 1624 / Anonymous 1647 conversion layers (until certification
  anchors exist).
- Stress-rule implementation (the migrated `bl_ipa` owns it).
- Paradigm generation, role flips, and syntactic material.
- The parent record's `.md` source-layer sync (awaiting the developer's word
  per parent #123).
- Direct Hewson/Aubin acquisition (Nisinoon carries the data).

---

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)