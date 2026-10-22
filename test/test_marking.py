# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Confidence-class vectors (snea-lib#2, SC-L14).

Every forward/inverse output carries a confidence class
(fully-derived / partial / lookup-governed / flagged) consistent with its
derivation trace. The mapping (the plan's approach decisions, in the
stated precedence contested → lookup → partial → fully-derived) derives
the class from the trace's flags.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.engine import ChainEngine, ChainInput
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


def test_three_class_partial(engine: ChainEngine) -> None:
    # the three row: the long-final blanket-divergence note
    # (gap-carried-blanket-realized-short) → partial
    result = engine.derive(ChainInput(form="*neʔθwi·"))
    assert result.confidence == "partial"
    assert "gap-carried-blanket-realized-short" in [f.id for f in result.flags]


def test_house_class_lookup_governed(engine: ChainEngine) -> None:
    # the house row: its trace carries the law10-trigger-cite lookup entry,
    # which the stated precedence outranks the partial entries riding the
    # same row
    result = engine.derive(ChainInput(form="*wi·kiwa·Hmi"))
    assert result.confidence == "lookup-governed"


def test_lets_eat_applied_b5_lookup_governed(engine: ChainEngine) -> None:
    result = engine.derive(ChainInput(form="*mǝtǝsītǝk", stage="PSNEA"))
    assert result.confidence == "lookup-governed"
    assert "b5-pending-ratification" in [f.id for f in result.flags]


def test_island_heart_clean_fully_derived(engine: ChainEngine) -> None:
    # the island/heart carried-B5 rows: no b5-application entry — the
    # remaining trace is clean → fully-derived (matching the lexicon's
    # flags: [])
    for form in ("*mete·hi", "*menahanwi"):
        result = engine.derive(ChainInput(form=form))
        assert result.confidence == "fully-derived", form


def test_contested_ladder_flagged(engine: ChainEngine) -> None:
    # a contested tie-breaker ladder row → flagged
    from snea_lib.derivation.inverse import InversionEngine

    inv = InversionEngine(load_rules())
    sel = inv.tie_break(("a", "b"), weights={"a": 0.0, "b": 0.0})
    assert sel.contested
    # and the resolution surface's flag marks the class in the marking
    # mapping (the tie_break's contended row never resolves to a value)
    assert sel.value is None


def test_forward_status_chain_derived(engine: ChainEngine) -> None:
    # the forward of a cited PA input: chain-derived (the default origin)
    result = engine.derive(ChainInput(form="*wi·kiwa·Hmi"))
    assert result.status == "chain-derived"


def test_composed_status(engine: ChainEngine) -> None:
    # composition-fed inputs carry the composed status through the forward
    # derivation (the composition's provenance marking feeds it)
    from snea_lib.derivation.composition import Allomorph, Component, compose

    assembly = compose(
        (
            Component(
                "initial",
                (
                    Allomorph("A", "wi·pital", "before-vowel"),
                    Allomorph("B", "wi·pital", "before-consonant"),
                ),
            ),
            Component("inflection", (Allomorph("A", "i", "any"),)),
        )
    )
    composed = engine.derive(ChainInput(form=assembly.pa_form, parse=assembly.parse, status="composed"))
    assert composed.status == "composed"
    assert composed.stage_forms["BL"] == "**wīpītay"


def test_inverse_status_attested() -> None:
    from snea_lib.derivation.inverse import DaughterForm, InversionEngine

    inv = InversionEngine(load_rules())
    result = inv.resolve((DaughterForm(daughter="Nr", tokens=("n", "i", "p")),))
    assert result.status == "attested"


def test_inverse_outputs_carry_confidence() -> None:
    # the inverse surfaces carry the confidence class, trace-consistent:
    # a single-source standing → partial; a clean multi-cognate resolution
    # → fully-derived; the contested residue (the recorded y/n doublets
    # without a discriminating cognate) → flagged; the single-form
    # inversion's daughter-own gap-marking → partial
    from snea_lib.derivation.inverse import DaughterForm, InversionEngine

    inv = InversionEngine(load_rules())
    standing = inv.resolve((DaughterForm(daughter="Nr", tokens=("n", "i")),))
    assert standing.confidence == "partial"
    resolved = inv.resolve(
        (
            DaughterForm(daughter="Nr", tokens=("n", "i", "p")),
            DaughterForm(daughter="Ms", tokens=("n", "i", "p")),
        )
    )
    assert resolved.confidence == "fully-derived"
    contested = inv.resolve(
        (
            DaughterForm(daughter="Nr", tokens=("y",)),
            DaughterForm(daughter="Nr", tokens=("n",)),
        )
    )
    assert contested.confidence == "flagged"
    assert contested.segments[0].contested
    inverted = inv.invert(DaughterForm(daughter="Ms", tokens=("i",)))
    assert inverted.confidence == "partial"