# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The cross-verification surface (snea-lib#2 item 13, R-L9).

The library exposes the forward/inverse comparison so a consumer marks a
forward PSNEA confirmed (inside its cognates' inverse intersection) or
flagged (outside); the library performs the set comparison. The dual-route
record that exercises it lives in the parent (the consumer spec's
certification; R-L9's division of labor).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from snea_lib.derivation.engine import ChainEngine, ChainInput
from snea_lib.derivation.inverse import CalibrationInversion, DaughterForm, InversionEngine


@dataclass(frozen=True)
class SegmentVerdict:
    """One segment's comparison outcome."""
    verdict: str  # "confirmed" | "flagged"
    forward: str
    candidates: tuple[str, ...]
    note: str = ""


@dataclass(frozen=True)
class CrossVerdict:
    """The per-segment comparison result over the cognate set."""
    per_segment: tuple[SegmentVerdict, ...]
    cognates: tuple[str, ...] = field(default_factory=tuple)


def _member_core(member: str) -> str:
    """The candidate's core phoneme: the star stripped and any
    parenthetical row-identity qualifier dropped (the record's candidate
    strings, e.g. ``*r (word-final, via the r-set)``)."""
    return member.split("(")[0].strip().removeprefix("*")


class CrossVerifier:
    """The set comparison; the forward and inverse engines injected."""

    def __init__(self, forward: ChainEngine, inverse: InversionEngine) -> None:
        self._forward = forward
        self._inverse = inverse

    def verify(
        self, psnea: ChainInput, cognates: Sequence[DaughterForm | CalibrationInversion]
    ) -> CrossVerdict:
        """Compare the forward PSNEA form against its cognates' inverse
        candidate sets, per segment."""
        forward_result = self._forward.derive(psnea)
        segs = forward_result.segments["PSNEA"]
        material = [s for s in segs if s.sym != "-"]
        inverted = []
        for c in cognates:
            if isinstance(c, DaughterForm):
                inverted.append(self._inverse.invert(c))
            else:
                # the calibration layer corroborates; it never sources
                continue
        if not inverted:
            raise ValueError("no invertible cognates for the comparison")
        if len(inverted[0].candidate_sets) != len(material):
            raise ValueError(
                "cognate-inversion segment count does not match the forward form; "
                "align the cognate set"
            )
        per_segment: list[SegmentVerdict] = []
        for i, seg in enumerate(material):
            sets = [set(inv.candidate_sets[i]) for inv in inverted]
            inter = set.intersection(*sets)
            cores = {_member_core(m) for m in inter}
            if seg.sym in cores:
                per_segment.append(
                    SegmentVerdict("confirmed", seg.sym, tuple(sorted(inter)))
                )
            else:
                per_segment.append(
                    SegmentVerdict(
                        "flagged",
                        seg.sym,
                        tuple(sorted(inter)),
                        note=(
                            f"the forward {seg.sym!r} sits outside its cognates' inverse "
                            "intersection"
                        ),
                    )
                )
        return CrossVerdict(
            per_segment=tuple(per_segment),
            cognates=tuple(
                form.daughter for form in cognates if isinstance(form, DaughterForm)
            ),
        )

    @staticmethod
    def verdict(result: CrossVerdict) -> str:
        """The overall verdict: any flagged segment marks the form flagged."""
        if any(s.verdict == "flagged" for s in result.per_segment):
            return "flagged"
        return "confirmed"