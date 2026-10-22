# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Scaffold sanity: the library installs and imports.

# Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import snea_lib


def test_import() -> None:
    assert snea_lib.__version__ == "0.1.0"