# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The OCR-sourcing proofing machinery: the runbook's semantics as code.

The semantics' source of record is the OCR-sourcing proofing runbook
(`docs/runbooks/ocr-sourcing-proofing.md` in the consuming repository that
ships it), read at authoring time — never at runtime: this package carries
the runbook's locator space, closed four-status vocabulary, record fields,
coverage-interval tracking with the OCR-7 extension rule, and the review
core over both anchor families (text-anchored and image-anchored), with
every consumer seam injected (vocabularies, palette contents, geometry
callbacks, register writers). The library knows kinds of anchors and record
contracts — never a store's layout, nor any region's meaning.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""