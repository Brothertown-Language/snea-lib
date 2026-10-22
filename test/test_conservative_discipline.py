# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Conservative-discipline vectors (snea-lib#2, SC-L2).

The four negative arms, mechanically: Law 13 never applies; Law 8 is
noted-not-applied; gap-marked environments flag-not-fill; an unlisted
Law-10 *i-context *k does not palatalize and flags. Each vector cites its
grounded record surface.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.engine import ChainEngine, ChainInput
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


def test_law13_never_applies(engine: ChainEngine) -> None:
    # the inan.-pl row's recorded PSNEA *-ar: word-final *r takes B2 (š);
    # the Law-13 gradient (š > s) never applies — the **-aš face keeps š
    result = engine.derive(ChainInput(form="*-ar", stage="PSNEA"))
    assert result.stage_forms["BL"] == "**-aš"
    assert result.stage_forms["BL"].endswith("š")
    entry = [t for t in result.trace if t.note == "law13-never-applied" and t.law_id == "law-13"]
    assert entry, "no law13-never-applied trace entry"
    assert "law13-never-applied" in [f.id for f in result.flags]


def test_law8_noted_not_applied(engine: ChainEngine) -> None:
    # the chief row *sa·kima·wa: the *w after the PA long *a· is Law-8's
    # environment; the 'usually drops' law is not environment-obligatory —
    # noted, and the w is retained in the PEA form (the record's PEA column)
    result = engine.derive(ChainInput(form="*sa·kima·wa"))
    assert result.stage_forms["PEA"] == "*sākīmāw"
    entry = [t for t in result.trace if t.note == "law8-noted-not-applied" and t.law_id == "law-8"]
    assert entry, "no law8-noted-not-applied trace entry"
    assert "law8-noted-not-applied" in [f.id for f in result.flags]


def test_law13_and_law8_absent_without_env(engine: ChainEngine) -> None:
    # the person row carries no Law-8 environment (its *w follows a short
    # PA *i) and no word-final š — neither note may fire
    result = engine.derive(ChainInput(form="*elenyiwa"))
    note_ids = {t.note for t in result.trace}
    assert "law8-noted-not-applied" not in note_ids
    assert "law13-never-applied" not in [f.id for f in result.flags]


def test_gap_environment_flags_not_fills(engine: ChainEngine) -> None:
    # the person row's word-initial unstressed *ǝ: the aphaeresis arm
    # (Law 16(ii)) is daughter-stage detail — held in-chain, gap flagged,
    # never filled: the *ǝ survives to PSNEA
    result = engine.derive(ChainInput(form="*elenyiwa"))
    assert result.stage_forms["PSNEA"] == "*ǝrǝnīw"
    assert "gap-environment-law-16-aphaeresis" in [f.id for f in result.flags]


def test_law10_unlisted_i_context_flagged(engine: ChainEngine) -> None:
    # a *k before PA *i that is not on the attested trigger list (house/
    # chief) does not palatalize and flags
    result = engine.derive(ChainInput(form="*kini"))
    assert result.stage_forms["PSNEA"] == "*kīn"
    entry = [t for t in result.trace if t.note == "law10-unlisted-i-context" and t.law_id == "law-10"]
    assert entry, "no law10-unlisted-i-context trace entry"
    assert "law10-unlisted-i-context" in [f.id for f in result.flags]
    k_seg = next(s for s in result.segments["PSNEA"] if s.sym in ("k", "t"))
    assert k_seg.sym == "k"
    assert not k_seg.palatal