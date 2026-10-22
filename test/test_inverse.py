# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Inverse-subsystem vectors (snea-lib#2, SC-L6).

Inverse mechanics per the recorded reconciliations: merger→candidate-set
inversion, intersection resolution, tie-breaker order, daughter-own
gap-marking. Vectors from the reversed-rule record's own content.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.inverse import (
    CalibrationInversion,
    DaughterForm,
    InversionEngine,
)
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> InversionEngine:
    return InversionEngine(load_rules())


def test_merger_inversion_is_a_set(engine: InversionEngine) -> None:
    # inv-Ms-n: the four-way inverse (the θ/l/r-to-r-to-n merger meets the
    # *n identity in Ms n)
    result = engine.invert(DaughterForm(daughter="Ms", tokens=("n",)))
    assert result.candidate_sets == (("*n", "*θ", "*l", "*r"),)
    # inv-Mp-c: the two-way inverse (inherited *č and palatalized *k)
    result = engine.invert(DaughterForm(daughter="Mp", tokens=("c",)))
    assert result.candidate_sets == (("*č", "*tʲ"),)


def test_one_to_one_singleton(engine: InversionEngine) -> None:
    result = engine.invert(DaughterForm(daughter="Nr", tokens=("ht", "sq")))
    assert result.candidate_sets == (("*ht",), ("*xkw",))


def test_intersection_resolution_by_agreement(engine: InversionEngine) -> None:
    # the friend-class worked case: the multi-cognate n-agreement — the n-
    # tokens ×2 (Nr + Ms-side) — the four-way set collapsed to *n (the
    # ladder's conservative step: the reflex-equal-to-PSNEA identity, the
    # record's "by agreement"); the i/p segments intersect to their
    # singletons directly
    forms = [
        DaughterForm(daughter="Nr", tokens=("n", "i", "p")),
        DaughterForm(daughter="Ms", tokens=("n", "i", "p")),
    ]
    result = engine.resolve(forms)
    first = result.segments[0]
    assert first.value == "*n"
    assert not first.contested
    assert result.segments[1].value == "*ī"
    assert result.segments[2].value == "*p"


def test_single_source_candidate_set_stands(engine: InversionEngine) -> None:
    # the record's reconciliation step 4: a single-source case keeps its
    # candidate set (the ambiguity stays stated)
    result = engine.resolve((DaughterForm(daughter="Nr", tokens=("n", "i")),))
    first = result.segments[0]
    assert first.value is None
    assert first.candidates == ("*n", "*θ", "*l", "*r")
    assert "candidate-set-standing" in [f.id for f in result.flags]
    assert result.segments[1].value == "*ī"


def test_tie_breaker_order(engine: InversionEngine) -> None:
    # step 1: weighted majority — the give case (the B1 grounding: the
    # Y-complex reflex at ~0.24 vs the Narragansett n at ~0.11 → y selected,
    # the displaced alternant recorded)
    sel = engine.tie_break(
        ("y", "n"),
        weights={"y": 0.24, "n": 0.11},
    )
    assert sel.value == "y"
    assert sel.displaced == ("n",)

    # step 2: attestation density — a weights tie resolves on density
    sel = engine.tie_break(
        ("a", "b"),
        weights={"a": 0.10, "b": 0.10},
        densities={"a": 1, "b": 3},
    )
    assert sel.value == "b"

    # step 3: conservative retention — still tied, the PSNEA value carried
    # (the equal-weight counterfactual's **wīpītar-type recorded resolution)
    sel = engine.tie_break(
        ("y", "n", "r"),
        weights={"y": 0.10, "n": 0.10, "r": 0.10},
        psnea_value="r",
    )
    assert sel.value == "r"

    # step 4: contested — referred to the linguist, never averaged
    sel = engine.tie_break(("a", "b"), weights={"a": 0.0, "b": 0.0})
    assert sel.contested
    assert sel.value is None


def test_daughter_own_development_gap_marked(engine: InversionEngine) -> None:
    # the record's per-language short-i note (inv-Ms-i): the daughter-own
    # development is gap-marked in the inversion trace
    result = engine.invert(DaughterForm(daughter="Ms", tokens=("i",)))
    assert result.candidate_sets == (("*ī",),)
    assert "daughter-own-development-marked" in [f.id for f in result.flags]


def test_edwards_calibration_never_sources(engine: InversionEngine) -> None:
    # the Mh (Edwards) layer: corroboration-only — no PSNEA candidate sets
    result = engine.invert_calibration(DaughterForm(daughter="Mh", tokens=("mp",)))
    assert isinstance(result, CalibrationInversion)
    assert result.marker == "corroboration-only"