# snea-lib

Shared Python machinery for SNEA/PA/PEA/PSNEA projects — derivation engines,
orthography/IPA tooling, and shared research-data utilities. Project-specific
applications live in the consuming repos.

**Charter boundary**: this repo holds general SNEA/PA/PEA/PSNEA machinery; it
does not hold project-specific applications. Consumers mount it as a git
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