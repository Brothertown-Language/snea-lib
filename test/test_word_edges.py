# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Word-edge law vectors (snea-lib#2, SC-L3).

Word-edge laws hold at true word edges and hold+flag at hyphen boundaries;
the stem-final vs suffix-final *r contrast resolves by the supplied parse
(B1 → y as stem-level, B2 → š as word-final).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.engine import ChainEngine, ChainInput, ParsePart
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


def test_word_edge_applies_at_true_edge(engine: ChainEngine) -> None:
    # the inan.-pl row: the suffix realized word-finally — the edge laws
    # APPLY (the row's own recorded columns: PEA *-ari → PSNEA *-ar → **-aš)
    result = engine.derive(ChainInput(form="*-ali", parse=(ParsePart("inflection", "-ali"),)))
    assert result.stage_forms["PSNEA"] == "*-ar"
    assert result.stage_forms["BL"] == "**-aš"


def test_hyphen_trailing_edge_laws_hold_and_flag(engine: ChainEngine) -> None:
    # the trailing-hyphen continuation marks the boundary: word-edge laws
    # hold there and flag (SC-L3's hold+flag arm) — the recorded apocope
    # does not apply at the hyphen boundary (the -ī retained); the *r at
    # the boundary takes the non-final B1 route
    result = engine.derive(ChainInput(form="*-ali-"))
    assert result.stage_forms["PSNEA"] == "*-arī-"
    assert result.stage_forms["BL"] == "**-ayī-"
    assert "edge-hyphen-held" in [f.id for f in result.flags]
    entry = [t for t in result.trace if t.note == "edge-hyphen-held"]
    assert entry, "no edge-hyphen-held trace entry"


def test_hyphen_bounded_r_takes_stem_level(engine: ChainEngine) -> None:
    # a trailing-hyphen stem citation: the *r at the hyphen boundary is not
    # word-final — the B2 edge law holds+flags and the *r takes B1 (y)
    result = engine.derive(ChainInput(form="*wīpītar-", stage="PSNEA"))
    # the boundary passes through the starred notation (the record's
    # citation convention)
    assert result.stage_forms["BL"] == "**wīpītay-"
    assert "edge-hyphen-held" in [f.id for f in result.flags]


def test_contrast_stem_level_vs_word_final(engine: ChainEngine) -> None:
    # the teeth/suffix *r contrast (spec §5): same string-final PSNEA *r —
    # stem-level via B1 → y vs word-final via B2 → š — resolved by the
    # supplied parse, never by the phonological string
    stem_level = engine.derive(
        ChainInput(
            form="*wi·pitali",
            parse=(ParsePart("initial", "wi·pital"), ParsePart("inflection", "i")),
        )
    )
    assert stem_level.stage_forms["BL"] == "**wīpītay"  # B1 (stem-level)
    word_final = engine.derive(ChainInput(form="*-ar", stage="PSNEA"))
    assert word_final.stage_forms["BL"] == "**-aš"  # B2 (word-final)