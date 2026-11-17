# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The row-recorded BL-leg y-drop (snea-lib#10).

The pronoun chains' recorded outcomes (the register's recorded chains:
PSNEA *nīy → nī, *kīy → kī — PA *nīθa/*kīθa, y-dialect; the *y-drop, not
a lost *n) are reproduced by the engine as a row-recorded drop at the BL
leg, mirroring the *-ali row's recorded PSNEA apocope precedent. The drop
keys on recorded row facts, never a new general law: Law 6's in-chain
retention of word-final *m/*n/*y is itself a recorded decision (the house
row) and is regression-asserted untouched by the parent suite.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import pytest

from snea_lib.derivation.engine import ChainEngine, ChainInput, ParsePart
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


# (row id, PA form, PSNEA citation form, recorded ortho, recorded ipa sans //)
_Y_DROP_ROWS: tuple[tuple[str, str, str, str, str], ...] = (
    ("pron-1s-y-drop", "*ni·θa", "*ni·y", "ni", "ˈniː"),
    ("pron-2s-y-drop", "*ki·θa", "*ki·y", "ki", "ˈkiː"),
)


@pytest.mark.parametrize("row_id,pa_form,psnea_form,ortho,ipa", _Y_DROP_ROWS)
def test_recorded_y_drop_outcome(
    engine: ChainEngine,
    row_id: str,
    pa_form: str,
    psnea_form: str,
    ortho: str,
    ipa: str,
) -> None:
    """The engine reproduces the recorded chains' BL outcomes from both
    the cited PA inputs and the PSNEA *y citations (SC-1)."""
    for form in (pa_form, psnea_form):
        result = engine.derive(
            ChainInput(
                form=form,
                parse=(ParsePart("inflection", form.lstrip("*")),),
                status="chain-derived",
            )
        )
        assert result.faces["orthography"] == ortho, form
        assert result.faces["ipa"] == ipa, form


@pytest.mark.parametrize("row_id,pa_form,psnea_form,ortho,ipa", _Y_DROP_ROWS)
def test_y_drop_trace_records_the_row_fact(
    engine: ChainEngine,
    row_id: str,
    pa_form: str,
    psnea_form: str,
    ortho: str,
    ipa: str,
) -> None:
    """The derivation trace carries the recorded-fact application at the
    BL leg, citing the recorded row (SC-4) — never a silent edit."""
    result = engine.derive(
        ChainInput(
            form=pa_form,
            parse=(ParsePart("inflection", pa_form.lstrip("*")),),
            status="chain-derived",
        )
    )
    drop_entries = [
        t
        for t in result.trace
        if t.stage == "BL" and "y-koine-recorded-drop" in t.law_id
    ]
    assert drop_entries, f"no recorded-drop trace entry for {row_id}"
    assert row_id in drop_entries[-1].note
    assert drop_entries[-1].cite


def test_no_general_y_drop_law(engine: ChainEngine) -> None:
    """The drop lives in the recorded row facts, not the law tables
    (SC-2): no law id in the law data names a general final-y drop, and
    the house row's recorded in-chain retention (word-final *n retained)
    is asserted behaviorally — the drop never reaches it."""
    laws_blob = str(engine._law_data) + str(engine.rules.get("brothertown_laws", {}))
    assert "y-koine-recorded-drop" not in laws_blob
    # the house row (paper Tables 4/6: PA *wi·kiwa·Hmi) keeps its recorded
    # forward-chain reproduction unchanged — Law 6's in-chain retention
    # asserted behaviorally, unaffected by the row-recorded drop
    from test_forward_chain import ROWS  # the recorded fixtures of record

    house = next(r for r in ROWS if r["id"] == "house")
    result = engine.derive(house["input"])
    assert result.stage_forms.get("PSNEA") == house["psnea"]
    assert result.faces["orthography"] == house["ortho"]
