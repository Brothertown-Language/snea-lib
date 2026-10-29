# snea-lib

Shared Python machinery for SNEA/PA/PEA/PSNEA projects — derivation engines,
orthography/IPA tooling, and shared research-data utilities. Project-specific
applications live in the consuming repos.

**Charter boundary**: this repo holds general SNEA/PA/PEA/PSNEA machinery and
shared research/workflow machinery usable beyond the SNEA family (snea-lib#4's
proofing machinery serves any derived text layer); it does not hold
project-specific applications — wired applications stay in consuming repos.

## The proofing machinery (`snea_lib.proofing`)

The OCR-sourcing proofing machinery (snea-lib#4): the runbook's locator space
and record semantics (`proofing.model`), the review core over text- and
image-anchored subjects with injected vocabularies and register writers
(`proofing.review`), and the extra-gated GUI components (`proofing.widgets`,
pyside6 via `[proofing]`). The UI test posture ships as reusable fixtures in
`test/conftest.py` — the managed display (Xvfb at 1080p; ``SNEA_UI_SCREEN=4k``
for 4K; offscreen fallback), the per-operation ``ui_shot`` capture with its
failure-time live capture, and the ``proofing_ui`` pytest marker (self-skipping
with ``uv sync --extra proofing`` when unprovisioned). Consumer adoption: mount
the library, declare the same marker, and consume the shared fixtures from the
conftest-by-reference pattern. Consumers mount it as a git
submodule (corpus-style) and record the mounted pointer; pointer updates are
explicit, named parent-repo changes.

**Status**: setup stage of the v1 derivation library — scaffold and packaging
only. The derivation engine (PA composition, forward PA→PEA→PSNEA→BL chain,
daughter→PSNEA→BL inverse chain) is specced at
[Brothertown-Language/snea-phonetics#134](https://github.com/Brothertown-Language/snea-phonetics/issues/134)
and is not yet implemented.

**Notation**: Costa-alphabet storage for BL/PSNEA forms is the shared notation
norm — storage is always the Costa alphabet; community orthographies are
display-time rendering overrides (same standard as `snea-grammar`).

## Commands

| Task | Command |
|------|---------|
| Sync dependencies | `uv sync` |
| Run tests | `uv run pytest test/` |
| Lint | `uvx ruff check src/ test/` |
| Type check | `uvx pyright src/` |

## License

MIT — see [LICENSE](LICENSE).

---

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)