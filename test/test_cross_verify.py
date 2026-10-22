# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Cross-verification surface vectors (snea-lib#2, SC-L17).

The library exposes the forward/inverse comparison so a consumer marks a
forward PSNEA confirmed (inside its cognates' inverse intersection) or
flagged (outside); the library performs the set comparison. Vectors on
rule-data-derived fixture sets.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.cross_verify import CrossVerifier
from snea_lib.derivation.engine import ChainEngine, ChainInput
from snea_lib.derivation.inverse import DaughterForm, InversionEngine
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def verifier() -> CrossVerifier:
    rules = load_rules()
    forward = ChainEngine(rules)
    inverse = InversionEngine(rules)
    return CrossVerifier(forward, inverse)


def test_confirmed_inside_intersection(verifier: CrossVerifier) -> None:
    # teeth-class: the forward PSNEA *wīpītar sits inside the Mp cognate's
    # inversion candidates (the y-token's set contains the r)
    verdict = verifier.verify(
        ChainInput(form="*wīpītar", stage="PSNEA"),
        (DaughterForm(daughter="Mp", tokens=("w", "i", "p", "i", "t", "a", "y")),),
    )
    assert verdict.per_segment[6].verdict == "confirmed"
    assert verifier.verdict(verdict) == "confirmed"


def test_flagged_outside_intersection(verifier: CrossVerifier) -> None:
    # a forward form with a segment outside its cognates' inverse
    # intersection marks flagged: the Mp y-token's set (the r-set) does not
    # contain *n
    verdict = verifier.verify(
        ChainInput(form="*wīpītan", stage="PSNEA"),
        (DaughterForm(daughter="Mp", tokens=("w", "i", "p", "i", "t", "a", "y")),),
    )
    assert verdict.per_segment[6].verdict == "flagged"
    assert verdict.per_segment[6].note
    assert verifier.verdict(verdict) == "flagged"


def test_two_cognate_intersection(verifier: CrossVerifier) -> None:
    verdict = verifier.verify(
        ChainInput(form="*wīpītar", stage="PSNEA"),
        (
            DaughterForm(daughter="Mp", tokens=("w", "i", "p", "i", "t", "a", "y")),
            DaughterForm(daughter="WP", tokens=("w", "i", "p", "i", "t", "a", "r")),
        ),
    )
    # five singleton segments confirm directly; the r segment resolves
    # inside the two-cognate intersection
    assert [s.verdict for s in verdict.per_segment[:5]] == ["confirmed"] * 5
    assert verdict.per_segment[6].verdict == "confirmed"
    assert verifier.verdict(verdict) == "confirmed"