# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""B5 pending-ratification vectors (snea-lib#2, SC-L13).

Every output whose derivation applies a recorded B5 application carries
the pending-ratification flag; B5-dependent output is never produced
unflagged; plain carried-B5 (the island/heart rows — no application
applied) produces neither the flag nor a b5-application trace entry,
matching the lexicon's flags: [].

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.engine import ChainEngine, ChainInput
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


def test_recorded_b5_applies_flag_engine(engine: ChainEngine) -> None:
    # the lets-eat record: the PSNEA *mǝtǝsītǝk matches the recorded B5
    # recommendation (vowel reduction, pending ratification); the flag and
    # the b5-application trace entry ride the output
    result = engine.derive(ChainInput(form="*mǝtǝsītǝk", stage="PSNEA"))
    assert "b5-pending-ratification" in [f.id for f in result.flags]
    entry = [t for t in result.trace if t.note.startswith("b5-application:")]
    assert entry, "no b5-application trace entry"
    assert result.faces["orthography"] == "mutusituk"


def test_declared_b5_application_flags(engine: ChainEngine) -> None:
    result = engine.derive(
        ChainInput(form="*kǝnǝnǝnī", stage="PSNEA", cls=("see-2s-1s-goal-vowel-reduction",))
    )
    assert "b5-pending-ratification" in [f.id for f in result.flags]


def test_carried_b5_unflagged(engine: ChainEngine) -> None:
    # the island/heart rows: B5 named in the law chain with no application
    # applied — no flag, no b5-application trace entry (the lexicon's
    # flags: [])
    heart = engine.derive(ChainInput(form="*mete·hi"))
    assert "b5-pending-ratification" not in [f.id for f in heart.flags]
    assert not [t for t in heart.trace if t.note.startswith("b5-application:")]
    island = engine.derive(ChainInput(form="*menahanwi"))
    assert "b5-pending-ratification" not in [f.id for f in island.flags]