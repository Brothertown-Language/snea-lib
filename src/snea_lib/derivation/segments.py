# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Token-based segment representation for the derivation chain (snea-lib#2,
R-L2).

Segments are tokens over a per-stage phoneme inventory (the paper's
Tables 1-2 notation; the record's §Notation): ``Seg`` carries the phoneme
glyph in its stage notation, the PSNEA palatal flag (serialized as plain
``t`` in PSNEA strings per the record's worked-form convention, as ``c`` in
BL faces), and the morphological component tag the composition's parse
supplies (R-L5: the parse the position-sensitive laws consume). String
conversion is a table-driven longest-match tokenizer over the stage's
inventory — no regex anywhere (SC-L8; parent R-14).

Stage notations:
- PA: ``p t č k s š θ l r m n w y h ʔ``; clusters ``ʔθ ʔl hθ hl nθ θk xk ʔk
  ht ʔt hč ʔč hs ʔs nl šk θkw hp xp nt nk``; vowels ``a e i o`` with ``·``
  as the length mark (``i·`` tokenize to the single long-vowel token).
- PEA/PSNEA: ``p t k s m n w y r h``; the palatal single ``tʲ``; clusters
  ``hš hs hč hk ht hp hx hr xkw šk nt nk``; vowels ``a ǝ ē ī ō ā``.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

from dataclasses import dataclass

BOUNDARY = "-"
LENGTH_MARK = "·"

# --- PA stage notation -------------------------------------------------------
PA_CLUSTERS: tuple[str, ...] = (
    "θkw", "ʔθ", "ʔl", "hθ", "hl", "nθ", "θk", "xk", "ʔk",
    "ht", "ʔt", "hč", "ʔč", "hs", "ʔs", "nl", "šk", "hp", "xp", "nt", "nk",
)
PA_SINGLES: frozenset[str] = frozenset("ptčksšθlrmnwyhʔH")
PA_VOWELS: frozenset[str] = frozenset("aeio")

# --- PEA/PSNEA stage notation (the EA inventories; tʲ the palatal single) -----
EA_CLUSTERS: tuple[str, ...] = (
    "hš", "hs", "hč", "hk", "ht", "hp", "hx", "hr", "xkw", "šk", "nt", "nk",
)
EA_SINGLES: frozenset[str] = frozenset("ptksmnwyrh")
EA_VOWELS: frozenset[str] = frozenset("aǝēīōā")

RESONENTS: frozenset[str] = frozenset("mnlrwy")
FRICATIVE_HEADS: frozenset[str] = frozenset("sšh")


@dataclass(frozen=True)
class Seg:
    """One segment token: the phoneme in its stage notation.

    ``palatal`` marks a PSNEA palatalized *k (Law 10): serialized as plain
    ``t`` in PSNEA strings per the record's worked-form convention, as ``c``
    in BL faces. ``component`` carries the parse tag (R-L5): one of
    ``initial|medial|final|inflection`` or empty for an untagged segment.
    """

    sym: str
    palatal: bool = False
    component: str = ""


def _tokenize_text(text: str, clusters: tuple[str, ...], singles: frozenset[str], vowels: frozenset[str]) -> list[Seg]:
    """Longest-match tokenization of one stage's notation (no regex)."""
    segs: list[Seg] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == BOUNDARY:
            segs.append(Seg(BOUNDARY))
            i += 1
            continue
        if ch == LENGTH_MARK:
            if not segs:
                raise ValueError(f"'·' with no preceding vowel at {text[:i]!r} ({text!r})")
            if segs[-1].sym not in vowels:
                raise ValueError(f"'·' after non-vowel {segs[-1].sym!r} ({text!r})")
            segs[-1] = Seg(segs[-1].sym + LENGTH_MARK, segs[-1].palatal, segs[-1].component)
            i += 1
            continue
        matched = False
        for length in (3, 2):
            if i + length <= n and text[i : i + length] in clusters:
                segs.append(Seg(text[i : i + length]))
                i += length
                matched = True
                break
        if not matched and (ch in singles or ch in vowels):
            segs.append(Seg(ch))
            i += 1
            matched = True
        if not matched:
            raise ValueError(f"segment {ch!r} is not in the stage notation ({text!r})")
    return segs


def tokenize_pa(text: str) -> list[Seg]:
    """Tokenize a PA-stage starred form (the leading star is notation, not a
    segment)."""
    return _tokenize_text(
        text.removeprefix("*"), PA_CLUSTERS, PA_SINGLES, PA_VOWELS
    )


def tokenize_ea(text: str) -> list[Seg]:
    """Tokenize a PEA/PSNEA-stage starred form (``tʲ`` the palatal single)."""
    return _tokenize_text(text.removeprefix("*"), ("tʲ",) + EA_CLUSTERS, EA_SINGLES, EA_VOWELS)


def serialize(segs: list[Seg], stage: str) -> str:
    """Serialize segments to the stage's starred record string."""
    out: list[str] = []
    for seg in segs:
        if seg.sym == BOUNDARY:
            out.append(BOUNDARY)
        elif seg.palatal:
            out.append("c" if stage == "BL" else "t")
        else:
            out.append(seg.sym)
    prefix = "**" if stage == "BL" else "*"
    return prefix + "".join(out)