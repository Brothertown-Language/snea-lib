# Plan — Library v1 derivation modules (snea-lib#2)

Spec: `.issues/2/spec.md` (parent Brothertown-Language/snea-phonetics#134).
Authorization: `#2 approved for pr` (carries plan → implement → PR; merge stays
human-only).

Every item below traces to exactly one SC of the spec. Items are ordered so
each RED/GREEN cycle builds on the verified prior state. All commands run
through `uv run`/`uvx` per AGENTS.md. Work happens on
`feature/2-library-v1-derivation-modules`.

## Approach decisions (binding; the implementation follows these)

- **Segment representation (R-L2).** `src/snea_lib/derivation/segments.py`:
  frozen dataclass tokens — `Seg(sym, stage, palatal, component)` where `sym`
  is the phoneme in its stage notation, `palatal` marks a PSNEA palatalized
  *k (serialized as plain `t` in PSNEA strings per the record, as `c` in BL
  faces), `component` carries parse tags (`initial|medial|final|inflection`).
  Word = `tuple[Seg, ...]`. String↔segment conversion is a table-driven
  tokenizer over a per-stage phoneme inventory (  PA notation: `·` length mark,
  `ʔθ/hθ/hl/ʔl/nθ/θk/xk/ʔk/ht/ʔt/hč/ʔč/hs/ʔs/nl/šk/θkw/hp/xp/nt/nk` clusters;
  PEA/PSNEA notation: `a` (Table 2 row 1: PA *a stays *a at PEA/PSNEA), `ǝ ē
  ī ō ā`, clusters `hš hs hč hk ht hp hx hr xkw` plus the retained shapes
  `šk/nt/nk` at the stages Table 1 records them; a hyphen morpheme-boundary
  token at every stage). No regex anywhere in
  `snea_lib/derivation/` (SC-L8).
- **Stage pipeline (R-L3).** `engine.py`: ordered stages
  `PA → pre-PEA → PEA → PSNEA → BL`; laws dispatched by id from
  `rules/forward_laws.yaml`; each application appends a trace entry
  (law id, cite, stage form). DerivationResult: stage forms, trace, flags,
  confidence, status. Intra-stage PEA order (needed to reproduce the
  recorded rows; ordering claims in the record are relative only):
  the Law-6 edge apocope first (so a word-final short vowel apocopates
  before Law 5 would lengthen it — grounded: teeth row `*wīpītar`), then
  Laws 1, 2, 16(a), 7, 9 as the leg's segmental run, then the word-final
  *w/(c)-class resolution (after Law 7 — see the edge-law bullet), then
  the Law-8 note evaluating the law's own stated PA-shape environment
  (`/V´ː __`: the *w's immediately preceding PA vowel carries `·` —
  grounded: the chief row `*sa·kima·wa`, whose `a·` precedes the retained
  w; the house/person rows' w's follow short PA *i and are outside the
  law's stated environment), then the vowel shifts 4/5 (incl. the
  PEA-system statement's `*a· → *ā`) close the leg.
  Law 11 is the PSNEA-leg law (hr/*hx → *hš).
- **Renderer conservatism.** A BL phoneme without a `bl_rendering.yaml`
  letter mapping stops the face production with an unmapped-segment error
  — never an invented letter; the error names the segment and stage form.
- **Conservative-discipline mechanics (R-L3/R-L4).** Law 8: trace entry
  `law8-noted-not-applied`, never applied — the applier's environment
  evaluation point is the PEA leg, where the law's own stated environment
  `/V´ː __` reads on the PA-shape segments (the *w's immediately preceding
  PA vowel carrying `·`; the chief row is the recorded env-case); the
  trace entry carries the law id and the paper's Law-8 cite; the
  vector asserts both the retained *w in the stage form and this entry's
  presence and law id. The discipline's grounding is the record's own
  generator convention (Table 5's generator rules: "only laws with
  stated, environment-obligatory conditions take a step" — Law 8's "usually
  drops" is not environment-obligatory). Law 13: `law13-never-applied`
  note (the same generator convention); gradient never applies. Gap-marked
  environments: `gap-environment-*` flags, never filled. Law 10 negative
  arm: unlisted *i-context *k does not palatalize;
  `law10-unlisted-i-context` flag.
- **Row-grounded edge laws (R-L6).** Word-edge laws apply only at true word
  edges. Law 6 in-chain: (a) the operative apocope is word-final *short*
  vowels; **grounding, stated explicitly:** the operative short-vowel
  apocope is Law 16(i)'s recorded taxonomy ("apocope (word-final short
  vowels, all PA short vowels)"); Goddard 1980 §4's Law-6 statement
  ("word-final vowels are lost") is the blanket surface behind it, and the
  record's own cells pin the retention exceptions — the three row's
  derivation excludes Law 6 entirely (row laws "2, 11, 16") and Table 5
  note f records its final as the long *i· reading retained through the
  chain, with Law 5's *ī the realized outcome; word-final *long* vowels
  are therefore retained in-chain (the teeth `*wīpītar`, chief
  `*sākīmāw`, house `*wīkīwāHm`, heart `*mǝtēh`, island `*mǝnahan`,
  person `*ǝrǝniw` PEA columns are the drop cells). The divergence between
  the blanket statement and the short-only in-chain surface is carried,
  cite-anchored, and never silently resolved: the law data carries both
  statements, the applier implements the short-vowel surface, and the
  trace carries a `gap-carried-blanket-realized-short` note when a
  long-final input is processed (so any future row contradicting it
  surfaces at the trace instead of silently). (b) a word-final *w exposed
  by (a) drops when postconsonantal (grounded: island row
  `*menahanwi → *mǝnahan`, Laws "6") and is retained when postvocalic
  (grounded: chief row `*sākīmāw`); (c) word-final *m/*n/*y exposed by
  (a) are retained in-chain, Goddard §28's loss scope recorded-not-applied
  (grounded: house row `*wītīwāHm`). **Ordering within the PEA leg:** the
  edge apocope (a) runs first, then Laws 1, 2, 16(a), 7, 9 in that run;
  the word-final *w resolution (b) — and the (c)-class evaluation — runs
  once, after the complete 1, 2, 16(a), 7, 9 run and before the vowel
  shifts 4/5, since any of those laws can change what a post-apocope *w
  follows (grounded: person row `*ǝrǝniw` — Law 7's y-drop makes the w
  postvocalic, and the w is retained; island's w follows n and drops at
  the same single evaluation point). The vowel shifts 4/5 close the leg.
  **Edge-law timing is parse-driven (R-L5's position-sensitive parse):** a
  word carrying stem material (any `initial|medial` component) applies its
  apocope at the PEA leg (grounded: every stem-bearing row's recorded PEA
  column); a pure-inflection citation (no stem component — the `*-ali`
  row) applies its recorded apocope at the PSNEA leg per its own recorded
  columns (PEA `*-ari` retained, PSNEA `*-ar` dropped; Table 4 note (b)
  grounds the PSNEA placement of `*-ar`); hyphen-marked continuations
  hold+flag per SC-L3 and override both timings. The suffix row's recorded
  apocope thereby exercises the §4 even-short-vowel-disyllables clause.
  **Law 16 stage ownership, stated explicitly:** the engine's in-chain
  Law-16 surface is the type-(a) syncope only (word-initial syllable
  between a resonant and a fricative — grounded: the three row's recorded
  PEA cell `*nhxwi`, whose derivation required it), with the trace noting
  Law 16's own declared scope ("vowel-deletion set; daughter-stage
  detail") so the in-chain surface is not mistaken for the law's whole
  domain; the remaining Law-16 processes are daughter-side and never
  in-chain (the §1 WP examples ⟨ren⟩ and Table 5's WP three cell |nhšwi·|
  are daughter-side demonstrations outside the chain surface). Law 6's
  remaining recorded clause ships in the edge applier: `*-kw` retention.
  The `b`+`(c)`+timing choices are trace entries citing the grounded rows.
- **Law 10 (R-L4).** Order: (1) the †-class exception routes (SC-L12) —
  R-L4's "the †-class 'good'/-ew paradigms override the law as exception
  data": a class member (declared, or matching the recorded form) does not
  palatalize via the law; the k carries and the exception route is recorded
  in the trace; the override precedes the arms it overrides; (2)
  unconditional before PEA *ē (SC-L10) — non-exception inputs palatalize
  before PEA *ē; (3) the attested trigger list (SC-L11, house/chief class)
  — palatalize with cite; (4) unlisted *i-context *k — flag, no
  palatalization (SC-L2 arm).
- **B-laws and faces (R-L8).** PSNEA → BL starred face applies the selected
  B reflexes (B1 non-final *r→y, B2 word-final *r→š, B3 *hš carried, B4
  palatal *tʲ→c-face, B5/B6/B7 carried-or-application); the starred face
  preserves the record's starred notation (`**wīcīwāHm`-style). The
  orthography face maps BL phonemes to Costa letters via
  `rules/bl_rendering.yaml` (including the recorded `final *-Hm → ⟨-ôh⟩`
  rendering, lexicon house flag, applied 2026-10-20, and the recorded
  orthographic-schwa epenthesis: an onset-adjacent consonant+cluster
  junction writes ⟨u⟩ at the junction — grounded: the three row's recorded
  orthography `nuhshwi` from `**nhšwi`, lexicon flag "initial cluster
  rendering", paper mini-dictionary ⟨nuhshwi⟩ /nəˈhʃwiː/; the epenthesis
  lives in `bl_rendering.yaml` as rendering data, not in code); the IPA
  face is `bl_ipa.to_ipa` over the orthography (so the three row's IPA
  face derives over `nuhshwi` → /nəˈhʃwiː/, matching the record). Three
  faces recorded per output. Bare (unparsed) PA word inputs default to a
  single stem component — they are stem-bearing for the edge-timing rule.
- **Parse-driven B1/B2 split (spec §5).** word-final *r is B2 only when
  it is the last segment of a `final|inflection` component; otherwise B1.
  Parse tags on inputs compose through all laws.
- **Composition (R-L5).** `composition.py`: components of kind
  `initial|medial|final|inflection`, each with Allomorph A/B/C variants and
  condition fields (`before-vowel|before-consonant|word-final|any`,
  evaluated table-driven against the neighbouring component's segment
  class); inflection data injected by the caller. Trace entries: final
  component selected, allomorph taken (name+condition), inflection attached,
  provenance (`composed-PA`/`cited-PA`). Output feeds the forward engine
  with the parse tags.
- **Inverse (R-L7).** `inverse.py`: per-daughter inversion over
  `rules/reversed_rules.yaml` (one_to_one → singleton set; one_to_many →
  full candidate set; gap_marked → no rule + gap mark); resolution =
  per-segment intersection across cognate inversions; single-source sets
  stand as recorded; residue resolved by the recorded tie-breaker ladder
  (weighted majority ~0.24 Y vs ~0.11 Nr → attestation density →
  conservative retention → contested); Edwards 1787 = Mh calibration,
  corroboration-only (never sources). Daughter forms enter as already-
  converted phoneme tokens — the library references the conversion cards,
  never reimplements them (parent record holds the cards). Ladder step-1
  weighting maps daughter columns to founding-bloc weights
  (`brothertown_laws.yaml`): Mp → Y-complex ~0.24, Nr → Narragansett
  ~0.11, WP → Wampanoag-area ~0.10 (attestation only — can no longer
  contend at step 1, per the record), Ms-side → corroboration/density
  only, Mh → calibration marker. The four-way n-set collapses on the
  all-n agreement via ladder step 3 (the reflex-equal-to-PSNEA-value
  candidate — grounded: friend worked case, `by agreement`). The
  rules/*.yaml files author structured fields directly (token lists,
  candidate lists) — the record's prose forms are extraction source, not
  engine input.
- **Cross-verification (R-L9).** `cross_verify.py`: per-segment membership
  test of a forward PSNEA form against its cognates' inverse candidate-set
  intersection → `confirmed` / `flagged`.
- **Marking (R-L6 output fields; SC-L13/14/15).** Flag vocabulary (each with
  severity): severity `partial` — `law8-noted-not-applied`,
  `law13-never-applied`, `lawless-carried`, `law10-unlisted-i-context`,
  `edge-hyphen-held`,
  `daughter-own-development-marked`, `candidate-set-standing` (a
  single-source inverse whose candidate set stands as recorded — carries
  the stated ambiguity, per the record's reconciliation step 4),
  `gap-carried-blanket-realized-short` (the edge-law bullet's
  blanket-vs-short divergence note, emitted when a long-final input is
  processed) — all severity `partial`; severity
  `lookup` — `law10-trigger-cite`, `law10-exception-route`,
  `b5-application`, `b5-pending-ratification` (the applied-B5 output's
  confidence class: `lookup-governed`); severity `contested` — `contested`.
  Confidence derived
  from trace, in
  precedence order contested → lookup → partial → fully-derived. Status:
  forward of a cited PA input → `chain-derived`; composition-fed →
  `composed`; inverse-from-attestation → `attested`.
- **DI (conventions + principles).** Data access stays injected per spec §2
  (constructor/parameter injection of rule sets, fixtures, inflection data).
  `dependency-injector` is advisory and buys nothing for a stateless rule
  engine whose inputs arrive per call — the DI approach used is explicit
  constructor injection; stated per principles-5.
- **bl_ipa migration (R-L8, SC-L7).** `src/snea_lib/bl_ipa.py`: the parent's
  `src/bl_ipa.py` copied byte-for-byte except its docstring provenance note
  (behavior unchanged). Parity fixtures: word set = Costa-letter BL forms —
  the parent lexicon's `bl` fields (`bt-starter-lexicon.yaml`, the record's
  Costa-face surface) plus the parent primer lesson table's `bl_letters`
  values (`bt-primer-lessons.tsv`), both parent-record surfaces; the
  expected IPA captured by running the parent's `src/bl_ipa.py` over that
  word set at implementation time and frozen into
  `test/bl_ipa_parity_words.yaml`. The starred Table 6 forms are NOT part
  of this word set — they are starred phonemic notation outside the Costa
  letter domain (the parent module raises on them) — and are asserted in
  item 8's stage-form vectors as strings, never through `bl_ipa`. The
  SC-L7 parity-run capture in the consumer PR is the consumer spec's
  instrument; this repo's frozen vector is the library-side behavior
  guard.
- **Rule-data files (R-L1).** `src/snea_lib/derivation/rules/`:
  `forward_tables.yaml` (Tables 1–3 cells), `forward_laws.yaml` (Laws 1–26,
  gap-marked environments, cites, engine keys), `brothertown_laws.yaml`
  (B1–B7, tie-breaker ladder, ~0.24/~0.11 weights), `law10_triggers.yaml`
  (attested *i-context class: house/chief), `analogical_exceptions.yaml`
  (†-class 'good'/-ew per Goddard 1981:83), `b5_recommendations.yaml`
  (recorded B5 applications with pending-ratification flags),
  `reversed_rules.yaml` (per-daughter inverses, source registry,
  reconciliation procedure), `bl_rendering.yaml` (phoneme→letter map +
  `final *-Hm → ⟨-ôh⟩` + the orthographic-schwa epenthesis). All extracted
  from the parent's tracked record
  (paper Tables 1–6 + B-laws §, the two inventory YAMLs, the lexicon) with
  cites; no `.md` file ships in the package (the paper's `.md` twin is
  excluded by construction and never read). Copyright safety: only the
  parent's tracked, project-authored material is extracted; nothing from
  `private/` enters the tree.

## Items

### 1. Rule-data package of record — SC-L1

- **Deliverable:** `snea_lib/derivation/` + `snea_lib/derivation/rules/`
  with the eight YAML data files and an `importlib.resources` loader
  (`load_rules()`); hatch packaging carries the YAMLs as package data —
  procedure: run `uv build`, list the wheel's contents, and add explicit
  hatch `force-include`/data config **if and only if** the listing omits
  the YAMLs; the wheel listing is recorded either way.
- **RED:** `uv run pytest test/test_rules_package.py -q` — the test asserts
  `snea_lib.derivation.rules` imports and `load_rules()` returns parsed
  tables; it fails now (module absent).
- **GREEN:** package + loader + data files land; test green.
- **Instrument:** `uv run pytest test/test_rules_package.py -q` (imports,
  `yaml.safe_load` of every `rules/*.yaml` via the loader, manifest check
  that no `.md` exists under the package, one structural smoke assert per
  table: forward tables have the 26+ rows, reversed rules have the four
  daughter columns, B-laws have B1–B7 + ladder + weights).

### 2. No-regex static guard over the conversion layer — SC-L8

- **Deliverable:** `test/test_no_regex.py`: walks
  `src/snea_lib/derivation/*.py` (excluding `__init__.py`) and
  `src/snea_lib/bl_ipa.py`, asserting none imports `re`; asserts the
  discovered conversion-layer set is non-empty (so the guard stays real).
- **RED:** fails now — the derivation module set is empty (the non-empty
  assert fires).
- **GREEN/sequencing (explicit):** the guard is a standing test whose
  non-empty clause is satisfied when item 3 lands the first conversion
  modules — item 3's suite run turns this guard green; from then on the
  guard walks every module as it lands, and each later item's suite run
  keeps it green. The dependency is linear (2 → 3), followable from the
  plan alone, and never circular.
- **Instrument:** `uv run pytest test/test_no_regex.py -q`.

### 3. Segment engine core + conservative discipline — SC-L2

- **Deliverable:** `segments.py` (token representation, stage notation
  tokenizer, serialize) + `engine.py` core (stages, law dispatch, trace,
  flags) with the conservative-discipline mechanics: Law 13 never applies;
  Law 8 noted-not-applied; gap-marked environments flag-not-fill; Law 10
  negative arm (unlisted *i-context *k → no palatalization +
  `law10-unlisted-i-context` flag). `rules/law10_triggers.yaml` consulted
  for the negative arm's classification.
- **RED:** `uv run pytest test/test_conservative_discipline.py -q` — four
  negative-vector groups fail (module absent → ImportError).
- **GREEN:** vectors pass: a Law-13-vector input (word-final *r at the
  SNEA boundary, western-gradient context recorded in the data) applies no
  reduction and carries `law13-never-applied`; a Law-8-vector input (*w
  after a long vowel) carries `law8-noted-not-applied` and keeps *w; a
  gap-environment vector flags-not-fills; an unlisted-*i-context *k vector
  stays *k with the flag.
- **Instrument:** `uv run pytest test/test_conservative_discipline.py -q`.

### 4. Law-10 trigger-list positive arm — SC-L11

- **Deliverable:** Law-10 applier's trigger-list arm: an *i-context *k
  whose form matches the recorded trigger class (house/chief) palatalizes,
  trace records `law10-trigger-cite` with the rule-data cite.
- **RED:** `uv run pytest test/test_law10_triggers.py -q` — the
  house/chief-class vector expects palatalization (PSNEA `*wītīwāHm`-class
  t-face) and the cite entry; fails now (negative arm of item 3 still
  governs every *i-context).
- **GREEN:** listed forms palatalize; unlisted forms keep item 3's behavior.
- **Instrument:** `uv run pytest test/test_law10_triggers.py -q` (positive
  vectors from `rules/law10_triggers.yaml`; negative arm re-asserted so the
  arms cannot regress).

### 5. Law-10 *ē arm — SC-L10

- **Deliverable:** unconditional palatalization before PEA *ē plus the
  trace entry recording the application.
- **RED:** `uv run pytest test/test_law10_e_arm.py -q` — a unit *k-before-
  *ē input (e.g. `*ke·tam` → PEA `*kētam`: the final *m is retained under
  the plan's edge rule (c), so no apocope interferes) expects the palatal
  PSNEA face and the trace entry; fails now (no *ē arm exists; the *k
  stays *k).
- **GREEN:** the ē input palatalizes with the trace record.
- **Instrument:** `uv run pytest test/test_law10_e_arm.py -q`.

### 6. †-class analogical exception — SC-L12

- **Deliverable:** `rules/analogical_exceptions.yaml` consulted by the
  Law-10 applier before the trigger arm: a recorded †-class input ('good'/
  -ew paradigm class) does not palatalize via the law, and the trace
  records the `law10-exception-route` entry with its cite.
- **RED:** `uv run pytest test/test_law10_exception.py -q` — the recorded
  good-class vector expects no palatalization AND the exception-route trace
  entry; fails now (the no-palatalization outcome holds via item 3's
  negative arm, but the exception-route trace entry does not exist).
- **GREEN:** the exception route is recorded; palatalization stays off for
  the class; the trigger/ē arms are unaffected.
- **Instrument:** `uv run pytest test/test_law10_exception.py -q`.

### 7. bl_ipa migration home + parity — SC-L7

- **Deliverable:** `src/snea_lib/bl_ipa.py` — the parent implementation
  migrated behavior-unchanged (single home; the module's public functions
  `segment`, `to_ipa_unmarked`, `mark_word`, `mark_stress`, `validate_ipa`,
  `to_ipa` and the letter/phone tables carried intact with their SPDX
  headers). Parity fixture: `test/bl_ipa_parity_words.yaml` — word set =
  Costa-letter BL forms from the parent-record surfaces (the lexicon's
  `bl` fields, `bt-starter-lexicon.yaml`; the primer lesson table's
  `bl_letters` values, `bt-primer-lessons.tsv`); expected IPA captured by
  running the parent's `src/bl_ipa.py` over that word set at
  implementation time and frozen; the test asserts the migrated module
  produces identical output. The starred Table 6 forms stay outside this
  word set (starred phonemic notation, not the module's Costa-letter
  domain — they are item 8's stage-form vectors compared as strings).
- **RED:** `uv run pytest test/test_bl_ipa_parity.py -q` — import of
  `snea_lib.bl_ipa` fails (module absent).
- **GREEN:** parity vectors pass against the migrated module.
- **Instrument:** `uv run pytest test/test_bl_ipa_parity.py -q` (the SC-L7
  parity-run capture in the consumer PR remains the consumer spec's
  instrument; the frozen vector is this repo's behavior guard).

### 8. Forward chain reproduction — SC-L4

- **Deliverable:** complete the forward law set (Laws 1–9, 11, 16(a), the
  cluster rows 20–26, 15/18/19 as table-driven segment swaps) and the
  B-stage (B1–B4, B6, B7 carried/applying; B5 carries, its applications are
  item 14) + the three-face renderer over `rules/bl_rendering.yaml`. The
  eight recorded rows reproduce end to end: PA input → PEA → PSNEA (and BL
  starred where the row records it — all Table 6 rows), asserting the
  recorded elements; the three row's fixture PA input is `*neʔθwi·` (the
  final *i· length reading per Table 5 note f, which the vector cites).
  Rows whose ledger entry also records the orthography and IPA faces
  (house `wiciwôh` `/ˌwiːˈtʃiːˌwʌ̃ːh/`, chief `sôcimôw`, teeth-3s
  `wipitay`, heart `mutáh`, three `nuhshwi`, island `munahan`, person
  `uyuniw`) get face vectors whose IPA face equals `bl_ipa.to_ipa` over
  the derived orthography (all seven verified against the parent module).
  The inan-pl row asserts its recorded elements (starred `*-ar`-chain →
  `**-aš`, orthography `-ash`, and the row's own recorded IPA face `/aʃ/`)
  — the stress rule's scope is words; a suffix citation carries the
  record's own unmarked face rather than a derived stress-marked one,
  and the vector documents that scope. Fixtures inline
  the recorded row strings and cite the row (paper Table 4/6; lexicon id).
  Recorded-string comparison normalizes the record's bare `i`/`o` at
  PEA+ stages to `ī`/`ō` per Table 2's PEA-system statement (documented in
  the fixture).
- **RED:** `uv run pytest test/test_forward_chain.py -q` — the eight-row
  vectors fail (the full forward law set, the B-stage, and the faces are
  absent; items 3–6 deliver only the discipline mechanics and the Law-10
  arms).
- **GREEN:** all rows reproduce their recorded elements; `uv run ruff check
  src/ test/` stays clean.
- **Instrument:** `uv run pytest test/test_forward_chain.py -q`.

### 9. Lawless segments carry and flag — SC-L16

- **Deliverable:** lawless-carry marking: segments with no tracked law
  (*H, the proto-laryngeal; recorded-not-covered segment classes in
  v1: *ʔ coda shapes carried with a note) carry through every stage and
  flag (`lawless-carried`) in both output and trace.
- **RED:** `uv run pytest test/test_lawless_carry.py -q` — the house-row
  vector (recorded chain PA `*wi·kiwa·Hmi` → PSNEA `*wītīwāHm`) asserts
  the carried H and the `lawless-carried` flag; fails now (the flag does
  not exist; the H carries silently after item 8).
- **GREEN:** H carries and flags; the row's stage strings unchanged.
- **Instrument:** `uv run pytest test/test_lawless_carry.py -q`.

### 10. Word-edge laws and the parse-resolved *r contrast — SC-L3

- **Deliverable:** hyphen-marked boundary handling (trailing/internal
  hyphens hold word-edge laws + `edge-hyphen-held` flag) and the explicit
  contrast vectors: stem-level *r (teeth parse: `[stem wi·pital]`
  `[inflection i]`) → B1 → `**wīpītay`; word-final *r (the inanim-pl row
  parse: `[inflection ali]`) → B2 → `**-aš`.
- **RED:** `uv run pytest test/test_word_edges.py -q` — the hyphen vector
  group fails (boundary-token inputs do not yet carry the edge-law
  hold+flag contract — item 8's edge mechanics do not define their
  behavior); the contrast vectors re-assert the parse-resolved split end
  to end.
- **GREEN:** hyphen inputs hold+flag at the boundary; contrast vectors pass
  on both arms.
- **Instrument:** `uv run pytest test/test_word_edges.py -q`.

### 11. Composition subsystem — SC-L5

- **Deliverable:** `composition.py` per the approach decisions; unit
  fixtures with injected inflection data (the recorded inanim-pl `*-ali`
  plus a fixture-declared allomorphic stem exercising A/B selection by
  condition) producing the assembled PA form, the parse, the four trace
  entries, and the provenance flag; the assembled word derives through the
  forward engine with its parse (the teeth-class end-to-end assembly:
  stem `wi·pital-`+`-i` → `*wi·pitali` → `**wīpītay`).
- **RED:** `uv run pytest test/test_composition.py -q` — fails (module
  absent).
- **GREEN:** composition vectors pass; provenance composes (`composed-PA`)
  where assembled and `cited-PA` where the row supplies the whole form.
- **Instrument:** `uv run pytest test/test_composition.py -q`.

### 12. Inverse subsystem — SC-L6

- **Deliverable:** `inverse.py` per the approach decisions, vectors from
  the reversed-rule record's own content: (a) merger→candidate-set
  inversion (inv-Ms-n four-way set; inv-Mp-c two-way set); (b)
  intersection resolution collapsing sets across cognates (friend-class
  resolution: the n-tokens agree on *n ×3) with single-source standings
  carrying the `candidate-set-standing` flag; (c) tie-breaker order vectors
  (weighted-majority give-case y-over-n per B1 with ~0.24 vs ~0.11;
  density tie → attestation density; conservative retention;
  contested → referred flag); (d) daughter-own developments gap-marked
  (per-language short-i note) and the Edwards calibration marker.
- **RED:** `uv run pytest test/test_inverse.py -q` — fails (module absent).
- **GREEN:** vectors pass against `rules/reversed_rules.yaml`.
- **Instrument:** `uv run pytest test/test_inverse.py -q`.

### 13. Cross-verification surface — SC-L17

- **Deliverable:** `cross_verify.py` exposing the forward/inverse comparison:
  a forward PSNEA form inside its cognates' inverse intersection marks
  `confirmed`; outside marks `flagged`. Vectors on rule-data-derived
  fixture sets (teeth-class: forward `*wīpītar` confirmed against
  Mp `*wīpītay` ⊗ WP `*wīpītar` inverses; a forward form with a
  non-member segment flagged).
- **RED:** `uv run pytest test/test_cross_verify.py -q` — fails (module
  absent).
- **GREEN:** comparison surface passes on both arms.
- **Instrument:** `uv run pytest test/test_cross_verify.py -q`.

### 14. B5 applications carry the pending-ratification flag — SC-L13

- **Deliverable:** B5-application mechanics: when a derivation applies a
  recorded B5 application (from `rules/b5_recommendations.yaml` — the
  lexicon's recorded vowel-reduction recommendations), the derivation's
  trace carries a `b5-application` entry and the output carries
  `b5-pending-ratification`; the flag attaches if and only if the trace
  contains a `b5-application` entry — B5-dependent output is never
  produced unflagged, and plain carried-B5 (B5 named in the law chain
  with no application applied — the island/heart rows) produces no flag
  and no `b5-application` entry, matching the lexicon's `flags: []`.
- **RED:** `uv run pytest test/test_b5_flags.py -q` — the
  lets-eat-class vector (applying the recorded recommendation) expects the
  pending-ratification flag; fails now (B5 applies nothing and flags
  nothing after item 8). The island/heart-class vectors assert the
  carried-B5 unflagged arm stays empty-flagged while the applied arm
  flags — the pair pins the distinction.
- **GREEN:** flagged on application; unflagged on plain carry.
- **Instrument:** `uv run pytest test/test_b5_flags.py -q`.

### 15. Confidence class on every output — SC-L14

- **Deliverable:** the confidence field per the approach-decision mapping,
  asserted trace-consistent on forward, composed, and inverse outputs
  (the three-class → `partial`: the `gap-carried-blanket-realized-short`
  divergence note; house-class → `lookup-governed`: its trace carries the
  `law10-trigger-cite` lookup entry, which the stated precedence
  (contested → lookup → partial → fully-derived) outranks the
  `lawless-carried` partial entry riding the same row; a clean identity
  row → `fully-derived`; a contested ladder row → `flagged`; single-source
  inverse standing → `partial`; applied-B5 (lets-eat class) →
  `lookup-governed` with the `b5-pending-ratification` flag; carried-B5
  rows (island/heart class) → `fully-derived` (no `b5-application`
  entry), matching the lexicon's `flags: []`). The trace-consistency rule
  is stated by item 14's flag-attachment rule: the
  `b5-pending-ratification` flag exists if and only if the trace carries a
  `b5-application` entry; the confidence mapping never collapses an
  applied-B5 row into a carried-B5 row's class.
- **RED:** `uv run pytest test/test_marking.py -q -k confidence` — the
  DerivationResult/inverse outputs lack the confidence field; vectors fail.
- **GREEN:** field present and matching the mapping on all surfaced outputs.
- **Instrument:** `uv run pytest test/test_marking.py -q -k confidence`.

### 16. Status on every output — SC-L15

- **Deliverable:** the status field per the approach-decision mapping
  (chain-derived / composed / attested), asserted trace-consistent on
  forward, composed, and inverse outputs.
- **RED:** `uv run pytest test/test_marking.py -q -k status` — vectors fail
  (field absent).
- **GREEN:** field present and matching the mapping.
- **Instrument:** `uv run pytest test/test_marking.py -q -k status`.

### 17. Composed-state all-green — SC-L9

- **Deliverable:** the composed-state gate executed and captured. Items
  1–16 execute their instruments and hold `uvx ruff` green from item 8
  onward by their own GREEN clauses; this item runs the spec's own SC-L9
  instrument at the composed state and captures the outputs as the PR's
  SC-L9 evidence.
- **RED:** the gate run itself. No residue is pre-asserted — items 1–16's
  own GREEN clauses already bound their surfaces, and claiming residual
  findings would be ungrounded; the RED clause is instead the sweep's
  fix-up trigger: any surface the run reports (a type finding pyright
  surfaces for the first time here, a late ruff regression, a test
  failure) is fixed within the item and the re-run captured. The plan
  states no expected findings because none may exist.
- **GREEN:** `uv run pytest test/ -q`, `uvx ruff check src/ test/`, and
  `uvx pyright src/` all green at the composed state — captured as the
  item's evidence.
- **Instrument:** the three commands' output in the execution record (the
  spec's own SC-L9 instrument).

## Blast radius

Files: `src/snea_lib/__init__.py` (docstring's "not yet implemented" note
updated), `src/snea_lib/bl_ipa.py` (new), `src/snea_lib/derivation/*` (new),
`src/snea_lib/derivation/rules/*.yaml` (new, 8 files), `test/*.py` (new, one
file per item), `pyproject.toml` (only if hatch wheel data config proves
necessary). `uv.lock` unchanged (pyyaml already declared; no new deps).
No repository-settings changes; no parent-repo files modified here (the
consumer-side work is the stacked sibling spec's).

## Spec-guard

Out of scope items are excluded by construction: no corpus wiring, no
record-level certification, no CI, no PyPI, no Winslow/Anonymous layers, no
stress-rule implementation beyond the migrated `bl_ipa`, no paradigm
generation, no `.md` sync. B5 applications are recommendations on record —
never treated as ratified (the pending-ratification flag is the marker).