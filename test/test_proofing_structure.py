# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""SC-8/SC-11: self-containment — the machinery's import graph holds only
stdlib + machinery-package + pyside6-in-components; no parent-repo path
literals; no store-schema names."""
import ast
from pathlib import Path

ALLOWED_IMPORTS = {"snea_lib", "PySide6", "PySide6.*"}
FORBIDDEN_LITERALS = ("eliot-tritext", "tmp/ocr", "leafmaps", "grammar-sources",
                      "proofing-status.tsv")

SRC = Path(__file__).resolve().parent.parent / "src" / "snea_lib" / "proofing"


def _sources():
    return sorted(SRC.rglob("*.py"))


def test_import_graph_holds_only_allowed_roots():
    for f in _sources():
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module] if node.level == 0 else []
            for name in names:
                if name in ("snea_lib", "snea_lib.proofing") or name.startswith("snea_lib.proofing"):
                    continue
                if name.startswith("PySide6"):
                    for py in ([f] if f.name in ("widgets.py",) else []):
                        pass
                    assert "widgets" in str(f), f"{f}: pyside6 imports ride the widgets module only"
                    continue
                root = name.split(".")[0]
                assert root in ALLOWED_IMPORTS or root in __import__("sys").stdlib_module_names, (
                    f"{f}: non-self-contained import {name!r}")


def test_widgets_module_carries_pyside6_only_import():
    text = (SRC / "widgets.py").read_text(encoding="utf-8")
    assert "PySide6" in text
    others = [f for f in _sources() if f.name != "widgets.py"]
    for f in others:
        assert "PySide6" not in f.read_text(encoding="utf-8"), f"{f}: pyside6 outside widgets"


def test_no_parent_repo_path_literals_or_store_names():
    for f in _sources():
        text = f.read_text(encoding="utf-8")
        for bad in FORBIDDEN_LITERALS:
            assert bad not in text, f"{f}: carries the parent-repo/store literal {bad!r}"
