# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The review-record core over both anchor families.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from .model import LocatorError


@dataclass(frozen=True)
class TextAnchor:
    """A text-anchored subject: a locator (the model's locator space)."""

    locator: str


@dataclass(frozen=True)
class Region:
    """A rectangle or polygon on a page image (kraken geometry is
    polygon-shaped; the component carries both). Coordinates are relative
    (0.0-1.0) unless the consumer's geometry contract says otherwise."""

    points: tuple[tuple[float, float], ...]

    def __post_init__(self) -> None:
        if len(self.points) not in (2, 3, 4):
            raise LocatorError(
                "region: a rectangle (4 corners) or a polygon (3+ points) — give points "
                f"as (x, y) pairs; got {len(self.points)}"
            )


@dataclass(frozen=True)
class ImageAnchor:
    """An image-anchored subject: a page image plus a region."""

    page: str
    region: Region


@dataclass
class ReviewRecord:
    """One review-record shape over both anchor families: the subject, a
    state from a per-consumer injected closed vocabulary, the pass date, and
    the evidence reference."""

    subject: TextAnchor | ImageAnchor
    state: str
    pass_date: str
    evidence: str


class RegisterWriter(Protocol):
    """The injected register-writer contract: verdicts go through this and
    nowhere else; the library holds no store schema and no file format."""

    def write(self, record: ReviewRecord) -> Any: ...


def make_vocabulary(*tokens: str) -> frozenset[str]:
    """A consumer's injected closed vocabulary."""
    return frozenset(tokens)


def verdict(
    writer: RegisterWriter,
    vocabulary: frozenset[str],
    subject: TextAnchor | ImageAnchor,
    state: str,
    pass_date: str,
    evidence: str,
) -> ReviewRecord:
    """Build and dispatch a verdict through the injected writer, rejecting
    any state outside the injected vocabulary."""
    if state not in vocabulary:
        raise LocatorError(
            f"state {state!r} outside the injected vocabulary {sorted(vocabulary)}"
        )
    _anchor_ok(subject)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", pass_date):
        raise LocatorError(f"pass date {pass_date!r}: not ISO YYYY-MM-DD")
    record = ReviewRecord(subject=subject, state=state, pass_date=pass_date,
                          evidence=evidence)
    writer.write(record)
    return record


def _anchor_ok(subject: TextAnchor | ImageAnchor) -> None:
    if isinstance(subject, TextAnchor):
        from .model import _validate_text

        _validate_text(subject.locator)
    elif isinstance(subject, ImageAnchor):
        _ = subject.page, subject.region
        if not re.search(r"\.(png|jpg|jpeg|tif|tiff)$", subject.page, re.I):
            raise LocatorError(f"page image {subject.page!r}: not a page-image path")
    else:
        raise LocatorError("subject: not a text anchor nor an image anchor")


class InMemoryRegister:
    """An in-memory writer for tests and consumers without a store yet."""

    def __init__(self) -> None:
        self.records: list[ReviewRecord] = []

    def write(self, record: ReviewRecord) -> Any:
        self.records.append(record)
        return record


def writer_adapter(fn: Callable[[ReviewRecord], Any]) -> RegisterWriter:
    """Adapt any callable taking the record to the register-writer contract."""

    class _W:
        def write(self, record: ReviewRecord) -> Any:
            return fn(record)

    return _W()