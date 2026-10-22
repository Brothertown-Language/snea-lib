# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The inverse subsystem (snea-lib#2 item 12, R-L7).

Daughter attestations convert to PSNEA candidate sets: table-driven
per-daughter inverses from the reversed-rule record (``rules/
reversed_rules.yaml``), merger inversion as candidate sets, resolution by
multi-cognate intersection and the recorded tie-breaker ladder, and
daughter-own developments gap-marked. The v1 source registry is the
exercised set (spec R-L7): Williams 1643 (Nr + Ms-side Chart-B), Prince-
Speck 1904 (Mp), Wood 1634 and Trumbull 1903 (Ms-side), Edwards 1787 (Mh,
calibration only — its forms corroborate, they never source a PSNEA
stage); Winslow 1624 and Anonymous 1647 are excluded pending conversion-
layer certification anchors. The daughter forms enter as ALREADY-CONVERTED
phoneme tokens: the library references the conversion cards (the parent
record holds them), never reimplements them, and stays corpus-agnostic.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from snea_lib.derivation.engine import (
    Flag,
    TraceEntry,
    confidence_from_flags,
)

# the daughter-column → founding-bloc weight mapping (the validated plan's
# stated map, grounded in the parent record's weights and the reconciliation's
# daughter_columns_mean: Ms-side cognates corroborate/densify; Mh calibrates)
DAUGHTER_WEIGHTS: dict[str, tuple[str, float]] = {
    "Mp": ("Y-complex (Mohegan-Pequot-Montauk-Niantic)", 0.24),
    "Nr": ("Narragansett", 0.11),
    "WP": ("Wampanoag-area emigrants", 0.10),
}
CORROBORATION_ONLY = "corroboration-only"
_CALIBRATION_CITE = (
    "docs/research/psnea-reversed-rule-inventory.yaml calibration_inversion (parent record); snea-lib#2 spec R-L7"
)


@dataclass(frozen=True)
class DaughterForm:
    """One daughter attestation as already-converted phoneme tokens."""
    daughter: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class InvertedForm:
    """The per-segment candidate sets (a one_to_many rule yields the full
    set; a merger's inverse is never a single guessed value). ``confidence``
    class derived from this inversion's flags in the stated precedence."""
    candidate_sets: tuple[tuple[str, ...], ...]
    trace: tuple[TraceEntry, ...] = field(default_factory=tuple)
    flags: tuple[Flag, ...] = field(default_factory=tuple)
    confidence: str = ""


