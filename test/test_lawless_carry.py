# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Lawless-carry vectors (snea-lib#2, SC-L16).

Segments with no tracked law — the proto-laryngeal *H; *ʔ outside its
recorded cluster shapes — carry through and flag ``lawless-carried`` in
both output and trace. Vector on the recorded house chain: the H carries
to PSNEA and flags.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.engine import ChainEngine, ChainInput
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


def test_house_lawless_H_carries_and_flags(engine: ChainEngine) -> None:
    # the house chain: PA *wi·kiwa·Hmi → PSNEA *wītīwāHm — the *H carries
    # through (no tracked law) and flags lawless in output and trace
    result = engine.derive(ChainInput(form="*wi·kiwa·Hmi"))
    assert result.stage_forms["PSNEA"] == "*wītīwāHm"
    assert any(s.sym == "H" for s in result.segments["PSNEA"]), "the H was not carried"
    assert "lawless-carried" in [f.id for f in result.flags]
    entry = [t for t in result.trace if t.note == "lawless-carried"]
    assert entry, "no lawless-carried trace entry"


def test_carried_H_in_bl_face(engine: ChainEngine) -> None:
    # the H's independent-h letter face in the orthography (the record's
    # wiciwôh carries the h)
    result = engine.derive(ChainInput(form="*wi·kiwa·Hmi"))
    assert result.faces["orthography"] == "wiciwôh"