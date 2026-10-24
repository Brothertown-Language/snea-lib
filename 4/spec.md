<!-- SPDX-FileCopyrightText: 2026 Michael Conrad -->
<!-- SPDX-License-Identifier: MIT -->

# Spec — The OCR-sourcing proofing machinery: the shared model layer, the review core, and the GUI components (snea-lib#4)

Cross-referenced: algonquian-library#69 (the runbook this machinery implements — `docs/runbooks/ocr-sourcing-proofing.md`), algonquian-library#88 (the follow-up migration spec in the consuming repo), snea-grammar (cites the same runbook path as governing).

## 1. Intent

The family's OCR proofing discipline is specified exactly once — the OCR-sourcing proofing runbook — and is implemented nowhere shared. This spec puts the machinery into the shared family library: the runbook's semantics as code, the review-record core that serves both the runbook pass and the region-mark review flows, and the GUI components every proofing/review surface consumes. The machinery serves general OCR proofing for any derived text layer, and it serves the eliot-tritext specifics — region marks, chapter-start review, duplicate-leaf and witness flows — as injected content, never as library logic.

## 2. The problem and the observed failures

The rule is one prose specification with three divergent implementations, each free to drift:

1. **The corpus-bound machinery** — algonquian-library's `tools/proofing_ui.py` (1309 lines), `tools/chapter_review_ui.py` (458 lines, its header records derivation from the proofing UI's image-pane machinery), `tools/dup_review_ui.py` (206 lines) and the acquisition stack behind them — hard-bound to the eliot-tritext layout (`docs/research/data/eliot-tritext/…`, `tmp/ocr/<BOOK>/…`, leafmaps, `kraken_geometry` sibling imports).
2. **The private untracked GUI** — snea-phonetics' `private/ocr-proofing/proof_gui.py`, which by its own header re-instantiates "the corpus #41/#93 pattern" for mirror-quote proofing: untracked, ungated, unreviewable, single-copy.
3. **The gate's record checks** — algonquian-library's `tools/build_grammar_sources.py` defines its own status tokens (`human-proofed`, `partially-proofed`, `unproofed`, `proofed`, `unproofed-working-copy`, `flagged`, and its `WORK_STATUSES` set) independently of any shared semantic implementation.

Each is an independent reading of one specification. The untracked copy is the clearest observed failure: original code outside version control, exactly the loss-and-drift hazard the developer has named a recipe for disaster. The shared library exists to prevent this class — it holds derivation and orthography machinery consumed via submodule — but holds no proofing machinery, and its charter's current wording ("general SNEA/PA/PEA/PSNEA machinery") does not admit the machinery family-wide or beyond it, while the developer projects non-SNEA reuse.

## 3. The design

Layered, dependency-injected, self-contained. Library code knows kinds of anchors, vocabularies, and record contracts — never which regions mean chapter starts, nor any store's layout.

### 3.1 The model layer (`snea_lib.proofing.model`)

The runbook OCR-1 through OCR-9 semantics as pure standard-library code:

- **The locator space**: a one-based, inclusive `START-END` line span in a tracked text layer; and the printed-work citation locator (page, section, paragraph) for documents with no line layer.
- **The closed four-status vocabulary**: `proofed`, `unproofed-working-copy`, `flagged`, `born-digital-not-applicable`. A state outside the four is not a status.
- **The three record fields**: the state, the pass date (ISO `YYYY-MM-DD`), and the covered locators.
- **Coverage intervals** with containment decisions and the OCR-7 extension rule: a record's covered locator set equals the pass's covered list; sourcing an uncovered locator requires the record extended first.

The module's provenance text cites the runbook path as the semantics' source of record, read at authoring time — never at runtime.

### 3.2 The review-record core (`snea_lib.proofing.review`)

One review-record shape over two anchor families:

- **Text-anchored** — a locator subject (the 3.1 space), for the runbook pass.
- **Image-anchored** — a page image plus a rectangle or polygon region, for the region-mark flows (chapter-start candidates, duplicate-leaf pairs, blank-leaf confirmations, boundary probes, witness bands).