@dataclass(frozen=True)
class CalibrationInversion:
    """The calibration layer's inversion record: corroboration only, never
    a PSNEA source (the Mh/Edwards marker)."""
    tokens: tuple[str, ...]
    marker: str = CORROBORATION_ONLY
    trace: tuple[TraceEntry, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Selection:
    """One segment's reconciliation outcome."""
    value: str | None
    candidates: tuple[str, ...]
    displaced: tuple[str, ...] = ()
    contested: bool = False
    ladder_note: str = ""


@dataclass(frozen=True)
class ResolutionResult:
    """The PSNEA reconstruction result per segment. ``confidence`` class
    derived from the resolution's flags in the stated precedence."""
    segments: tuple[Selection, ...]
    trace: tuple[TraceEntry, ...] = field(default_factory=tuple)
    flags: tuple[Flag, ...] = field(default_factory=tuple)
    status: str = "attested"
    confidence: str = ""


class InversionEngine:
    """The inverse engine; rule data injected."""

    def __init__(self, rules: dict[str, dict]) -> None:
        self.rules = rules
        self._columns: dict[str, dict] = {
            str(k): v for k, v in rules["reversed_rules"]["reversed_rules"].items()
        }
        self._principles = rules["reversed_rules"]["inversion_principles"]

    # -- per-daughter inversion (the candidate sets) -------------------------
    def invert(self, form: DaughterForm) -> InvertedForm:
        if form.daughter == "Mh":
            raise ValueError(
                "the Mh layer is calibration-only (corroboration, never a PSNEA "
                "source); use invert_calibration"
            )
        if form.daughter not in self._columns:
            raise ValueError(f"no reversed-rule column for daughter {form.daughter!r}")
        rules = self._columns[form.daughter]["rules"]
        sets: list[tuple[str, ...]] = []
        trace: list[TraceEntry] = []
        flags: list[Flag] = []
        for token in form.tokens:
            rule = self._match(rules, token)
            if rule is None:
                # the column states no reflex for this shape: gap-marked,
                # never filled (the record's inversion principles)
                flags.append(Flag("gap-environment-inverse-no-rule", "partial", ""))
                continue
            candidates = tuple(rule["psnea"])
            sets.append(candidates)
            trace.append(TraceEntry("inverse", rule["id"], "", "", note=str(rule["type"])))
            if rule.get("note"):
                # the record's per-language developments: gap-marked
                flags.append(Flag("daughter-own-development-marked", "partial", ""))
        if len(sets) != len(form.tokens):
            raise ValueError(
                f"daughter {form.daughter!r} token(s) without a recorded inverse column rule"
            )
        return InvertedForm(
            candidate_sets=tuple(sets),
            trace=tuple(trace),
            flags=tuple(flags),
            confidence=confidence_from_flags(tuple(flags)),
        )

    def invert_calibration(self, form: DaughterForm) -> CalibrationInversion:
        """The Mh (Edwards) layer: corroboration-only — the inversion is
        marked, it never sources a PSNEA stage."""
        trace = (
            TraceEntry(
                "inverse", "calibration", _CALIBRATION_CITE, "", note="corroboration-only",
            ),
        )
        return CalibrationInversion(tokens=form.tokens, marker=CORROBORATION_ONLY, trace=trace)

    # -- multi-cognate resolution (the recorded procedure) --------------------
    def resolve(self, forms: Sequence[DaughterForm | CalibrationInversion]) -> ResolutionResult:
        """Multi-cognate intersection per segment (the record's
        reconciliation: procedure step 4) with the tie-breaker ladder for
        the residue (step 5)."""
        inverted: list[InvertedForm] = []
        calib: list[CalibrationInversion] = []
        for form in forms:
            if isinstance(form, CalibrationInversion):
                calib.append(form)
                continue
            if isinstance(form, DaughterForm):
                inverted.append(self.invert(form))
                continue
            raise TypeError(f"unsupported inversion input: {type(form).__name__}")
        if not inverted:
            raise ValueError("no invertible daughter forms in the cognate set")
        lengths = {len(inv.candidate_sets) for inv in inverted}
        if len(lengths) != 1:
            raise ValueError(
                f"cognate forms disagree in segment count: {sorted(lengths)} — "
                "the deleted-segment records are not recoverable from the "
                "daughter form alone; align the cognate set"
            )
        n = lengths.pop()
        if calib:
            # the calibration cognates corroborate; they never source
            pass
        seg_selected: list[Selection] = []
        trace: list[TraceEntry] = []
        flags: list[Flag] = []
        for i in range(n):
            sets = [set(inv.candidate_sets[i]) for inv in inverted]
            inter = set.intersection(*sets)
            ordered = tuple(s for s in inverted[0].candidate_sets[i] if s in inter)
            if len(ordered) == 1:
                seg_selected.append(Selection(value=ordered[0], candidates=ordered))
                continue
            if len(inverted) == 1:
                # the record's step 4: a single-source case keeps its
                # candidate set; the ambiguity stays stated
                flags.append(Flag("candidate-set-standing", "partial", ""))
                seg_selected.append(Selection(value=None, candidates=ordered))
                continue
            # the residue (record step 5): the cognate tokens decide the
            # route — shared tokens resolve by the ladder's conservative
            # step (the record's by-agreement); divergent tokens are a koine
            # selection point resolved by the ladder's weighted steps
            source_forms = [f for f in forms if isinstance(f, DaughterForm)]
            tokens = [form.tokens[i] for form in source_forms]
            distinct = list(dict.fromkeys(tokens))
            if len(distinct) == 1:
                sel = self.tie_break(ordered, reflex=distinct[0])
            else:
                weights: dict[str, float] = {}
                for form in source_forms:
                    if form.daughter in DAUGHTER_WEIGHTS:
                        weights[form.tokens[i]] = max(
                            weights.get(form.tokens[i], 0.0),
                            DAUGHTER_WEIGHTS[form.daughter][1],
                        )
                densities = {t: sum(1 for tk in tokens if tk == t) for t in distinct}
                sel = self.tie_break(tuple(distinct), weights=weights, densities=densities)
            if sel.contested:
                flags.append(Flag("contested", "contested", ""))
            seg_selected.append(sel)
            if sel.displaced:
                trace.append(
                    TraceEntry("inverse", "reconciliation", "", "",
                               note=f"residue: {sel.displaced!r} recorded displaced")
                )
        return ResolutionResult(
            segments=tuple(seg_selected),
            trace=tuple(trace),
            flags=tuple(flags),
            status="attested",
            confidence=confidence_from_flags(tuple(flags)),
        )

    # -- the tie-breaker ladder (the recorded four-step order) ----------------
    def tie_break(
        self,
        members: Sequence[str],
        *,
        weights: Mapping[str, float] | None = None,
        densities: Mapping[str, int] | None = None,
        psnea_value: str | None = None,
        reflex: str | None = None,
    ) -> Selection:
        """The recorded tie-breaker ladder, applied in order:
        (1) weighted majority (demographic x evidential);
        (2) attestation density;
        (3) conservative retention — the reflex equal to the PSNEA value
            itself (the un-innovated side: the PSNEA value carried where the
            carry is among the members, else the reflex-identity member);
        (4) contested: referred to the linguist, never averaged or
            coin-flipped."""
        members = tuple(members)
        if not members:
            raise ValueError("no members to break")
        w = dict(weights or {})
        d = dict(densities or {})
        if w:
            top = max(w.values())
            ranked = tuple(m for m in members if w.get(m, 0.0) == top)
            if len(ranked) == 1:
                return Selection(
                    value=ranked[0],
                    candidates=members,
                    displaced=tuple(m for m in members if m != ranked[0]),
                    ladder_note="ladder step 1 (weighted majority)",
                )
            members = ranked
        if densities is not None:
            dens = {m: d.get(m, 0) for m in members}
            top = max(dens.values())
            ranked = tuple(m for m in members if dens[m] == top)
            if len(ranked) == 1:
                return Selection(
                    value=ranked[0],
                    candidates=members,
                    displaced=tuple(m for m in members if m != ranked[0]),
                    ladder_note="ladder step 2 (attestation density)",
                )
            members = ranked
        if psnea_value is not None and psnea_value in members:
            return Selection(
                value=psnea_value,
                candidates=members,
                displaced=tuple(m for m in members if m != psnea_value),
                ladder_note="ladder step 3 (conservative retention: the PSNEA value carried)",
            )
        if reflex is not None:
            identity = tuple(m for m in members if m.removeprefix("*") == reflex)
            if len(identity) == 1:
                return Selection(
                    value=identity[0],
                    candidates=members,
                    displaced=tuple(m for m in members if m != identity[0]),
                    ladder_note="ladder step 3 (conservative retention: the reflex-equal-to-PSNEA identity)",
                )
        return Selection(
            value=None,
            candidates=members,
            contested=True,
            ladder_note="ladder step 4 (contested: referred to the linguist)",
        )

    @staticmethod
    def _match(rules: list[dict], token: str) -> dict | None:
        for rule in rules:
            if token in (rule.get("reflexes") or []):
                return rule
        return None