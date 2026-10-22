# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Composition-subsystem vectors (snea-lib#2, SC-L5).

Whole-word PA forms and their morphological parse (initial/medial/final/
inflection boundaries) assembled from component-shaped inputs (Component
Type, Allomorph-A/B/C variants, Condition fields) plus injected standard PA
inflection data, with provenance marking (cited-PA vs composed-PA) and
every assembly choice (final selected, allomorph taken, inflection attached)
in the trace. Unit fixtures; the assembled word derives through the forward
engine with its parse.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.composition import Allomorph, Component, cited, compose
from snea_lib.derivation.engine import ChainEngine, ChainInput
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


def test_teeth_assembly_end_to_end(engine: ChainEngine) -> None:
    # the teeth-class assembly: the stem (fixture-declared allomorphic A/B,
    # injected) + the recorded 3s inflection -i → *wi·pitali; assembled,
    # the word derives through the forward engine with its parse →
    # **wīpītay (B1, stem-level)
    stem = Component(
        kind="initial",
        allomorphs=(
            Allomorph(name="A", form="wi·pital", condition="before-vowel"),
            Allomorph(name="B", form="wi·pital", condition="before-consonant"),
        ),
    )
    infl = Component(kind="inflection", allomorphs=(Allomorph(name="A", form="i", condition="any"),))
    result = compose((stem, infl))
    assert result.pa_form == "*wi·pitali"
    assert [p.kind for p in result.parse] == ["initial", "inflection"]
    assert result.provenance == "composed-PA"
    trace_kinds = {t.kind for t in result.trace}
    assert {"final-selected", "allomorph-taken", "inflection-attached", "provenance"} <= trace_kinds
    taken = [t for t in result.trace if t.kind == "allomorph-taken"]
    assert any("A" in t.detail and "before-vowel" in t.detail for t in taken)

    forward = engine.derive(ChainInput(form=result.pa_form, parse=result.parse))
    assert forward.stage_forms["BL"] == "**wīpītay"


def test_recorded_suffix_cited(engine: ChainEngine) -> None:
    # the recorded inanim-pl row: the whole form cited → cited-PA; the
    # forward chain's recorded columns reproduce through the citation
    citation = cited("*-ali", (( "inflection", "-ali"),))
    assert citation.pa_form == "*-ali"
    assert citation.provenance == "cited-PA"
    assert any(t.kind == "provenance" and "cited-PA" in t.detail for t in citation.trace)
    forward = engine.derive(ChainInput(form=citation.pa_form, parse=citation.parse))
    assert forward.stage_forms["PSNEA"] == "*-ar"
    assert forward.stage_forms["BL"] == "**-aš"