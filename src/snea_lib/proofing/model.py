# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The runbook's locator space and record semantics (OCR-1 through OCR-9).

The semantics' source of record: the OCR-sourcing proofing runbook
(`docs/runbooks/ocr-sourcing-proofing.md`), read at authoring time.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date as date_type
from typing import Iterable

# The closed four-status vocabulary (the runbook's). A token outside this
# set is not a status; consumers inject the review-level vocabulary, but the
# proofing-pass statuses are exactly these four.
STATUSES = frozenset(
    {"proofed", "unproofed-working-copy", "flagged", "born-digital-not-applicable"}
)

_SPAN_RE = re.compile(r"^(\d+)-(\d+)$")


class LocatorError(ValueError):
    """A locator outside the runbook's locator space."""


def _valid_year(iso: str) -> bool:
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", iso)
    if not m:
        return False
    y, mo, d = (int(x) for x in m.groups())
    return 1 <= mo <= 12 and 1 <= d <= 31


@dataclass(frozen=True)
class LineSpan:
    """A one-based, inclusive ``START-END`` line span in a tracked text layer."""

    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 1 or self.end < self.start:
            raise LocatorError(f"line span {self.start}-{self.end}: must be one-based, START<=END")

    @classmethod
    def parse(cls, text: str) -> "LineSpan":
        m = _SPAN_RE.fullmatch(text.strip())
        if not m:
            raise LocatorError(f"{text!r}: not a START-END line span")
        return cls(int(m.group(1)), int(m.group(2)))

    def contains(self, other) -> bool:
        """Boundary containment: 3-7 contains 3 and 7, not 2 or 8; a nested
        span is contained; an adjacent span (3-7 vs 8-10) is not."""
        if isinstance(other, int):
            return self.start <= other <= self.end
        return self.start <= other.start and other.end <= self.end

    def overlaps(self, other: "LineSpan") -> bool:
        return self.start <= other.end and other.start <= self.end


@dataclass(frozen=True)
class Citation:
    """A printed-work citation locator: page, section, or paragraph — for
    documents with no line layer. One of the three kinds carries the value."""

    kind: str  # "page" | "section" | "paragraph"
    value: str

    def __post_init__(self) -> None:
        if self.kind not in ("page", "section", "paragraph"):
            raise LocatorError(f"citation kind {self.kind!r}: unknown kind")

    @classmethod
    def parse(cls, text: str) -> "Citation":
        m = re.fullmatch(r"(page|section|paragraph):(.+)", text.strip())
        if not m:
            raise LocatorError(f"{text!r}: not a page/section/paragraph citation")
        return cls(m.group(1), m.group(2))


# The locator kinds a document-level containment decision understands. A
# document orders its citations by its own kind sequence; containment within
# the same document means the same kind with equal-or-containing scope.
_CITATION_ORDER = {"page": 0, "section": 1, "paragraph": 2}


def contains(superset: LineSpan | tuple[str, dict], subset) -> bool:
    """Document-level containment for citation locators: within the same
    document's locator ordering, a page covers the sections/paragraphs on
    it; a section covers the paragraphs in it. Cross-kind containment
    follows that page > section > paragraph ordering."""
    if isinstance(superset, LineSpan):
        if isinstance(subset, LineSpan):
            return superset.contains(subset)
        raise LocatorError("line span vs citation: different locator kinds")
    if isinstance(superset, tuple):
        sup_kind, sup_val = superset
    else:
        sup_kind, sup_val = superset.kind, superset.value
    sub_kind, sub_val = subset.kind, subset.value
    if _CITATION_ORDER[sup_kind] > _CITATION_ORDER[sub_kind]:
        return False
    if sup_kind == sub_kind:
        return sup_val == sub_val
    return True


@dataclass(frozen=True)
class Record:
    """The three record fields (the runbook's): the state, the pass date
    (ISO YYYY-MM-DD), and the covered locators."""

    status: str
    proofing_date: str
    covered: tuple[str, ...] = field(default=())

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise LocatorError(
                f"status {self.status!r} outside the four-status vocabulary"
            )
        if not _valid_year(self.proofing_date):
            raise LocatorError(f"proofing date {self.proofing_date!r}: not ISO YYYY-MM-DD")
        for loc in self.covered:
            _validate_text(loc)


def _validate_text(locator: str) -> None:
    text = locator.strip()
    if _SPAN_RE.fullmatch(text):
        LineSpan.parse(text)
        return
    if re.fullmatch(r"\d+", text):
        LineSpan(int(text), int(text))
        return
    Citation.parse(locator)


@dataclass
class Coverage:
    """Coverage-interval tracking with the OCR-7 extension rule: a record's
    covered locator set equals the pass's covered list; sourcing an
    uncovered locator requires the record extended first."""

    covered: list[str] = field(default_factory=list)

    @classmethod
    def from_pass(cls, covered: Iterable[str]) -> "Coverage":
        covered = list(covered)
        for loc in covered:
            _validate_text(loc)
        return cls(covered)

    def covers(self, locator: str) -> bool:
        _validate_text(locator)
        if locator in self.covered:
            return True
        text = locator.strip()
        if _SPAN_RE.fullmatch(text) or re.fullmatch(r"\d+", text):
            want = LineSpan.parse(text) if "-" in text else LineSpan(int(text), int(text))
            for have in self.covered:
                if _SPAN_RE.fullmatch(have.strip()):
                    if LineSpan.parse(have).contains(want):
                        return True
        return False

    def extend(self, covered: Iterable[str]) -> None:
        """The OCR-7 extension rule: appending the new pass's covered list
        extends the record; an uncovered locator is sourced only after this."""
        added = list(covered)
        for loc in added:
            _validate_text(loc)
        self.covered.extend(added)


def parse_date(iso: str) -> date_type:
    if not _valid_year(iso):
        raise LocatorError(f"{iso!r}: not ISO YYYY-MM-DD")
    y, m, d = (int(x) for x in iso.split("-"))
    return date_type(y, m, d)