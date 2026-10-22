# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""bl_ipa migration parity (snea-lib#2, SC-L7 — library-side vector).

The migrated ``snea_lib.bl_ipa`` is the single home of the BL
orthography/IPA machinery, migrated behavior-unchanged from the parent
record's ``src/bl_ipa.py``. This repo's frozen vector asserts the migrated
module reproduces the parent module's captured outputs verbatim over the
Costa-letter word set (the lexicon's ``bl`` fields + the primer lesson
table's ``bl_letters`` values). The SC-L7 parity-run capture in the
consumer PR remains the consumer spec's instrument.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from pathlib import Path

import pytest
import yaml

import snea_lib.bl_ipa as migrated


@pytest.fixture()
def parity_words() -> list[dict]:
    path = Path(__file__).resolve().parent / "bl_ipa_parity_words.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data["words"]


def test_migration_home_imports() -> None:
    assert migrated.__name__ == "snea_lib.bl_ipa"
    for fn in ("segment", "to_ipa_unmarked", "mark_word", "mark_stress", "validate_ipa", "to_ipa"):
        assert hasattr(migrated, fn), f"the migration surface lost {fn}"


def test_word_parity(parity_words: list[dict]) -> None:
    assert parity_words, "the parity word set is empty"
    failures = []
    for w in parity_words:
        got = migrated.to_ipa(w["word"])
        if got != w["expected_ipa"]:
            failures.append(f"{w['word']!r}: {got!r} != captured {w['expected_ipa']!r}")
    assert not failures, "parity failures:\n" + "\n".join(failures)


def test_reduced_faces_match_mark_word(parity_words: list[dict]) -> None:
    # the unmarked and stress-marked faces compose exactly as the parent's
    # to_ipa = mark_stress(to_ipa_unmarked(...)) contract records
    for w in parity_words:
        assert migrated.mark_stress(migrated.to_ipa_unmarked(w["word"])) == migrated.to_ipa(
            w["word"]
        )