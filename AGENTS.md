# AGENTS.md — snea-lib

<!-- SPDX-FileCopyrightText: 2026 Michael Conrad -->
<!-- SPDX-License-Identifier: MIT -->

Shared Python machinery for SNEA/PA/PEA/PSNEA projects — derivation engines,
orthography/IPA tooling, and shared research-data utilities. Project-specific
applications live in the consuming repos.

## Consumption

`Brothertown-Language/snea-phonetics` mounts this repository as a git
submodule and records the mounted pointer (developer ruling 2026-10-22).
Pointer updates ride explicit, named parent-repo changes — never silent
resolution updates.

## Commands

| Task | Command | Note |
|------|---------|------|
| Sync dependencies | `uv sync` | uses `pyproject.toml` |
| Run tests | `uv run pytest test/` | scaffold + engine tests |
| Lint | `uvx ruff check src/ test/` | Python only |
| Type check | `uvx pyright src/` | Python only |

**Never** use bare `python`, `python3`, or `pip` — always prefix with
`uv run`/`uvx`.

## Notation

Costa-alphabet storage for BL/PSNEA forms is the shared notation norm —
storage is always the Costa alphabet; community orthographies (Trumbull,
Prince-Speck, Williams, Edwards, et al.) are display-time rendering overrides.
One convention feeds both this library and `snea-grammar`.

## Workflow

- Branch before any file modification (`feature/<issue>-<slug>`); trunk is
  hook-protected.
- Rule-data files are versioned artifacts of the library, shipped as package
  data; the `.md` source-layer documents of the consuming record never feed
  the engine.
- Context-dependent conversion is table-driven, never regex (the research
  cards' standing convention).

## Reference

The deck conventions (floor, authorization vocabulary, tool hierarchy) live in
the consuming repository's `.opencode/` and govern agent work here.

---

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)