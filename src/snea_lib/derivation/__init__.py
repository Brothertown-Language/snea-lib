# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Derivation machinery for SNEA/PA/PEA/PSNEA chains.

Subpackages carry the rule data of record (``rules/``) and the engines that
consume it. Data access is injected: the library is corpus-agnostic and
never touches a consumer's corpus submodule or record files directly.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""