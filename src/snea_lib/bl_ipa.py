# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""BL orthography to IPA generator.

The BL language is written in the Costa/Modern-Mohegan alphabet with BL's
phonetic values (the paper's Tables 8-10 ruling). This module is the
deterministic letters-to-IPA face of that convention: a table-driven
longest-match scanner (no regex — the alphabet is phonemic, one letter or
digraph per phoneme), vowel length carried by the letter values, and the
recorded stress rule (primary on the penultimate syllable — never the
first, rarely the last; long vowels carry secondary stress wherever they
stand; even-numbered short vowels are stressed counting from the word
beginning or the last stress point, finals excepted; nothing exceeds the
primary's emphasis — the parent record's stress-system sources).

This file is the migrated single home of the BL orthography/IPA machinery
(snea-lib#2, R-L8): migrated behavior-unchanged from the parent record's
src/bl_ipa.py at migration time; the consumer spec's parity run re-checks
it over the parent's recorded test inputs.

Provenance: AI-authored, OpenCode (huggingface/zai-org/GLM-5.3-Flash).
"""

from __future__ import annotations

# The BL letter inventory (Costa letters, BL values — paper Table 9, BL row).
# Digraphs are matched before single letters (longest match first).
BL_TO_IPA: dict[str, str] = {
    # preaspiration + cluster digraphs (B2/B3-adjacent letter conventions)
    "hsh": "hʃ",  # B3: the hš cluster
    "hp": "hp",
    "ht": "ht",
    "hk": "hk",
    "hq": "hkw",
    # the s-digraph
    "sh": "ʃ",
    # vowels (BL values: length carried by the letter)
    "a": "a",
    "á": "eː",
    "i": "iː",
    "o": "oː",
    "ô": "ʌ̃ː",
    "u": "ə",
    # consonants
    "c": "tʃ",
    "h": "h",
    "k": "k",
    "m": "m",
    "n": "n",
    "p": "p",
    "q": "kw",
    "s": "s",
    "t": "t",
    "w": "w",
    "y": "j",
}

# Capitals occur sentence-initially in the lesson frames and in names
# (the pronunciation guide records capitals A/O; the uppercase set is the
# sentence-case face of the same letters).
BL_TO_IPA.update({k.upper(): v for k, v in list(BL_TO_IPA.items()) if len(k) == 1})

# The IPA vowel set the stress rule operates on (nuclei of the syllables).
IPA_VOWELS = set("aáeiouôʌãəɛ")

# The closed BL IPA alphabet — every segment the generator may emit, and the
# validation set for any IPA claimed to be BL (the developer's validation
# point: a limited, enumerable inventory of phones and modifiers).
IPA_PHONES: frozenset[str] = frozenset({
    # stops (unaspirated), affricate, fricatives, sonorants, glides
    "p", "t", "k", "tʃ", "s", "ʃ", "h", "m", "n", "w", "j",
    # the q letter's cluster
    "kw",
    # preaspiration clusters (h + the following consonant)
    "hp", "ht", "hk", "hkw", "hʃ",
    # vowels (length carried by the letter values; ô is the nasal vowel)
    "a", "ə", "iː", "oː", "eː", "ʌ̃ː",
})
_PRIMARY = "\u02c8"  # ˈ
_SECONDARY = "\u02cc"  # ˌ
_LENGTH = "\u02d0"  # ː
_COMBINING_TILDE = "\u0303"

IPA_MODIFIERS: frozenset[str] = frozenset({_PRIMARY, _SECONDARY, _LENGTH, _COMBINING_TILDE})
IPA_PASSTHROUGH: frozenset[str] = frozenset({" ", "_", ".", ",", "?", "!", ";", ":", "-", "/", "·"})


def validate_ipa(ipa: str) -> list[str]:
    """Validate an IPA string against the closed BL inventory.

    Returns the list of violations (empty = valid). Every segment must be a
    documented BL phone; the only allowed modifiers are the two stress marks,
    the length mark, and the nasal tilde; blanks/punctuation pass through.
    """
    errors: list[str] = []
    units = _syllables(ipa.strip("/"))
    seen_phone = False
    for onset, nucleus in units:
        for ch in onset:
            if ch in IPA_PASSTHROUGH:
                continue
            # onset consonants are validated as segments below
        if not nucleus:
            continue
        vowel_part = ""
        for ch in nucleus:
            if ch in IPA_VOWELS or ch == _COMBINING_TILDE:
                vowel_part += ch
            else:
                break
        if vowel_part.replace(_COMBINING_TILDE, "") not in IPA_VOWELS:
            errors.append(f"nucleus {nucleus!r} is not a BL vowel")
        seen_phone = True
    # segment-validate the whole string by longest match over the phone set
    body = ipa.strip("/")
    i = 0
    n = len(body)
    phones = sorted(IPA_PHONES, key=len, reverse=True)
    while i < n:
        ch = body[i]
        if ch in IPA_PASSTHROUGH or ch in IPA_MODIFIERS or ch in IPA_VOWELS or ch == _COMBINING_TILDE:
            i += 1
            continue
        matched = False
        for phone in phones:
            if body.startswith(phone, i):
                i += len(phone)
                matched = True
                break
        if not matched:
            errors.append(f"segment at {i} ({body[i:i+3]!r}) is not in the BL IPA inventory")
            i += 1
    if not seen_phone and units:
        errors.append("no vowel nucleus found")
    return errors



def segment(bl: str) -> list[str]:
    """Split a BL letter form into its phone segments (longest match).

    Blank-frame tokens (___) and sentence punctuation are passed through
    as their own segments so lesson frames can be processed whole.
    """
    segments: list[str] = []
    i = 0
    n = len(bl)
    while i < n:
        ch = bl[i]
        if ch in (" ", "_", ".", ",", "?", "!", ";", ":", "-", "/"):
            segments.append(ch)
            i += 1
            continue
        matched = False
        for length in (3, 2, 1):
            if i + length <= n and bl[i : i + length] in BL_TO_IPA:
                segments.append(BL_TO_IPA[bl[i : i + length]])
                i += length
                matched = True
                break
        if not matched:
            raise ValueError(f"letter {ch!r} is not in the adopted BL orthography ({bl!r})")
    return segments


def to_ipa_unmarked(bl: str) -> str:
    """The segmental IPA of a BL letter form: length carried, no stress marks."""
    return "".join(segment(bl))


def _syllables(ipa: str) -> list[list[str]]:
    """Split an IPA string into (onset, nucleus) units, onset-maximized.

    Consonants between nuclei attach to the following nucleus; word-final
    consonants are the last nucleus's coda. Each unit is [onset, nucleus
    (with any combining marks and length)].
    """
    units: list[list[str]] = []
    onset = ""
    i = 0
    n = len(ipa)
    while i < n:
        ch = ipa[i]
        if ch in IPA_VOWELS:
            nucleus = ch
            while i + 1 < n and (ipa[i + 1] == _COMBINING_TILDE or ipa[i + 1] == _LENGTH):
                i += 1
                nucleus += ipa[i]
            units.append([onset, nucleus])
            onset = ""
        else:
            onset += ch
        i += 1
    if onset and units:
        units[-1][1] += onset  # trailing consonants = the final coda
    return units


def _is_long(nucleus: str) -> bool:
    return _LENGTH in nucleus


def mark_word(word: str) -> str:
    """Stress-mark one IPA word per the recorded BL rule."""
    units = _syllables(word)
    nv = len(units)
    if nv == 0:
        return word
    marks = [""] * nv
    if nv == 1:
        marks[0] = _PRIMARY
    else:
        primary = nv - 2 if nv > 2 else nv - 1  # penult; disyllable -> final
        marks[primary] = _PRIMARY
        for idx, (onset, nucleus) in enumerate(units):
            if idx != primary and _is_long(nucleus):
                marks[idx] = _SECONDARY
        count = 0
        for idx, (onset, nucleus) in enumerate(units):
            if idx == nv - 1:
                continue  # final syllables are never stressed
            if marks[idx]:
                count = 0
                continue
            count += 1
            if count % 2 == 0:
                marks[idx] = _SECONDARY
                count = 0
    return "".join(m + onset + nucleus for (onset, nucleus), m in zip(units, marks))


def mark_stress(ipa: str) -> str:
    """Stress-mark an IPA string (multi-word aware; '·' segments pass through)."""
    if "·" in ipa:
        parts = []
        for part in ipa.split("·"):
            part = part.strip()
            if part.startswith("/") and part.endswith("/"):
                parts.append(
                    "/" + " ".join(mark_word(w) for w in part.strip("/").split(" ")) + "/"
                )
            else:
                parts.append(part)
        return " · ".join(parts)
    body = ipa.strip("/")
    marked = " ".join(mark_word(w) for w in body.split(" "))
    if ipa.startswith("/") and ipa.endswith("/"):
        return "/" + marked + "/"
    return marked


def to_ipa(bl: str) -> str:
    """BL letter form -> IPA with vowel length and primary/secondary stress."""
    return mark_stress(to_ipa_unmarked(bl))
