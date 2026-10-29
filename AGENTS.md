# AGENTS.md — snea-lib

<!-- SPDX-FileCopyrightText: 2026 Michael Conrad -->
<!-- SPDX-License-Identifier: MIT -->

Shared Python machinery for SNEA/PA/PEA/PSNEA projects — derivation engines,
orthography/IPA tooling, proofing/review machinery, and shared research-data
utilities. The machinery layer admits research/workflow machinery beyond the
SNEA family (the machinery serves any derived text layer); project-specific
applications still live in the consuming repos — the applications boundary
stands (snea-lib#4 §3.5).

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

## Copyright safety (enforced)

A copyright safety check is required on every addition to this repository.
Material whose license does not permit tracking — in-copyright scans, CDL
page-image captures, paywalled extracts — lives ONLY in `private/`
(gitignored): never `tmp/`, never the tracked tree. Trackable material
(public-domain text, metadata indexes, search-inside snippet text) is tracked
at its canonical home in its owning repository. `private/` holds durable
private material only — `tmp/` holds only throwaway work, cleaned up after
its task. This mirrors the copyright-placement convention of the other
`snea-*` projects.

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