<!-- SPDX-FileCopyrightText: 2026 Michael Conrad -->
<!-- SPDX-License-Identifier: MIT -->

# Spec — snea-lib#10: the row-recorded BL-leg y-drop for the pronoun chains

Authorization: the developer's 2026-11-17 pre-approval ("pre-approved to
file specs and stacked PRs for submodules to complete this work,
including implementing the submodule updates needed") — this is the
submodule chain of snea-phonetics#184 (the BL y-koine rule). Plan and
implementation proceed under that approval; the PR halts at the human
merge gate.

## Source

- The consumer spec snea-phonetics#184 (the BL y-koine rule): a BL form
  whose staged chain passes the r-set surfaces the y-dialect outcome,
  never the donor's r → n reflex. The pronoun chains are the recorded
  test case: PSNEA \*nīy → nī, \*kīy → kī (PA \*nīθa/\*kīθa, y-dialect;
  the \*y-drop, not a lost \*n), realized ⟨ni⟩/⟨ki⟩
  (`to_ipa` /ˈniː/, /ˈkiː/) — corroborated by the modern comparison side.
- The engine gap, verified live (2026-11-17, both repos' validators):
  forward from \*ni·y the orthography face is ⟨niy⟩ (Law 6's in-chain
  retention of final \*y — the house row's own recorded decision); from
  the cited PA \*ni·θa the face is ⟨nish⟩ (the naive B2 application to
  the \*r reflex). Both contradict the recorded chain.
- The design constraint (snea-phonetics#184's finding): the y-drop MUST
  land as a **row-recorded drop at the BL leg**, mirroring the \*-ali
  row's recorded PSNEA apocope precedent in `_edge_apocope` — keyed to
  the recorded rows, never a new general law. Law 6's in-chain retention
  of final \*m/\*n/\*y is itself a recorded decision (the house row); a
  general y-drop law would contradict the record.

## Problem

The engine cannot reproduce the pronoun chains' recorded BL outcomes.
The chain-reproduction contract in the consuming repo (snea-phonetics#184
SC-3) needs the engine's post-merge state to derive ⟨ni⟩/⟨ki⟩ from the
pron chains; until then it holds a record-fact disposition.

## Scope

| Surface | Role |
|---|---|
| `src/snea_lib/derivation/engine.py` | the BL-leg row-recorded y-drop (the \*-ali precedent's mechanism class) |
| `src/snea_lib/derivation/rules/` | the recorded-row data the drop keys on (the pron chains' recorded facts, cited) |
| `test/` | the RED/GREEN contract + the Law-6 regression assertions |

Out of scope: the consuming repo's surfaces (snea-phonetics#184 carries
them); any general y-drop law; the inverse engine unless its own tests
demand the recorded fact's mirror.

## Requirements

- **R-1.** `ChainEngine.derive` on the pron chains (PA \*ni·θa/\*ki·θa
  and the PSNEA \*nīy/\*kīy citations) SHALL produce the recorded BL
  outcomes ⟨ni⟩/⟨ki⟩ (IPA /ˈniː/, /ˈkiː/ via the orthography face), by a
  drop recorded at the row level and applied at the BL leg.
- **R-2.** The drop SHALL be keyed to recorded row data (the
  \*-ali-precedent mechanism class: a recorded fact applied where the
  chain states it), never a new general sound law; the rule-data record
  cites its source (the register's recorded chains, the developer's
  y-koine directive).
- **R-3.** Law 6's recorded in-chain retention of word-final
  \*m/\*n/\*y SHALL be behaviorally unaffected (the house row and every
  existing retention assertion stay green — no general-law change).
- **R-4.** The trace SHALL record the drop as a recorded-fact
  application (leg BL, with the row citation) — visible in the
  derivation trace, never a silent edit.

## Success criteria

| ID | Class | Criterion | Instrument |
|----|-------|-----------|------------|
| SC-1 | behavioral | \*ni·θa and \*ni·y (parse `(ParsePart("inflection","ni·y"),)`) derive orthography face ⟨ni⟩; \*ki·θa/\*ki·y → ⟨ki⟩; IPA faces /ˈniː/, /ˈkiː/ | `uv run pytest test/` on the new chain test |
| SC-2 | structural | The drop is a row-recorded application: the rule-data record exists, cites the recorded chains, and is keyed to the rows (no new general law in the law tables) | read the rule-data record + diff the law tables |
| SC-3 | behavioral | Law-6 retention regression: the house row and existing retention tests stay green | `uv run pytest test/` full library suite |
| SC-4 | structural | The trace carries the recorded-fact application at the BL leg with the row citation | assert the trace in the chain test |

## Out of scope

Consumer-repo surfaces and suites (snea-phonetics#184) · general
sound-law changes · the N-dialect donor reflexes.

## Impact

Consumers: snea-phonetics#184's chain-reproduction contract (the two-state
join) and the ladder's record-vs-engine precedence. Risks: a keyed drop
could over-apply if its key is broader than the recorded rows — the tests
assert the non-pron final-y behaviors stay exactly as recorded (house
row). The library's public API is unchanged.

*Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)*
