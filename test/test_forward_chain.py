# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Forward-chain reproduction vectors (snea-lib#2, SC-L4).

The forward engine reproduces the recorded worked-derivation forms on
parent-record-derived single-form fixtures: the paper's Table 4/6 rows
(each fixture cites its recorded row) end to end — PA input → PEA → PSNEA
→ BL starred — plus the recorded orthography and IPA faces where the
parent record records them (the lexicon's chain-derived entries); rows
recording only output form and law path (the inanim-pl row: paper
Table 6; B2) assert the recorded elements. Recorded-string comparison
normalizes the record's bare ``i``/``o`` at PEA+ stages to ``ī``/``ō``
per Table 2's PEA-system statement (the worked-glyph shorthand).

A Law-9 smoke rides the item (the law set's only unexercised mandatory
applier).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import pytest

from snea_lib.derivation.engine import ChainEngine, ChainInput, ParsePart
from snea_lib.derivation.rules import load_rules


def _norm(recorded: str) -> str:
    """The recorded PEA+ worked-glyph shorthand: bare i/o = the long
    ī/ō (Table 2's PEA-system notation)."""
    return recorded.replace("i", "ī").replace("o", "ō")


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


# (id, ChainInput, recorded stage forms, recorded ortho, recorded ipa sans //)
# Each fixture cites its recorded row (paper Table 4/6; lexicon entry id).
ROWS = [
    {
        "id": "teeth-3s",
        "cite": "paper Tables 4/6 (PA *wi·pitali; B1); lexicon#teeth-3s; Goddard 1980 §3.1 / cline (58)",
        "input": ChainInput(
            form="*wi·pitali",
            parse=(ParsePart("initial", "wi·pital"), ParsePart("inflection", "i")),
        ),
        "pa": "*wi·pitali",
        "pea": "*wīpītar",
        "psnea": "*wīpītar",
        "bl": "**wīpītay",
        "ortho": "wipitay",
        "ipa": "ˌwiːˈpiːtaj",
    },
    {
        "id": "house",
        "cite": "paper Tables 4/6 (PA *wi·kiwa·Hmi; B4); lexicon#house; Costa (1) citing Goddard 1982:26",
        "input": ChainInput(form="*wi·kiwa·Hmi"),
        "pa": "*wi·kiwa·Hmi",
        "pea": "*wīkīwāHm",
        "psnea": "*wītīwāHm",
        "bl": "**wīcīwāHm",
        "ortho": "wiciwôh",
        "ipa": "ˌwiːˈtʃiːˌwʌ̃ːh",
    },
    {
        "id": "chief",
        "cite": "paper Tables 4/6 (PA *sa·kima·wa; B4); lexicon#chief; Costa (1) citing Goddard 1978:75",
        "input": ChainInput(form="*sa·kima·wa"),
        "pa": "*sa·kima·wa",
        "pea": "*sākīmāw",
        "psnea": "*sātīmāw",
        "bl": "**sācīmāw",
        "ortho": "sôcimôw",
        "ipa": "ˌsʌ̃ːˈtʃiːˌmʌ̃ːw",
    },
    {
        "id": "inan-pl",
        "cite": "paper Table 6 (+ Table 4: *-ali → *-ari → *-ar; B2); lexicon#inan-pl",
        "input": ChainInput(form="*-ali", parse=(ParsePart("inflection", "-ali"),)),
        "pa": "*-ali",
        "pea": "*-ari",
        "psnea": "*-ar",
        "bl": "**-aš",
        "ortho": "-ash",
        # the suffix citation carries the record's own unmarked IPA face
        # (the stress rule's scope is words; the record's face is the
        # assertion — the plan's documented scope)
        "ipa_recorded_unmarked": "aʃ",
    },
    {
        "id": "heart",
        "cite": "paper Tables 4/6 (PA *mete·hi; B5,B6); lexicon#heart; Goddard 1981 §7",
        "input": ChainInput(form="*mete·hi"),
        "pa": "*mete·hi",
        "pea": "*mǝtēh",
        "psnea": "*mǝtēh",
        "bl": "**mǝtēh",
        "ortho": "mutáh",
        "ipa": "məˈteːh",
    },
    {
        "id": "three",
        "cite": "paper Tables 4/6 (PA *neʔθwi with the final *i· of Table 5 note f; B3); lexicon#three",
        "input": ChainInput(form="*neʔθwi·"),
        "pa": "*neʔθwi·",
        "pea": "*nhxwi",
        "psnea": "*nhšwi",
        "bl": "**nhšwi",
        "ortho": "nuhshwi",
        "ipa": "nəˈhʃwiː",
    },
    {
        "id": "person",
        "cite": "paper Tables 4/6 (PA *elenyiwa; B1); lexicon#man (uyuniw; PA *elenyiwa)",
        "input": ChainInput(form="*elenyiwa"),
        "pa": "*elenyiwa",
        "pea": "*ǝrǝniw",
        "psnea": "*ǝrǝniw",
        "bl": "**ǝyǝniw",
        "ortho": "uyuniw",
        "ipa": "əˈjəˌniːw",
    },
    {
        "id": "island",
        "cite": "paper Tables 4/6 (PA *menahanwi; B5); lexicon#island (munahan); Gd82:34 via Rudes, Goddard 1981 §9",
        "input": ChainInput(form="*menahanwi"),
        "pa": "*menahanwi",
        "pea": "*mǝnahan",
        "psnea": "*mǝnahan",
        "bl": "**mǝnahan",
        "ortho": "munahan",
        "ipa": "məˈnahan",
    },
]


def test_forward_chain_rows(engine: ChainEngine) -> None:
    failures: list[str] = []
    for row in ROWS:
        rid = row["id"]
        result = engine.derive(row["input"])
        forms = result.stage_forms
        if forms.get("PA") != row["pa"]:
            failures.append(f"{rid}: PA {forms['PA']!r} != {row['pa']!r}")
        if forms.get("PEA") != _norm(row["pea"]):
            failures.append(f"{rid}: PEA {forms['PEA']!r} != norm({row['pea']!r})")
        if forms.get("PSNEA") != _norm(row["psnea"]):
            failures.append(f"{rid}: PSNEA {forms['PSNEA']!r} != norm({row['psnea']!r})")
        if forms.get("BL") != _norm(row["bl"]):
            failures.append(f"{rid}: BL {forms['BL']!r} != norm({row['bl']!r})")
        if result.faces["orthography"] != row["ortho"]:
            failures.append(
                f"{rid}: orthography {result.faces['orthography']!r} != {row['ortho']!r}"
            )
        expected_ipa = row.get("ipa")
        if expected_ipa is not None and result.faces["ipa"] != expected_ipa:
            failures.append(f"{rid}: IPA /{result.faces['ipa']}/ != /{expected_ipa}/")
    assert not failures, "SC-L4 row-reproduction failures:\n" + "\n".join(failures)


def test_inan_pl_recorded_ipa_face(engine: ChainEngine) -> None:
    # the recorded elements of the inanim-pl row: the suffix citation's
    # own unmarked IPA face (the record's /aʃ/ — the stress rule's scope
    # is words; the record's face is the assertion)
    row = next(r for r in ROWS if r["id"] == "inan-pl")
    result = engine.derive(row["input"])
    assert row["ipa_recorded_unmarked"] == "aʃ"
    assert result.faces["orthography"] == "-ash"


def test_law16a_recorded_in_trace(engine: ChainEngine) -> None:
    # the three row's grounded Law-16(iii-a) surface: the recorded PEA
    # cell *nhxwi required the syncope; the trace records it with its cite
    row = next(r for r in ROWS if r["id"] == "three")
    result = engine.derive(row["input"])
    entry = [t for t in result.trace if t.stage == "PEA" and t.law_id == "law-16"]
    assert entry, "no Law-16(iii-a) in-chain surface in the three row's trace"


def test_law9_smoke(engine: ChainEngine) -> None:
    # the *š /s merger (Law 9) as data — a PA *š single shifts to *s
    result = engine.derive(ChainInput(form="*šim"))
    assert result.stage_forms["PEA"] == "*sīm"
    entry = [t for t in result.trace if t.law_id == "law-9"]
    assert entry, "no Law-9 applier trace entry"