## Spec — Rule-data lockstep with the corrected continuum chart (snea-phonetics#175)

**Sibling spec:** Brothertown-Language/snea-phonetics#175 corrected the synthesized PA→PEA→PSNEA continuum chart (both the `.md` card and the submission tex): the Law 20 row now states Goddard 1981 §15's printed triad (`PA *hk, *xk, *čk → Mass /hk/`, page-image verified; the earlier `*θk, *xk, *ʔk` reading was a misquote — the \*ʔk member belongs to Goddard 1994 ex. (42), and \*θk routes to Mass /sk/ per §16); the Cunningham adjustments set the `*hč, *ʔč` Mp cell to **hc** and the `*hs, *ʔs` Mp cell to **hs** (the hsh cells were analogy-fills — Fielding's chart carries no such rows); and Fielding's chart's **Delaware and Wampanoag columns are discounted as not valid data** (the sixth Cunningham adjustment — no determination may rest on them).

snea-phonetics' `test_rule_data_lockstep.py` enforces tex ↔ snea-lib rule-data agreement and now fails on four forward-table cells and the law-20/25/26 statements. This spec owns the snea-lib side.

**Scope (snea-lib only):** `src/snea_lib/derivation/rules/forward_tables.yaml`, `forward_laws.yaml`, `bl_rendering.yaml`, and the tests that assert them. The consuming repo's submodule pin bump rides the snea-phonetics#175 branch after this lands (ride-along invariant — never a standalone pointer PR).

**Requirements:**
- **R-1** `forward_tables.yaml` rows agree with the corrected tex Table 1: the law-20 row's `pa` is `*hk, *xk, *čk`; the `*šk` row's `wp` is null (the Fielding `tch` cell is discounted, no independent source); the `*hč, *ʔč` row's `mp` is `hc`; the `*hs, *ʔs` row's `mp` is `hs`.
- **R-2** `forward_laws.yaml` statements agree with the corrected tex prose: law-20 (printed triad + ⟨q⟩ environment), law-25 (Mp sk, c only; the WP tch discount stated; the \*θk → /sk/ §16 cross-reference), law-26 (WP sq per the Trumbull-table row alone), and any statement carrying a discounted Delaware/Wampanoag chart leg (law-18's "Delaware retains the nasal" calibration clause — restated per the discount).
- **R-3** `bl_rendering.yaml`'s \*hč and \*hs faces are re-grounded: the `"hč": "hsh"` and `"hs": "hsh"` mappings carry the corrected grounding (Table 1: \*hč → Mp hc, \*hs → Mp hs per the Cunningham adjustments) and render accordingly (`hc` / `hs`); the `"hš": "hsh"` B3 digraph stands unchanged (its grounding is BL's own /hš/ face, not the discounted cells). Any engine output or parity fixture asserting the old faces is updated with the same change.
- **R-4** The parent record's mirror (`docs/research/pa-pea-psnea-sound-continuum.tex` in snea-phonetics) is the single criteria source — no divergent restatement of the corrected rows is introduced anywhere in snea-lib.

**Success criteria:**
- **SC-1** (behavioral): snea-phonetics' `test_rule_data_lockstep.py` (both tests) runs green against snea-lib@HEAD after the pin bump. Evidence: executed pytest output run from the snea-phonetics tree with the bumped submodule.
- **SC-2** (behavioral): snea-lib's own full test suite runs green (or carries only its own pre-existing dispositioned reds, identical on its trunk). Evidence: executed pytest output.
- **SC-3** (content): no statement or cell in the three rule-data files attributes \*θk or \*ʔk to Goddard 1981 §15, cites Fielding's Delaware or Wampanoag columns, or maps \*hč/\*hs to the Mp hsh face. Evidence: grep of the rules tree.

Counts are operational; executed outputs are the records.

> **Artifacts:** full spec at `snea-lib/.issues/{N}/spec.md` (local-authoritative; linked via local-issues after filing).

*Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)*
