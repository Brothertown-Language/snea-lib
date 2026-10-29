# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""SC-2: coverage intervals and the OCR-7 extension rule."""
import pytest

from snea_lib.proofing.model import Coverage, LocatorError


def test_covered_set_equals_the_pass_list():
    cov = Coverage.from_pass(["3-7", "page:143"])
    assert cov.covers("3-7") and cov.covers("page:143")


def test_containment_answers_follow():
    cov = Coverage.from_pass(["3-7"])
    assert cov.covers("4-6") and cov.covers("3") and cov.covers("7")
    assert not cov.covers("8-10")


def test_uncovered_reports_not_covered_until_extended():
    cov = Coverage.from_pass(["3-7"])
    assert not cov.covers("9-12")
    cov.extend(["9-12"])  # the OCR-7 extension rule
    assert cov.covers("9-12")


def test_invalid_locators_rejected_at_every_seam():
    with pytest.raises(LocatorError):
        Coverage.from_pass(["0-2"])
    with pytest.raises(LocatorError):
        cov = Coverage.from_pass(["3-7"])
        cov.covers("verse:9")
    with pytest.raises(LocatorError):
        cov = Coverage.from_pass(["3-7"])
        cov.extend(["9-0"])
