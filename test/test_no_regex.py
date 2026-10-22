# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""No-regex static guard over the conversion layer.

SC-L8 (snea-lib#2): ``import re`` is prohibited in the conversion layer —
the research cards' standing convention (table-driven conversion, never
regex; parent R-14). The guard walks the conversion-layer modules (the
``snea_lib/derivation`` package's own modules plus the ``bl_ipa`` home) and
asserts none imports ``re``. The discovered set must be non-empty, so the
guard stays real rather than walking an absent tree.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "snea_lib"


def conversion_layer_files() -> list[Path]:
    py_files = sorted((SRC / "derivation").glob("*.py"))
    py_files += sorted(SRC.glob("bl_ipa.py"))
    return [p for p in py_files if p.name != "__init__.py"]


def test_conversion_layer_present() -> None:
    files_found = conversion_layer_files()
    assert files_found, "conversion-layer module set is empty"


def test_no_regex_imports() -> None:
    files_found = conversion_layer_files()
    offenders: list[str] = []
    for path in files_found:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
                if "re" in names:
                    offenders.append(f"{path.name}: import re")
            elif isinstance(node, ast.ImportFrom) and node.module == "re":
                offenders.append(f"{path.name}: from re import ...")
    assert not offenders, f"re import in the conversion layer: {offenders}"