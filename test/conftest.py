# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The proofing UI test posture (snea-lib#4 R-6/SC-5/SC-6/SC-12):

- a conftest-managed Xvfb display at 1080p (set ``SNEA_UI_SCREEN=4k`` for
  3840x2160; offscreen fallback where Xvfb is absent);
- per-state-changing-operation screenshot capture through ``ui_shot``;
- failure-time live capture (outcome-driven or forced);
- the loud skip with the named provisioning instruction when the
  ``proofing`` extra (pyside6) is absent.
"""

from pathlib import Path

import pytest

try:
    import PySide6  # noqa: F401

    _HAVE_EXTRA = True
except ImportError:
    _HAVE_EXTRA = False

PROVISION_INSTRUCTION = "uv sync --extra proofing"
SCREENS = {"1080p": (1920, 1080, 24), "4k": (3840, 2160, 24)}


def _screen_size():
    import os

    return SCREENS.get(os.environ.get("SNEA_UI_SCREEN", "1080p").lower(),
                       SCREENS["1080p"])


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session", autouse=True)
def managed_display(request):
    """The managed display: Xvfb at 1080p (or 4K) when present, offscreen
    fallback otherwise. Only active while the extra is provisioned."""
    import os
    import shutil
    import subprocess

    if not _HAVE_EXTRA:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        yield None
        return
    if not shutil.which("Xvfb"):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        yield None
        return
    w, h, depth = _screen_size()
    display = os.environ.get("XVFB_DISPLAY", ":99")
    proc = subprocess.Popen(
        ["Xvfb", display, "-screen", "0", f"{w}x{h}x{depth}", "-nolisten", "tcp"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.environ["DISPLAY"] = display
    os.environ.pop("QT_QPA_PLATFORM", None)
    try:
        yield proc
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture
def qapp():
    """A QApplication instance for the UI tests."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def ui_shot(request, tmp_path: Path):
    """Per-state-changing-operation screenshot capture; registers the
    failure-time live capture of the last-shot widget (outcome-driven, or
    forced via ``ui_shot.force_failure()`` for the helper-driven case)."""
    captured: dict[str, Path] = {}
    last_widget = {"widget": None}
    forced = {"failure": False}

    def shoot(widget, name: str) -> Path:
        last_widget["widget"] = widget
        path = tmp_path / f"{name}.png"
        widget.grab().save(str(path))
        assert path.exists() and path.stat().st_size > 0, "screenshot did not land"
        captured[name] = path
        return path

    def failure_capture():
        widget = last_widget["widget"]
        outcome = getattr(request.node, "rep_call", None)
        if widget is not None and (
            forced["failure"] or (outcome is not None and outcome.failed)
        ):
            path = tmp_path / "FAILURE-live.png"
            widget.grab().save(str(path))
            assert path.exists() and path.stat().st_size > 0
            return path
        return None

    shoot.failure_capture = failure_capture
    shoot.force_failure = lambda: forced.update(failure=True)
    shoot.captured = captured
    yield shoot
    if request.session.testsfailed:
        failure_capture()


@pytest.fixture
def require_extra():
    """SC-5's loud skip with the named provisioning instruction."""
    if not _HAVE_EXTRA:
        pytest.skip("the proofing UI suite needs pyside6 — provision: "
                    + PROVISION_INSTRUCTION)