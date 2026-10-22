# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The ordered stage-wise derivation engine (snea-lib#2, R-L2/R-L3/R-L6).

Stages: PA -> PEA -> PSNEA -> BL, run on token segments (``segments.py``).
Laws dispatch by engine id from the rule data (``rules/forward_laws.yaml``);
each application records a stage form and trace entry. The conservative
discipline is mechanical (the record's own generator convention — Table 5's
generator rules: only laws with stated, environment-obligatory conditions
take a step; optional/gradient laws are noted, not applied; where no stated
law gives a reflex, the value carries and flags — the output flags, never
invents).

Binding mechanics (the validated plan's approach decisions):

- PEA-leg order: the Law-6 edge apocope first (a word-final short vowel
  apocopates before Law 5 would lengthen it — grounded: teeth row
  ``*wīpītar``), then Laws 1, 2, 7 (Law 9 and the 16(a) syncope join with
  the forward-law set), then the word-final *w / *m/*n/*y resolution (after
  the full segmental run — Law 7's y-drop can change what a post-apocope *w
  follows: grounded: person row ``*ǝrǝniw`` vs island row ``*mǝnahan``),
  then the vowel shifts (Laws 4/5 incl. the PEA system's ``*a· → *ā``),
  then the Law-8 note (the environment evaluation at the leg-closed shape —
  grounded: house/chief rows carry the w).
- Operative apocope: word-final SHORT vowels (Law 16(i)'s recorded
  taxonomy); word-final long vowels retained in-chain (the three row's
  recorded retention; the ``gap-carried-blanket-realized-short`` note
  carries the blanket-vs-short divergence explicitly).
- Edge timing is parse-driven: stem-bearing words apocopate at the PEA leg;
  pure-inflection citations at the PSNEA leg per their recorded columns.
- Law 10's arms: the †-class exception route first (R-L4's override rule;
  ships at its plan item), then the unconditional *ē arm, then the attested
  trigger list, then the unlisted-*i-context flag. This module implements
  the arms its item delivers; the remaining arms' checks join at their
  items.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from snea_lib.derivation.render import faces as _render_faces
from snea_lib.derivation.segments import (
    BOUNDARY,
    EA_VOWELS,
    FRICATIVE_HEADS,
    LENGTH_MARK,
    PA_VOWELS,
    RESONENTS,
    Seg,
    serialize,
    tokenize_ea,
    tokenize_pa,
)

EA_POST = EA_VOWELS  # the PEA/PSNEA vowel set (short "a ǝ", long "ī ō ē ā")

# the PEA long-vowel glyphs (post-shift: the length is inside the glyph)
EA_LONGS: frozenset[str] = frozenset(g for g in EA_VOWELS if len(g) > 1)

# Law-2's net cluster outcomes (the recorded pre-PEA + PEA completion
# sequence, one net mapping: PA *ʔθ -> pre-PEA *ʔx -> PEA *hx, etc.).
_LAW2_NET: dict[str, str] = {
    "ʔθ": "hx",
    "hθ": "hx",
    "hl": "hx",
    "ʔl": "hr",
    "nθ": "hr",
}

# the PEA vowel shifts (Laws 4/5 and the PEA system statement: *ǝ < *e;
# *ī < *i and *i·; *ō < *o· (and secondary *o); *ē < *e·; *ā < *a·)
_VOWEL_SHIFTS: dict[str, str] = {
    "e": "ǝ",
    "i": "ī",
    "i·": "ī",
    "o": "ō",
    "o·": "ō",
    "e·": "ē",
    "a·": "ā",
}

# the PEA-leg cluster cells (the rows' recorded PEA cells; the carried
# clusters hp/ht/hk/hč/hs/šk/nt/nk have no entries — preaspiration retention
# Law 15 and the row cells' carry)
_CLUSTER_CELLS_PEA: dict[str, dict[str, str]] = {
    "law-19": {"xp": "hp"},
    "law-20": {"θk": "hk", "xk": "hk", "ʔk": "hk"},
    "law-21": {"ʔt": "ht"},
    "law-22": {"ʔč": "hč"},
    "law-23": {"ʔs": "hs"},
    "law-24": {"nl": "hr"},
    "law-26": {"θkw": "xkw"},
}

_BT_LADDER_CITE = (
    "docs/research/pa-pea-psnea-sound-continuum.tex §sec:brothertown-laws (parent record)"
)

_EDGE_CITE_L6 = (
    "docs/research/pa-pea-psnea-sound-continuum.tex Law 6 (parent record); snea-lib#2 spec R-L6"
)


@dataclass(frozen=True)
class ParsePart:
    """One morphological component: kind ``initial|medial|final|inflection``
    plus its segment material (no boundary hyphens inside; the parts'
    sequence is the morphological order)."""

    kind: str
    form: str


@dataclass(frozen=True)
class ChainInput:
    """A stage input: the starred form (hyphens = morpheme-boundary
    markers, passed through), its stage, an optional parse, optionally the
    recorded class keys the input belongs to, and the origin status the
    output carries (chain-derived for cited PA inputs — the default;
    composed for composition-fed inputs)."""

    form: str
    stage: str = "PA"
    parse: tuple[ParsePart, ...] | None = None
    cls: tuple[str, ...] = ()
    status: str = "chain-derived"

    def __post_init__(self) -> None:
        if self.stage not in ("PA", "PEA", "PSNEA"):
            raise ValueError(f"unsupported input stage: {self.stage!r}")
        if self.status not in ("chain-derived", "composed", "attested"):
            raise ValueError(f"unsupported input status: {self.status!r}")


@dataclass(frozen=True)
class Flag:
    """One discipline/marking flag: id, severity, and its record cite."""

    id: str
    severity: str
    cite: str = ""


@dataclass(frozen=True)
class TraceEntry:
    """One derivation-trace entry: stage, law id, cite, resulting form, and
    an optional note (the noted-not-applied / carried classes)."""

    stage: str
    law_id: str
    cite: str
    form: str
    note: str = ""


@dataclass(frozen=True)
class DerivationResult:
    """Every derivation records stage forms, applied laws, holds, and flags
    in its trace (R-L2). ``faces`` carries the three BL faces (R-L8);
    ``confidence`` class derived from the trace's flags in the plan's
    precedence order (contested → lookup → partial → fully-derived)."""

    stage_forms: dict[str, str]
    segments: dict[str, tuple[Seg, ...]]
    trace: tuple[TraceEntry, ...]
    flags: tuple[Flag, ...]
    faces: dict[str, str] = field(default_factory=dict)
    confidence: str = ""
    status: str = ""


_SEVERITY_RANK: dict[str, str] = {
    "contested": "flagged",
    "lookup": "lookup-governed",
    "partial": "partial",
}


def confidence_from_flags(flags: tuple[Flag, ...]) -> str:
    """The trace-consistent confidence class: the highest-severity flag
    decides (contested → lookup → partial → fully-derived)."""
    for severity in ("contested", "lookup", "partial"):
        if any(f.severity == severity for f in flags):
            return _SEVERITY_RANK[severity]
    return "fully-derived"


def _strip_star(form: str) -> str:
    return form.removeprefix("*")


class ChainEngine:
    """The derivation engine; rule data injected (the library is
    corpus-agnostic — R-L2/R-L10)."""

    def __init__(self, rules: dict[str, dict]) -> None:
        self.rules = rules
        self._law_data: dict[str, dict] = {
            rec["engine_id"]: rec for rec in rules["forward_laws"]["laws"]
        }
        self._triggers = rules["law10_triggers"]
        self._exceptions = rules["analogical_exceptions"]
        self._b5 = rules["b5_recommendations"]

    # -- public ------------------------------------------------------------
    def derive(self, inp: ChainInput) -> DerivationResult:
        trace: list[TraceEntry] = []
        flags: list[Flag] = []
        pieces = self._materialize(inp)
        stage_forms: dict[str, str] = {}
        seg_hist: dict[str, tuple[Seg, ...]] = {}

        if inp.stage == "PA":
            segs = self._pea_leg(pieces, inp, trace, flags)
            stage_forms["PA"] = inp.form
            stage_forms["PEA"] = serialize(segs, "PEA")
            seg_hist["PA"] = self._snapshot(inp)
            seg_hist["PEA"] = tuple(segs)
            segs = self._psnea_leg(segs, pieces, inp, trace, flags)
            stage_forms["PSNEA"] = serialize(segs, "PSNEA")
            seg_hist["PSNEA"] = tuple(segs)
        elif inp.stage == "PSNEA":
            stage_forms["PSNEA"] = inp.form
            segs = [Seg(s.sym, s.palatal, s.component) for s in _flat(pieces)]
            seg_hist["PSNEA"] = tuple(segs)
        else:
            raise ValueError(f"unsupported input stage: {inp.stage!r}")

        starred = self._bl_leg(segs, pieces, trace, flags, inp, stage_forms["PSNEA"])
        stage_forms["BL"] = serialize(starred, "BL")
        seg_hist["BL"] = tuple(starred)
        bl_faces = _render_faces(starred, self.rules["bl_rendering"])
        faces = {
            "starred": bl_faces.starred,
            "orthography": bl_faces.orthography,
            "ipa": bl_faces.ipa,
        }

        return DerivationResult(
            stage_forms=stage_forms,
            segments=seg_hist,
            trace=tuple(trace),
            flags=tuple(flags),
            faces=faces,
            confidence=confidence_from_flags(tuple(flags)),
            status=inp.status,
        )

    # -- helpers -----------------------------------------------------------
    def _materialize(self, inp: ChainInput) -> list[tuple[str, list[Seg]]]:
        """The parse pieces (each piece's segments tagged with the R-L5
        kind; piece material carries no boundary hyphens — the pieces'
        sequence is the morphological order)."""
        parts: list[ParsePart]
        if inp.parse is not None:
            parts = list(inp.parse)
        else:
            parts = [ParsePart(kind="initial", form=_strip_star(inp.form))]
        out = []
        for part in parts:
            tokenized = self._tokenize_stage(part.form, inp.stage)
            out.append((part.kind, [Seg(s.sym, s.palatal, part.kind) for s in tokenized]))
        return out

    def _snapshot(self, inp: ChainInput) -> tuple[Seg, ...]:
        if inp.parse is not None:
            segs: list[Seg] = []
            for part in inp.parse:
                for s in self._tokenize_stage(part.form, inp.stage):
                    segs.append(Seg(s.sym) if s.component == "" else s)
            return tuple(segs)
        return tuple(self._tokenize_stage(inp.form, inp.stage))

    def _tokenize_stage(self, text: str, stage: str) -> list[Seg]:
        if stage == "PA":
            return tokenize_pa(text)
        if stage in ("PEA", "PSNEA"):
            return tokenize_ea(text)
        raise ValueError(f"no tokenizer for stage {stage!r}")

    @staticmethod
    def _cited(rec: dict) -> str:
        anchor = rec.get("anchor") or {}
        return f"{anchor.get('path', '')} {anchor.get('lines', '')}".strip()

    # -- the PEA leg ---------------------------------------------------------
    def _pea_leg(
        self,
        pieces: list[tuple[str, list[Seg]]],
        inp: ChainInput,
        trace: list[TraceEntry],
        flags: list[Flag],
    ) -> list[Seg]:
        segs: list[Seg] = []
        for kind, parts in pieces:
            segs.extend(parts)
        stem_bearing = any(s.component in ("initial", "medial") for s in segs)

        law6_cite = self._cited(self._law_data["law-6"])
        if stem_bearing:
            self._edge_apocope(segs, law6_cite, trace, flags, leg="PEA")
        # else: pure-inflection citations apply their recorded apocope at the PSNEA leg

        self._apply_law1(segs, trace)
        self._apply_law2(segs, trace)
        self._apply_cluster_cells(segs, trace)
        self._apply_law16a(segs, trace)
        self._apply_law7(segs, trace)
        self._apply_law9(segs, trace)
        self._word_final_resolution(segs, law6_cite, trace, flags)
        self._law8_note(segs, trace, flags)
        self._vowel_shifts(segs, trace)
        return segs

    # -- the Law-6 edge applier ----------------------------------------------
    def _edge_apocope(
        self,
        segs: list[Seg],
        cite: str,
        trace: list[TraceEntry],
        flags: list[Flag],
        leg: str,
    ) -> None:
        """The Law-6 edge apocope, by its parse-driven leg:

        - the PEA leg (stem-bearing words): word-final SHORT vowels
          apocopate; long finals retained (the three row's recorded
          retention) carried with the blanket-vs-short divergence note
          (Law 16(i)'s operative short-vowel domain vs Goddard §4's
          blanket statement);
        - the PSNEA leg (pure-inflection citations): the row's own recorded
          drop (the ``*-ali`` row's columns: PEA ``*-ari`` retained, PSNEA
          ``*-ar`` dropped) — the word-final vowel drops whatever its
          post-shift length class.
        """
        if not segs:
            return
        last = segs[-1].sym
        if last == BOUNDARY:
            # SC-L3's hold+flag arm: the hyphen-marked boundary holds the
            # word-edge laws
            trace.append(
                TraceEntry(leg, "law-6", cite, serialize(segs, "PSNEA" if leg == "PSNEA" else "PEA"),
                           note="edge-hyphen-held")
            )
            flags.append(Flag("edge-hyphen-held", "partial", cite))
            return
        if leg == "PSNEA":
            if last in EA_POST:
                segs.pop()
                trace.append(
                    TraceEntry("PSNEA", "law-6", cite, serialize(segs, "PSNEA"),
                               note="recorded apocope at the PSNEA leg (the *-ali row's own columns: *-ari -> *-ar; Table 4 note (b))")
                )
            elif last == "w":
                self._word_final_resolution(segs, cite, trace, flags)
            return
        # the PEA leg
        if last in PA_VOWELS:
            segs.pop()
            trace.append(
                TraceEntry("PEA", "law-6", cite, serialize(segs, "PEA"),
                           note="edge-apocope: word-final short V (Law 16(i)'s operative domain)")
            )
        elif last.endswith(LENGTH_MARK):
            flags.append(Flag("gap-carried-blanket-realized-short", "partial", cite))

    def _word_final_resolution(
        self, segs: list[Seg], cite: str, trace: list[TraceEntry], flags: list[Flag]
    ) -> None:
        """(b) word-final *w: dropped postconsonantally (island row),
        retained postvocalically (chief row); (c) word-final *m/*n/*y
        retained in-chain (house row; Goddard §28's loss scope
        daughter-side)."""
        if not segs:
            return
        last = segs[-1]
        if last.sym == "w":
            prev = segs[-2].sym if len(segs) > 1 else ""
            if _is_pa_vowel(prev) or prev in EA_POST:
                trace.append(
                    TraceEntry("PEA", "law-6", cite, serialize(segs, "PEA"),
                               note="word-final postvocalic *w retained (chief row)")
                )
            elif prev and prev != BOUNDARY:
                segs.pop()
                trace.append(
                    TraceEntry("PEA", "law-6", cite, serialize(segs, "PEA"),
                               note="word-final postconsonantal *w dropped (island row)")
                )
        elif last.sym in ("m", "n", "y"):
            trace.append(
                TraceEntry("PEA", "law-6", cite, serialize(segs, "PEA"),
                           note="word-final *m/*n/*y retained in-chain; Goddard §28 loss scope is daughter-side (house row)")
            )

    # -- the PEA-stage laws ----------------------------------------------------
    def _apply_law1(self, segs: list[Seg], trace: list[TraceEntry]) -> None:
        cite = self._cited(self._law_data["law-1"])
        changed = False
        for i, seg in enumerate(segs):
            if seg.sym in ("θ", "l"):
                segs[i] = Seg("r", seg.palatal, seg.component)
                changed = True
        if changed:
            trace.append(TraceEntry("PEA", "law-1", cite, serialize(segs, "PEA")))

    def _apply_law2(self, segs: list[Seg], trace: list[TraceEntry]) -> None:
        cite = self._cited(self._law_data["law-2"])
        changed = False
        for i, seg in enumerate(segs):
            if seg.sym in _LAW2_NET:
                segs[i] = Seg(_LAW2_NET[seg.sym], seg.palatal, seg.component)
                changed = True
        if changed:
            trace.append(TraceEntry("PEA", "law-2", cite, serialize(segs, "PEA")))

    # -- the cluster cells (the rows' PEA cells; Laws 19-26; 15's carry) --------
    def _apply_cluster_cells(self, segs: list[Seg], trace: list[TraceEntry]) -> None:
        for law_id, mapping in _CLUSTER_CELLS_PEA.items():
            cite = self._cited(self._law_data[law_id])
            changed = False
            for i, seg in enumerate(segs):
                if seg.sym in mapping:
                    segs[i] = Seg(mapping[seg.sym], seg.palatal, seg.component)
                    changed = True
            if changed:
                trace.append(TraceEntry("PEA", law_id, cite, serialize(segs, "PEA")))

    # -- Law 16(a): the in-chain syncope surface (the three row's cell) ----------
    def _apply_law16a(self, segs: list[Seg], trace: list[TraceEntry]) -> None:
        cite = self._cited(self._law_data["law-16"])
        if (
            len(segs) >= 3
            and segs[0].sym in RESONENTS
            and segs[1].sym in PA_VOWELS
            and segs[2].sym[:1] in FRICATIVE_HEADS
        ):
            # the recorded (a) surface (the three row's PEA cell *nhxwi): the
            # word-initial syllable between a resonant and a fricative
            del segs[1]
            trace.append(
                TraceEntry("PEA", "law-16", cite, serialize(segs, "PEA"),
                           note="in-chain surface: Law 16(iii-a) syncope (word-initial syllable, resonant/fricative; the law's own daughter-stage scope noted)")
            )

    # -- Law 9 (the š/s merger; the šk cluster carried per its row) ----------------
    def _apply_law9(self, segs: list[Seg], trace: list[TraceEntry]) -> None:
        cite = self._cited(self._law_data["law-9"])
        changed = False
        for i, seg in enumerate(segs):
            if seg.sym == "š":
                segs[i] = Seg("s", seg.palatal, seg.component)
                changed = True
        if changed:
            trace.append(TraceEntry("PEA", "law-9", cite, serialize(segs, "PEA")))

    def _apply_law7(self, segs: list[Seg], trace: list[TraceEntry]) -> None:
        cite = self._cited(self._law_data["law-7"])
        kept: list[Seg] = []
        changed = False
        for i, seg in enumerate(segs):
            if (
                seg.sym == "y"
                and i > 0
                and not _is_pa_vowel(segs[i - 1].sym)
                and segs[i - 1].sym != BOUNDARY
            ):
                changed = True
                continue  # PA *y drops after a consonant
            kept.append(seg)
        if changed:
            segs[:] = kept
            trace.append(TraceEntry("PEA", "law-7", cite, serialize(segs, "PEA")))

    # -- the vowel shifts (Laws 4/5 + the PEA system) ---------------------------
    def _vowel_shifts(self, segs: list[Seg], trace: list[TraceEntry]) -> None:
        cite = self._cited(self._law_data["law-4"]) + " ; " + self._cited(self._law_data["law-5"])
        changed = False
        for i, seg in enumerate(segs):
            if seg.sym in _VOWEL_SHIFTS:
                segs[i] = Seg(_VOWEL_SHIFTS[seg.sym], seg.palatal, seg.component)
                changed = True
        if changed:
            trace.append(TraceEntry("PEA", "law-4/5", cite, serialize(segs, "PEA")))

    # -- the Law-8 note (recorded-not-applied) -----------------------------------
    def _law8_note(
        self, segs: list[Seg], trace: list[TraceEntry], flags: list[Flag]
    ) -> None:
        """The law's own stated environment, read on the PA-shape segments:
        a *w immediately preceded by a PA long vowel (the `·`-carrying glyph
        — the chief row is the recorded env-case)."""
        cite = self._cited(self._law_data["law-8"])
        for i, seg in enumerate(segs):
            if seg.sym != "w" or i == 0:
                continue
            prev = segs[i - 1].sym
            if prev.endswith(LENGTH_MARK) and prev[:-1] in PA_VOWELS:
                # /V´ː __ : the 'usually drops' law is not environment-
                # obligatory — noted, never applied (the record's generator
                # convention)
                trace.append(
                    TraceEntry("PEA", "law-8", cite, serialize(segs, "PEA"),
                               note="law8-noted-not-applied")
                )
                flags.append(Flag("law8-noted-not-applied", "partial", cite))
                return

    # -- the PSNEA leg ------------------------------------------------------------
    def _psnea_leg(
        self,
        segs: list[Seg],
        pieces: list[tuple[str, list[Seg]]],
        inp: ChainInput,
        trace: list[TraceEntry],
        flags: list[Flag],
    ) -> list[Seg]:
        stem_bearing = any(kind in ("initial", "medial") for kind, _ in pieces)
        if not stem_bearing:
            cite = self._cited(self._law_data["law-6"])
            self._edge_apocope(segs, cite, trace, flags, leg="PSNEA")
            self._word_final_resolution(segs, cite, trace, flags)
        self._apply_law10_arms(segs, inp, trace, flags)
        self._apply_law11(segs, trace)
        self._law16_daughter_side_note(segs, trace, flags)
        self._lawless_carry(segs, trace, flags)
        return segs

    # -- the lawless-carry marking (SC-L16): the proto-laryngeal *H and the
    # -- *ʔ outside its recorded cluster shapes carry and flag lawless ------
    def _lawless_carry(
        self, segs: list[Seg], trace: list[TraceEntry], flags: list[Flag]
    ) -> None:
        cite = (
            "snea-lib#2 spec §5 (the parent #134 §6 edge cases): the *H "
            "proto-laryngeal carries and flags lawless; *ʔ cluster coda only"
        )
        for seg in segs:
            if seg.sym != BOUNDARY and seg.sym in ("H", "ʔ"):
                trace.append(
                    TraceEntry("PSNEA", "lawless", cite, serialize(segs, "PSNEA"),
                               note="lawless-carried")
                )
                flags.append(Flag("lawless-carried", "partial", cite))
                return

    # -- the gap-arm: Law-16's daughter-side scope held + flagged ---------------
    def _law16_daughter_side_note(
        self, segs: list[Seg], trace: list[TraceEntry], flags: list[Flag]
    ) -> None:
        cite = self._cited(self._law_data["law-16"])
        if segs and segs[0].sym == "ǝ":
            trace.append(
                TraceEntry("PSNEA", "law-16", cite, serialize(segs, "PSNEA"),
                           note="daughter-side scope (vowel-deletion set; daughter-stage detail): aphaeresis gap flagged, never filled in-chain")
            )
            flags.append(Flag("gap-environment-law-16-aphaeresis", "partial", cite))

    # -- the Law-10 arms ------------------------------------------------------------
    def _apply_law10_arms(
        self, segs: list[Seg], inp: ChainInput, trace: list[TraceEntry], flags: list[Flag]
    ) -> None:
        cite = self._cited(self._law_data["law-10"])
        trigger_cite = self._trigger_cite()
        # arm 1: the †-class exception routes (R-L4's override rule — the
        # override precedes the arms it overrides): a declared/matching
        # member palatalizes via no Law-10 arm; the k carries
        member = self._exception_member(inp)
        if member is not None:
            trace.append(
                TraceEntry("PSNEA", "law-10", member, serialize(segs, "PSNEA"),
                           note="law10-exception-route")
            )
            flags.append(Flag("law10-exception-route", "lookup", member))
            return
        # This item delivered arm 2 (the unconditional *ē arm); arm 3 (the
        # attested trigger list) and arm 4 follow.
        for i, seg in enumerate(segs):
            if seg.sym != "k":
                continue
            right = self._next_vowel(segs, i)
            if right == "ē":
                segs[i] = Seg("t", True, seg.component)
                trace.append(
                    TraceEntry("PSNEA", "law-10", cite, serialize(segs, "PSNEA"),
                               note="law10-e-arm")
                )
                continue
            if right == "ī":
                if self._trigger_matches(inp.form):
                    segs[i] = Seg("t", True, seg.component)
                    trace.append(
                        TraceEntry("PSNEA", "law-10", trigger_cite,
                                   serialize(segs, "PSNEA"),
                                   note="law10-trigger-cite")
                    )
                    flags.append(Flag("law10-trigger-cite", "lookup", trigger_cite))
                    continue
                trace.append(
                    TraceEntry("PSNEA", "law-10", cite, serialize(segs, "PSNEA"),
                               note="law10-unlisted-i-context")
                )
                flags.append(Flag("law10-unlisted-i-context", "partial", cite))

    def _trigger_matches(self, form: str) -> bool:
        instances = self._triggers["attested_trigger_list"]["instances"]
        form_body = form.removeprefix("*")
        return any(
            inst["context"].removeprefix("*") in form_body for inst in instances
        )

    def _trigger_cite(self) -> str:
        instances = self._triggers["attested_trigger_list"]["instances"]
        cites = sorted({inst["cite"] for inst in instances})
        return " ; ".join(cites)

    def _exception_member(self, inp: ChainInput) -> str | None:
        """The †-class membership test: a declared class key, or the input's
        form matching the class's recorded PA form. Returns the class's cite
        when the input is a member, else None."""
        classes = self._exceptions["exception_classes"]
        form_body = _strip_star(inp.form)
        for cls in classes:
            if cls["id"] in inp.cls:
                return str(cls.get("class_cite", ""))
            recorded = _strip_star(cls.get("recorded_pa_form", ""))
            if recorded and form_body == recorded:
                return str(cls.get("class_cite", ""))
        return None

    def _apply_law11(self, segs: list[Seg], trace: list[TraceEntry]) -> None:
        cite = self._cited(self._law_data["law-11"])
        changed = False
        for i, seg in enumerate(segs):
            if seg.sym in ("hr", "hx"):
                segs[i] = Seg("hš", seg.palatal, seg.component)
                changed = True
        if changed:
            trace.append(TraceEntry("PSNEA", "law-11", cite, serialize(segs, "PSNEA")))

    # -- the BL leg (this item's skeleton: B1/B2/B3; the palatal face is B4's) --
    def _bl_leg(
        self,
        segs: list[Seg],
        pieces: list[tuple[str, list[Seg]]],
        trace: list[TraceEntry],
        flags: list[Flag],
        inp: ChainInput,
        stage_forms_psnea_string: str,
    ) -> list[Seg]:
        out: list[Seg] = []
        b2_applied = False
        last_kind = pieces[-1][0]
        for i, seg in enumerate(segs):
            if seg.sym == BOUNDARY:
                out.append(seg)
                continue
            if seg.sym == "r":
                word_final = self._parse_word_final(segs, i)
                bounded = i + 1 < len(segs) and segs[i + 1].sym == BOUNDARY
                if word_final and (len(pieces) == 1 or (seg.component == last_kind and last_kind in ("final", "inflection"))):
                    out.append(Seg("š", seg.palatal, seg.component))
                    b2_applied = True
                elif bounded:
                    # the hyphen boundary holds the B2 edge law; the *r takes
                    # the stem-level B1 route and the hold flags
                    out.append(Seg("y", seg.palatal, seg.component))
                    trace.append(
                        TraceEntry("BL", "law-6", _EDGE_CITE_L6, serialize(segs, "PSNEA"),
                                   note="edge-hyphen-held")
                    )
                    flags.append(Flag("edge-hyphen-held", "partial", _EDGE_CITE_L6))
                else:
                    out.append(Seg("y", seg.palatal, seg.component))
            elif seg.sym in ("hš", "hs"):
                out.append(Seg("hš", seg.palatal, seg.component))
            else:
                out.append(Seg(seg.sym, seg.palatal, seg.component))
        if b2_applied:
            trace.append(
                TraceEntry("BL", "B2", _BT_LADDER_CITE, serialize(out, "BL"),
                           note="B2 word-final *r > š (the displaced s is the Law-13 gradient, never applied)")
            )
        # B7: the Cunningham-corrected nasal-loss rows carry corrected
        # (PA *nt > t, *nk > k with no nasalized-vowel development)
        b7_applied = False
        for i, seg in enumerate(out):
            if seg.sym == "nt":
                out[i] = Seg("t", seg.palatal, seg.component)
                b7_applied = True
            elif seg.sym == "nk":
                out[i] = Seg("k", seg.palatal, seg.component)
                b7_applied = True
        if b7_applied:
            trace.append(
                TraceEntry("BL", "B7", _BT_LADDER_CITE, serialize(out, "BL"),
                           note="B7 the nasal-loss corrections carry corrected (Law 18)")
            )
        # B5: the recorded applications (recommendations on record, pending
        # ratification — never treated as ratified). Applied when the input
        # declares the recommendation key or the PSNEA form matches the
        # recorded application target; the flag attaches iff the
        # b5-application entry exists.
        b5_cite_self = self.rules["b5_recommendations"]["meta"]["source"]
        for rec in self._b5["recommendations"]:
            applies = (
                rec["id"] in inp.cls
                or stage_forms_psnea_string == rec["applies_to_psnea"]
            )
            if applies:
                trace.append(
                    TraceEntry("BL", "B5", str(b5_cite_self), serialize(out, "BL"),
                               note=f"b5-application: {rec['application']} ({rec['id']}; pending ratification)")
                )
                flags.append(Flag("b5-pending-ratification", "lookup", str(b5_cite_self)))
        if out and out[-1].sym == "š":
            cite13 = self._cited(self._law_data["law-13"])
            trace.append(
                TraceEntry("BL", "law-13", cite13, serialize(out, "BL"),
                           note="law13-never-applied")
            )
            flags.append(Flag("law13-never-applied", "partial", cite13))
        return out

    # -- geometry helpers ----------------------------------------------------------
    @staticmethod
    def _parse_word_final(segs: list[Seg], idx: int) -> bool:
        """True iff the segment at idx is the word-final segment by the
        parse (boundary tokens excluded from the comparison); a boundary
        directly following means a marked continuation — not word-final."""
        if idx + 1 < len(segs) and segs[idx + 1].sym == BOUNDARY:
            return False
        for j in range(idx + 1, len(segs)):
            if segs[j].sym != BOUNDARY:
                return False
        return True

    @staticmethod
    def _next_vowel(segs: list[Seg], idx: int) -> str:
        """The segment immediately following idx, when it is a vowel."""
        if idx + 1 < len(segs) and segs[idx + 1].sym in EA_POST:
            return segs[idx + 1].sym
        return ""


def _is_pa_vowel(sym: str) -> bool:
    """True iff the PA-stage segment is a vowel (short or `·`-long)."""
    if sym in PA_VOWELS:
        return True
    return sym.endswith(LENGTH_MARK) and sym[:-1] in PA_VOWELS


def _flat(pieces: list[tuple[str, list[Seg]]]) -> list[Seg]:
    return [s for _, parts in pieces for s in parts]