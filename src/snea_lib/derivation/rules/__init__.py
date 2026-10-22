# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Rule-data package of record (snea_lib.derivation.rules).

The versioned rule data ships as package data; the loader reads every
``rules/*.yaml`` through ``importlib.resources`` and returns the parsed
tables keyed by file stem. The ``.md`` source layer is excluded by
construction (the paper's ``.md`` twin is stale — parent record #134 §2).

Rule-data sources (all parent-tracked record material, extracted with
cites back to their record paths):
- ``forward_tables`` — the paper's Tables 1-3 correspondence cells
- ``forward_laws`` — the verified forward laws (Laws 1-26)
- ``brothertown_laws`` — candidate laws B1-B7, tie-breaker ladder, weights
- ``law10_triggers`` — the attested Law-10 trigger list
- ``analogical_exceptions`` — the †-class exception data
- ``b5_recommendations`` — recorded B5 applications (pending ratification)
- ``reversed_rules`` — per-daughter inverses, source registry, reconciliation
- ``bl_rendering`` — phoneme-to-letter map and recorded special renderings

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

from importlib.resources import files
from typing import Any

import yaml

__all__ = ["load_rules"]

_TABLE_NAMES: tuple[str, ...] = (
    "forward_tables",
    "forward_laws",
    "brothertown_laws",
    "law10_triggers",
    "analogical_exceptions",
    "b5_recommendations",
    "reversed_rules",
    "bl_rendering",
)


def load_rules() -> dict[str, dict[str, Any]]:
    """Load every ``rules/*.yaml`` as package data; return stem → parsed
    mapping. Unknown files in the package are ignored (only the recorded
    tables load); a recorded table that fails to parse raises.
    """
    root = files("snea_lib.derivation.rules")
    tables: dict[str, dict[str, Any]] = {}
    for name in _TABLE_NAMES:
        path = root / f"{name}.yaml"
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise TypeError(f"rule data {name}.yaml did not parse to a mapping")
        tables[name] = parsed
    return tables