Each record carries: the subject, a state drawn from a **per-consumer injected closed vocabulary** (the runbook's four is one instance; each geometry register injects its own), the pass date, and the evidence reference. Verdicts are written through an **injected register-writer contract**; the library holds no store schema and no file format.

### 3.3 The GUI components (`snea_lib.proofing.widgets`, extra-gated)

The shared machinery the three implementations repeatedly re-derived:

- the image pane (page-image rendering at reference metrics);
- region overlays supporting rectangles **and** polygons (kraken geometry is polygon-shaped; the component accepts both);
- the side-by-side two-pane comparison (witness or text-layer against the page image);
- item/region navigation (next item, leaf paging, selection state);
- a verdict palette whose character/content set is injected (the special-character sets are SNEA-orthography content — adapter-provided);
- window-geometry persistence and restore.

Content is injectable at every seam: vocabularies, palette contents, geometry-loading callbacks, register writers, session keys. The library never knows a store path.

### 3.4 The `[proofing]` extra and the test posture

- The extra carries `pyside6` and nothing else GUI-shaped. The default environment installs and tests the headless surfaces without it. Torch never enters the library.
- The screenshot-test posture ports from algonquian-library's `test/conftest.py` (authoring-time reference): a conftest-managed Xvfb display (offscreen fallback where Xvfb is absent), per-state-changing-operation screenshot capture through a `ui_shot` fixture, and failure-time live capture — shipped as **reusable fixtures** so the SOP stops being re-implemented per repository.

### 3.5 The charter amendment

`README.md` and `AGENTS.md` admit shared research/workflow machinery usable by projects beyond the SNEA family, while the "no project-specific applications" line stands (wired applications stay in consuming repos).

## 4. Requirements

- **R-1**: The machinery SHALL implement the runbook's locator space — one-based inclusive `START-END` line spans and printed-work citation locators — with parsing, validation, and containment decisions.
- **R-2**: The machinery SHALL implement the runbook's record semantics — the three record fields and the closed four-status vocabulary — with coverage-interval tracking and the OCR-7 extension rule.
- **R-3**: The machinery SHALL implement the review-record core over both anchor families — text-anchored and image-anchored (rectangle or polygon) — with per-consumer injected closed vocabularies and verdicts written through an injected register-writer contract.
- **R-4**: The machinery SHALL provide the GUI components: image pane, region overlays (rectangle and polygon), side-by-side comparison, item/region navigation, an injected-content verdict palette, and window-geometry persistence.
- **R-5**: The GUI components SHALL ride an optional-dependencies extra (`proofing`) carrying pyside6; the default environment SHALL install and test without it; torch SHALL NOT enter the library.
- **R-6**: The screenshot-test posture SHALL ship as reusable fixtures (managed display, `ui_shot` capture, failure capture) consumed by this repository's own UI tests and documented for consumer adoption.
- **R-7**: The machinery SHALL be self-contained: imports limited to the standard library, the machinery's own package, and pyside6 (components only); no imports of `snea_lib.derivation`, `snea_lib.bl_ipa`, or any parent-repo code or path; the runbook citation lives in provenance text at authoring time only.
- **R-8**: The charter SHALL be amended in `README.md` and `AGENTS.md` to admit shared research/workflow machinery beyond the SNEA family.

## 5. Success criteria

| ID | Criterion | Class | Verification instrument |
|----|-----------|-------|------------------------|
| SC-1 | Locator semantics: `3-7` and `7-7` parse; `0-2` and reversed spans rejected; containment correct at boundaries (`3-7` contains 3 and 7, not 2 or 8); adjacent spans (`3-7` vs `8-10`) do not overlap; nested spans overlap | behavioral | `uv run pytest test/test_proofing_model_locators.py -q` passes in snea-lib |
| SC-2 | Coverage: a record's covered set equals its pass's covered list; containment answers follow; extension appends and an uncovered locator reports not-covered until then | behavioral | `uv run pytest test/test_proofing_model_coverage.py -q` passes |
| SC-3 | The four-status vocabulary rejects any outside token; the three record fields roundtrip through serialization | behavioral | `uv run pytest test/test_proofing_model_records.py -q` passes |
| SC-4 | The review core accepts both anchor families under two distinct injected vocabularies in one suite; an out-of-vocabulary state is rejected; verdicts land on the injected writer and nowhere else | behavioral | `uv run pytest test/test_proofing_review_core.py -q` passes (in-memory writer) |
| SC-5 | Extra posture: the default `uv sync` environment holds neither pyside6 nor torch; `uv sync --extra proofing` provides pyside6; base dependencies remain pyyaml-only | structural | run both sync forms and probe `uv run python -c "import PySide6"` (fail by default, succeed with extra); pyproject inspection (`rg torch` empty) |
| SC-6 | Components render offscreen under the managed display in the default tier: a page image renders in the pane; rectangle and polygon overlays draw; side-by-side panes show two images; navigation advances selection; the verdict palette applies an injected state; every state-changing operation captures a screenshot artifact | behavioral | `uv run pytest test/` (UI test files) asserting widget state and `ui_shot` artifacts |
| SC-7 | Window geometry persists across a close/reopen cycle | behavioral | pytest case setting geometry, closing, reopening, asserting restore |
| SC-8 | Self-containment: the machinery's import graph holds only stdlib + machinery-package + pyside6-in-components; zero `derivation`/`bl_ipa`/parent-repo imports | structural | a source-walking pytest structural test asserting the import set; `uvx pyright src/` clean |
| SC-9 | The charter amendment is present in `README.md` and `AGENTS.md`, naming shared research/workflow machinery and non-SNEA usability | structural | content check on both files for the amended paragraph |
| SC-10 | The runbook citation is present in the model layer's provenance text, naming the runbook path | structural | content check for `docs/runbooks/ocr-sourcing-proofing.md` in the model package/README |

## 6. Out of scope

- Any consumer-repo change: submodule mount creation, migrations, dependency cleanups, gate re-basing (the consuming repo's follow-up spec owns these).
- Record formats, store schemas, geometry stores, register layouts — unchanged everywhere.
- The `corrector` subproject in its entirety — the developer dropped the issue; the code stays whole and standalone.
- Wheel publishing to any index.
- snea-phonetics adoption (its own repo's change, taken up separately).

## 7. Approach

Fresh implementation in snea-lib, extracted in knowledge from the three existing implementations at authoring time only (the corpus UI suite, the private GUI's pattern header, the gate's status tokens) — the family's standing discipline for rule data applied to a code machinery: parent repos are read while authoring, never by the shipped code. Dependency injection at every seam; no display-dependent test runs outside the managed posture; the package's UI surface rides the extra so derivation consumers never resolve Qt.

## 8. Impact

- snea-lib's environment and test surface gain pyside6 (extra only) and a display-managed UI-test posture; the derivation surfaces and their consumption are untouched.
- Consumers are unaffected until the named follow-up specs; the submodule+pythonpath consumption mode is unchanged, so no consumer dependency set moves.
- The wheel payload gains the machinery package; the extra is optional, so payload cost lands only on consumers that opt in.
- The charter amendment is the change that makes family-wide and non-SNEA consumption *licensable* by the repo's own rules.

## 9. Traceability

Every criterion answers a developer statement from the design discussion (2026-10-24 session):

| Developer statement | Criteria |
|---------------------|----------|
| "the OCR proofing is for ALL sources and references as needed. It is not only for the eliot bible" | R-1..R-3 (source-agnostic model + review core) |
| "I prefer item B so the code can be used elsewhere without needing weird cross-ups, the machine could possibly be used for non-SNEA needs in other repos" | R-3, R-5, R-7, R-8; SC-4, SC-5, SC-8, SC-9 |
| "keep in mind for the new code in the lib repo that both the general OCR proofing as well as the specific needs of the eliot tritext with the region marks proofing etc is also needed" | R-3, R-4 (two anchor families, injected vocabularies, polygon overlays); SC-4, SC-6 |
| "there are like 3 different main OCR related setups, they all need to be placed into the lib, and possibly made more KISS and DRY in their coding as they share a lot of requirements.; we need to fully migrate to the new approach" | R-1..R-6, R-8; SC-1..SC-10 |
| "keep the OCR machinery self-contained in a subfolder so that the parent repo isn't polluted with dependencies it doesn't need for lib usages" | R-5, R-7; SC-5, SC-8 |
| "It is expected that snea-lib will be imported as a submodule when shared code is needed. KISS. DRY." | R-7 (submodule-consumable, self-contained) |
| "corrector model training will remain separate. it is a stand alone utility… drop the corrector issue" | Out of scope (corrector excluded whole) |
| "proceed with specs… after specs are created; report then halt with URLs" | this spec + the follow-up migration spec at algonquian-library#88 |

## 10. Not included

Model training and weights; segmentation/geometry format modeling (kraken shapes stay app-side as data the components accept); publishing; documentation of consumer adapters (that is the migration spec's surface).

---

*Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)*