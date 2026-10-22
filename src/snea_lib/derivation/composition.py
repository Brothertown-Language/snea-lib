# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The composition subsystem (snea-lib#2 item 11, R-L5).

Whole-word PA forms and their morphological parse (initial/medial/final/
inflection boundaries) assembled from component-shaped inputs: components
declare their kind, their Allomorph-A/B/C variants, and Condition fields
(``before-vowel|before-consonant|word-final|any`` — evaluated table-driven
against the neighbouring component's segment class; no regex). The
standard PA inflection data is injected by the caller (the library stays
corpus-agnostic). Provenance marking: ``composed-PA`` (assembled) vs
``cited-PA`` (the row supplies the whole form). Every assembly choice —
the final component selected, the allomorph taken (name + condition), the
inflection attached, the provenance — is recorded in the trace (R-L6's
composition requirements). The output's parse feeds the forward engine
with the annotations its position-sensitive laws consume (R-L5).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from snea_lib.derivation.engine import ParsePart, _is_pa_vowel
from snea_lib.derivation.segments import BOUNDARY, tokenize_pa

COMPOSITION_CONDITIONS: tuple[str, ...] = (
    "before-vowel",
    "before-consonant",
    "word-final",
    "any",
)


@dataclass(frozen=True)
class Allomorph:
    """One variant of a component: its name (A/B/C per the record's
    shaped-input vocabulary), its form, and the Condition field its
    selection reads on."""

    name: str
    form: str
    condition: str


@dataclass(frozen=True)
class Component:
    """One component-shaped input: kind ``initial|medial|final|inflection``
    with its allomorphic variants."""

    kind: str
    allomorphs: tuple[Allomorph, ...]


@dataclass(frozen=True)
class CompositionEntry:
    """One composition-trace entry (the assembly choices, R-L6)."""

    kind: str
    detail: str


@dataclass(frozen=True)
class CompositionResult:
    """The assembled whole-word PA form, its parse (the R-L5 annotations
    the forward engine's position-sensitive laws consume), the provenance
    marking, and the assembly trace."""

    pa_form: str
    parse: tuple[ParsePart, ...]
    provenance: str
    trace: tuple[CompositionEntry, ...]


def compose(components: Sequence[Component]) -> CompositionResult:
    """Assemble the whole-word PA form from the component sequence (the
    sequence = the morphological order)."""
    if not components:
        raise ValueError("empty component sequence")
    chosen: list[Allomorph] = []
    trace: list[CompositionEntry] = []
    for idx, comp in enumerate(components):
        next_comp = components[idx + 1] if idx + 1 < len(components) else None
        allomorph = _select_allomorph(comp, next_comp, is_last=next_comp is None)
        chosen.append(allomorph)
        trace.append(
            CompositionEntry("allomorph-taken", f"{comp.kind}: {allomorph.name} (condition {allomorph.condition})")
        )
    last = components[-1]
    trace.append(CompositionEntry("final-selected", f"{last.kind}: {chosen[-1].form}"))
    if last.kind == "inflection":
        trace.append(CompositionEntry("inflection-attached", chosen[-1].form))
    trace.append(CompositionEntry("provenance", "composed-PA"))
    pa_form = "*" + "".join(a.form for a in chosen)
    parse = tuple(ParsePart(comp.kind, a.form) for comp, a in zip(components, chosen))
    return CompositionResult(pa_form=pa_form, parse=parse, provenance="composed-PA", trace=tuple(trace))


def cited(pa_form: str, parse: Sequence[tuple[str, str]]) -> CompositionResult:
    """The cited-PA path: the row supplies the whole form (the citation's
    own parse travels with it)."""
    parts = tuple(ParsePart(kind, form) for kind, form in parse)
    trace = (
        CompositionEntry("final-selected", parts[-1].kind if parts else ""),
        CompositionEntry("provenance", "cited-PA"),
    )
    return CompositionResult(
        pa_form=pa_form,
        parse=parts,
        provenance="cited-PA",
        trace=trace,
    )


# -- allomorph selection (the Condition fields, table-driven) -----------------
def _select_allomorph(comp: Component, next_comp: Component | None, *, is_last: bool) -> Allomorph:
    if not comp.allomorphs:
        raise ValueError(f"no allomorphs on component kind {comp.kind!r}")
    for allomorph in comp.allomorphs:
        if _condition_ok(allomorph.condition, next_comp, is_last=is_last):
            return allomorph
    raise ValueError(f"no allomorph condition satisfied for component kind {comp.kind!r}")


def _condition_ok(condition: str, next_comp: Component | None, *, is_last: bool) -> bool:
    if condition not in COMPOSITION_CONDITIONS:
        raise ValueError(f"unknown condition field {condition!r}")
    if condition == "any":
        return True
    if condition == "word-final":
        return is_last
    if next_comp is None:
        return False
    shape = _neighbour_shape(next_comp)
    if condition == "before-vowel":
        return shape == "vowel"
    return shape == "consonant"


def _neighbour_shape(next_comp: Component) -> str | None:
    """The neighbouring component's first segment class (table-driven; the
    first-listed allomorph's material reads the neighbour)."""
    if not next_comp.allomorphs:
        return None
    tokens = tokenize_pa(next_comp.allomorphs[0].form.removeprefix("*"))
    material = [t for t in tokens if t.sym != BOUNDARY]
    if not material:
        return None
    return "vowel" if _is_pa_vowel(material[0].sym) else "consonant"