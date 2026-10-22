# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The BL three-face renderer (snea-lib#2 item 8, R-L8).

The BL face production: the starred phonemic face (the B-stage's serialized
form, the paper's Table 6 convention), the Costa-orthography face (the
phoneme-to-letter map over ``rules/bl_rendering.yaml``, including the
recorded final ``*-Hm → ⟨-ôh⟩`` rendering and the orthographic-schwa
epenthesis), and the IPA face (the migrated ``snea_lib.bl_ipa.to_ipa`` over
the orthography). Renderer conservatism: a BL phoneme without a letter
mapping stops face production with an unmapped-segment error naming the
segment and the starred face — never an invented letter.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

from dataclasses import dataclass

from snea_lib import bl_ipa
from snea_lib.derivation.segments import BOUNDARY, Seg, serialize

# the h-initial clusters the orthographic-schwa epenthesis writes at
# (the recorded junction class: the three row's +hsh)
_H_CLUSTERS: frozenset[str] = frozenset({"hš", "hs", "hč", "hk", "ht", "hp"})

# the single consonants the epenthesis's recorded trigger reads on
_SINGLE_CONS: frozenset[str] = frozenset("ptksšhmnwy")


@dataclass(frozen=True)
class BLFaces:
    """The three BL faces (R-L8): starred phonemic form, Costa orthography,
    IPA."""

    starred: str
    orthography: str
    ipa: str


def faces(segs: list[Seg], render_table: dict) -> BLFaces:
    """The three faces for the BL leg's (already B-applied) segments."""
    starred = serialize(segs, "BL")
    orthography = _orthography_face(segs, render_table)
    return BLFaces(starred=starred, orthography=orthography, ipa=bl_ipa.to_ipa(orthography))


def _orthography_face(segs: list[Seg], render_table: dict) -> str:
    letter_map: dict[str, str] = render_table["phoneme_to_letter"]
    specials = render_table.get("special_renderings", {})
    material = [s for s in segs if s.sym != BOUNDARY]
    # the recorded final *-Hm rendering: the m dissolves (the recorder's
    # nasal mark — its nasal quality carried by the nasal-letter face); the
    # H renders its letter (h)
    dissolve_final_m = (
        "final-Hm" in specials
        and len(material) >= 2
        and material[-1].sym == "m"
        and material[-2].sym == "H"
    )
    letters: list[str | None] = []
    for i, seg in enumerate(segs):
        if seg.sym == BOUNDARY:
            letters.append(BOUNDARY)
            continue
        if dissolve_final_m and material and seg is material[-1]:
            letters.append(None)
            continue
        key = "tʲ" if seg.palatal else seg.sym
        letter = letter_map.get(key)
        if letter is None:
            raise ValueError(
                f"unmapped BL phoneme {seg.sym!r} (palatal={seg.palatal}) in "
                f"the starred BL face {serialize(segs, 'BL')!r} — no invented letter"
            )
        letters.append(letter)
    return _apply_epenthesis(letters, segs, render_table)


def _apply_epenthesis(letters: list[str | None], segs: list[Seg], render_table: dict) -> str:
    """The orthographic-schwa epenthesis (the recorded rule): a consonant
    directly followed by an h-initial cluster (no vowel between) writes the
    schwa letter at the junction — grounded: the three row's recorded
    orthography ``nuhshwi`` from ``**nhšwi``."""
    ep = render_table.get("orthographic_epenthesis")
    out: list[str] = []
    for i, seg in enumerate(segs):
        li = letters[i]
        letter = li if li is not None else ""
        out.append(letter)
        nxt = segs[i + 1] if i + 1 < len(segs) else None
        if (
            ep
            and letter
            and seg.sym in _SINGLE_CONS
            and nxt is not None
            and nxt.sym in _H_CLUSTERS
        ):
            out.append(str(ep["letter"]))
    return "".join(out)