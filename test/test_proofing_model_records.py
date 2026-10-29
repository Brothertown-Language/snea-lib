# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""SC-3: the four-status vocabulary and record-field roundtrip."""
import pytest

from snea_lib.proofing.model import Record, LocatorError, parse_date


def test_four_statuses_accepted_and_outside_rejected():
    for state in ("proofed", "unproofed-working-copy", "flagged", "born-digital-not-applicable"):
        Record(state, "2026-10-28", ("3-7",))
    with pytest.raises(LocatorError):
        Record("human-proofed", "2026-10-28", ("3-7",))
    with pytest.raises(TypeError):
        Record("proofed", "2026-10-28", ("3-7",), "partially")


def test_record_fields_roundtrip():
    r = Record("proofed", "2026-10-28", ("3-7", "page:143"))
    assert (r.status, r.proofing_date) == ("proofed", "2026-10-28")
    assert r.covered == ("3-7", "page:143")


def test_dates_validated():
    with pytest.raises(LocatorError):
        Record("proofed", "not-a-date")
    assert parse_date("2026-10-28").year == 2026
