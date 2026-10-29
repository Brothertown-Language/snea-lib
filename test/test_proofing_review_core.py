# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""SC-4: the review core over both anchor families with two injected
vocabularies in one suite; verdicts land on the injected writer only."""
import pytest

from snea_lib.proofing.model import LocatorError
from snea_lib.proofing.review import (
    ImageAnchor,
    InMemoryRegister,
    Region,
    TextAnchor,
    make_vocabulary,
    verdict,
)


def test_text_anchor_family_with_vocab_one():
    vocab = make_vocabulary("proofed", "flagged")
    reg = InMemoryRegister()
    verdict(reg, vocab, TextAnchor("3-7"), "proofed", "2026-10-28", "commit 5e98e43")
    assert reg.records[0].evidence == "commit 5e98e43"


def test_image_anchor_family_with_vocab_two():
    vocab = make_vocabulary("confirmed", "rejected")
    reg = InMemoryRegister()
    rec = verdict(
        reg, vocab,
        ImageAnchor("plate-7.png", Region(((0.1, 0.2), (0.9, 0.2), (0.9, 0.6), (0.1, 0.6)))),
        "confirmed", "2026-10-28", "region re-read",
    )
    assert rec.subject.region.points[0] == (0.1, 0.2)


def test_out_of_vocabulary_states_rejected():
    reg = InMemoryRegister()
    with pytest.raises(LocatorError):
        verdict(reg, make_vocabulary("proofed"), TextAnchor("3-7"), "human-proofed", "2026-10-28", "e")
    with pytest.raises(LocatorError):
        verdict(reg, make_vocabulary("confirmed"), ImageAnchor("p.png", Region(((0, 0), (1, 1)))), "proofed", "2026-10-28", "e")


def test_bad_anchor_and_date_shapes_rejected():
    reg = InMemoryRegister()
    vocab = make_vocabulary("ok")
    with pytest.raises(LocatorError):
        verdict(reg, vocab, TextAnchor("0-2"), "ok", "2026-10-28", "e")
    with pytest.raises(LocatorError):
        verdict(reg, vocab, ImageAnchor("p.txt", Region(((0, 0), (1, 1)))), "ok", "2026-10-28", "e")
    with pytest.raises(LocatorError):
        verdict(reg, vocab, TextAnchor("3-7"), "ok", "10/28/2026", "e")
