# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""SC-1: locator semantics across both kinds (snea-lib#4 R-1)."""
import pytest

from snea_lib.proofing.model import Citation, LineSpan, LocatorError, contains


def test_line_span_parses_3_7_and_7_7():
    assert LineSpan.parse("3-7") == LineSpan(3, 7)
    assert LineSpan.parse("7-7") == LineSpan(7, 7)


def test_zero_based_and_rejected_spans():
    with pytest.raises(LocatorError):
        LineSpan.parse("0-2")
    with pytest.raises(LocatorError):
        LineSpan.parse("8-3")


def test_boundary_containment():
    seven = LineSpan.parse("3-7")
    assert seven.contains(3) and seven.contains(7)
    assert not seven.contains(2) and not seven.contains(8)


def test_adjacency_is_not_overlap_and_nesting_is():
    a, b, inner = LineSpan.parse("3-7"), LineSpan.parse("8-10"), LineSpan.parse("4-6")
    assert not a.overlaps(b)
    assert a.contains(inner) and a.overlaps(inner)


def test_citation_kinds_parse_and_validate():
    assert Citation.parse("page:143") == Citation("page", "143")
    assert Citation.parse("section:2.4") == Citation("section", "2.4")
    assert Citation.parse("paragraph:12") == Citation("paragraph", "12")
    with pytest.raises(LocatorError):
        Citation.parse("verse:21")


def test_citation_containment_within_document_ordering():
    page, section, para = Citation("page", "143"), Citation("section", "2.4"), Citation("paragraph", "12")
    assert contains(page, section) and contains(page, para) and contains(section, para)
    assert not contains(para, section) and not contains(section, page)
    assert contains(("page", "143"), Citation("paragraph", "12"))
