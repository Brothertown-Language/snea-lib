# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Law-10 *e-arm vector (snea-lib#2, SC-L10).

Palatalization applies before PEA *e unconditionally, and the application
is recorded in the trace — a unit *k-before-e input exercising the
recorded Law-10 rule data.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.engine import ChainEngine, ChainInput
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


def test_k_before_pea_e_palatalizes_unconditionally(engine: ChainEngine) -> None:
    # a unit *k-before-e input: *ke·tam -> PEA *kētam (the final *m is
    # retained under the word-final rule) -> the k palatalizes before the e
    result = engine.derive(ChainInput(form="*ke·tam"))
    assert result.stage_forms["PEA"] == "*kētam"
    assert result.stage_forms["PSNEA"].startswith("*t")
    k_seg = next(s for s in result.segments["PSNEA"] if s.sym in ("k", "t"))
    assert k_seg.sym == "t"
    assert k_seg.palatal


def test_e_arm_recorded_in_trace(engine: ChainEngine) -> None:
    result = engine.derive(ChainInput(form="*ke·tam"))
    entry = [
        t
        for t in result.trace
        if t.law_id == "law-10" and t.stage == "PSNEA" and t.note == "law10-e-arm"
    ]
    assert entry, "no law10-e-arm trace entry"