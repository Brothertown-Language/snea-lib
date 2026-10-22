# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Rule-data package of record: resolves, loads, and stays .md-free.

SC-L1 (snea-lib#2): the rule-data package resolves and loads —
``snea_lib.derivation.rules`` imports, every ``rules/*.yaml`` parses, and
the ``.md`` source layer is absent from the package (the paper's ``.md``
twin is stale and excluded by construction — parent #134 §2).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from importlib.resources import files

import yaml

import snea_lib.derivation.rules as rules_pkg


def test_rules_package_imports() -> None:
    assert rules_pkg.__name__ == "snea_lib.derivation.rules"


def test_load_rules_returns_parsed_tables() -> None:
    rules = rules_pkg.load_rules()
    # the eight data files of record, each parseable through the loader
    for name in (
        "forward_tables",
        "forward_laws",
        "brothertown_laws",
        "law10_triggers",
        "analogical_exceptions",
        "b5_recommendations",
        "reversed_rules",
        "bl_rendering",
    ):
        assert name in rules, f"missing rule-data table: {name}"
        assert isinstance(rules[name], dict), f"{name} did not parse to a mapping"


def test_every_rules_yaml_parses() -> None:
    root = files("snea_lib.derivation.rules")
    yaml_names = [p.name for p in root.iterdir() if p.name.endswith(".yaml")]
    assert yaml_names, "no rule-data YAML files present"
    for name in yaml_names:
        data = yaml.safe_load((root / name).read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"{name} did not parse to a mapping"


def test_md_layer_absent() -> None:
    root = files("snea_lib.derivation.rules")
    md_names = [p.name for p in root.iterdir() if p.name.endswith((".md", ".markdown"))]
    assert not md_names, f".md source-layer files in the package: {md_names}"


def test_structural_smoke() -> None:
    rules = rules_pkg.load_rules()
    tables = rules["forward_tables"]
    # forward tables carry the correspondence rows and the daughter columns
    consonant_rows = tables["table1_consonants"]["rows"]
    assert len(consonant_rows) >= 26, f"table 1 unexpectedly small: {len(consonant_rows)}"
    for col in ("Ms", "Nr", "Mp", "WP"):
        assert col in tables["table1_consonants"]["columns"]
    assert "table2_vowels" in tables and "table3_word_final" in tables
    # forward laws: the recorded law set with engine keys
    laws = rules["forward_laws"]["laws"]
    assert len(laws) >= 25, f"forward-law set unexpectedly small: {len(laws)}"
    # brothertown: B1-B7 + ladder + weights
    bt = rules["brothertown_laws"]
    assert set(bt["candidate_laws"]) >= {"B1", "B2", "B3", "B4", "B5", "B6", "B7"}
    assert len(bt["tie_breaker_ladder"]) == 4
    # reversed rules: the four daughter columns
    rr = rules["reversed_rules"]["reversed_rules"]
    assert set(rr) >= {"Ms", "Nr", "Mp", "WP"}