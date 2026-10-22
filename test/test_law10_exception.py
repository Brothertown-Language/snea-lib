# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""†-class analogical-exception vectors (snea-lib#2, SC-L12).

The recorded 'good'/-ew paradigm forms (the Goddard 1981:83 class) do not
palatalize via the law, and the exception route is recorded in the trace
(the R-L4 override rule). Vectors from the recorded †-class exception data.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

from snea_lib.derivation.engine import ChainEngine, ChainInput
from snea_lib.derivation.rules import load_rules


@pytest.fixture()
def engine() -> ChainEngine:
    return ChainEngine(load_rules())


def test_recorded_form_exception_route(engine: ChainEngine) -> None:
    # the recorded †-class form: PA *werikiwa (Goddard 1981:74) — the law
    # does not palatalize via the law's route; the k carries; the exception
    # route is recorded (R-L4: the †-class overrides the law)
    result = engine.derive(ChainInput(form="*werikiwa"))
    k_seg = next(s for s in result.segments["PSNEA"] if s.sym in ("k", "t", "y"))
    assert k_seg.sym == "k", "the †-class *k palatalized via the law"
    assert not k_seg.palatal
    entry = [
        t
        for t in result.trace
        if t.law_id == "law-10" and t.note == "law10-exception-route"
    ]
    assert entry, "no law10-exception-route trace entry"


def test_declared_member_exception_route(engine: ChainEngine) -> None:
    # a declared member of the recorded -ew paradigm class: the exception
    # route precedes the arms (the override rules even in the *ē
    # environment)
    result = engine.derive(
        ChainInput(form="*ke·tam", cls=("daggers-good-ew-paradigms",))
    )
    entry = [
        t
        for t in result.trace
        if t.law_id == "law-10" and t.note == "law10-exception-route"
    ]
    assert entry, "no law10-exception-route trace entry for the declared member"
    assert "law10-e-arm" not in [t.note for t in result.trace]
    k_seg = next(s for s in result.segments["PSNEA"] if s.sym in ("k", "t"))
    assert k_seg.sym == "k"


def test_non_members_keep_their_arms(engine: ChainEngine) -> None:
    # the -e arm and the trigger arm must not regress behind the exception
    unlisted = engine.derive(ChainInput(form="*kini"))
    assert "law10-unlisted-i-context" in [f.id for f in unlisted.flags]
    e_arm = engine.derive(ChainInput(form="*ke·tam"))
    assert "law10-e-arm" in [t.note for t in e_arm.trace]
    assert next(s for s in e_arm.segments["PSNEA"] if s.sym in ("k", "t")).palatal