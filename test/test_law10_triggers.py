# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Law-10 trigger-list vectors (snea-lib#2, SC-L11).

The attested trigger list governs Law-10 in *i-contexts: the recorded
trigger class (house/chief) palatalizes with the cite recorded; the
unlisted-*k negative arm (SC-L2) re-asserted so the arms cannot regress.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.engine import ChainEngine, ChainInput
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


def test_house_class_palatalizes_with_cite(engine: ChainEngine) -> None:
    # the house row: the recorded trigger class palatalizes
    # (paper Table 4: *wi·kiwa·Hmi -> *wītīwāHm; Costa example (1))
    result = engine.derive(ChainInput(form="*wi·kiwa·Hmi"))
    assert result.stage_forms["PSNEA"] == "*wītīwāHm"
    entry = [t for t in result.trace if t.law_id == "law-10" and t.note == "law10-trigger-cite"]
    assert entry, "no law10-trigger-cite trace entry"
    assert "law10-trigger-cite" not in [f.id for f in result.flags if f.id == "law10-unlisted-i-context"]


def test_chief_class_palatalizes_with_cite(engine: ChainEngine) -> None:
    # the chief row (Costa example (1): Ms ⟨sontim⟩, Nr ⟨sâchim⟩)
    result = engine.derive(ChainInput(form="*sa·kima·wa"))
    assert result.stage_forms["PSNEA"] == "*sātīmāw"
    entry = [t for t in result.trace if t.law_id == "law-10" and t.note == "law10-trigger-cite"]
    assert entry, "no law10-trigger-cite trace entry"


def test_unlisted_i_context_still_flags_and_does_not_palatalize(engine: ChainEngine) -> None:
    # the negative arm (SC-L2) cannot regress once the positive arm lands
    result = engine.derive(ChainInput(form="*kini"))
    assert result.stage_forms["PSNEA"] == "*kīn"
    assert "law10-unlisted-i-context" in [f.id for f in result.flags]
    k_seg = next(s for s in result.segments["PSNEA"] if s.sym in ("k", "t"))
    assert k_seg.sym == "k"
    assert not k_seg.palatal