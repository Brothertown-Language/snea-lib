# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""snea-lib: shared Python machinery for SNEA/PA/PEA/PSNEA projects.

Derivation engines, orthography/IPA tooling, and shared research-data
utilities. Consumed by mounting this repository as a git submodule and
importing ``snea_lib``. Project-specific applications live in the consuming
repos.

Derivation machinery (Brothertown-Language/snea-lib#2): the rule-data package
of record at ``snea_lib.derivation.rules`` — the forward correspondence
tables, the verified forward laws, the candidate B-laws with the
tie-breaker ladder and weights, the Law-10 trigger list, the †-class
exception data, the recorded B5 applications (pending ratification), the
per-daughter reversed rules, and the BL rendering data — plus the engines
that consume it: the token-based segment engine with the ordered
stage-wise law pipeline and its conservative discipline, the composition
subsystem feeding the forward chain its parse, the inverse subsystem
(daughter attestations → PSNEA candidate sets), the cross-verification
surface, and the migrated ``snea_lib.bl_ipa`` BL orthography/IPA home.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

__version__ = "0.1.0"