# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The extra-gated UI suite (snea-lib#4 SC-6/SC-7/SC-12) under the managed
display: components render, overlays draw, side-by-side works, navigation
advances, the palette applies injected content, geometry persists across a
close/reopen cycle, and the failure-capture helper produces the artifact."""

import pytest

pytestmark = [pytest.mark.proofing_ui]

require_provisioning = pytest.mark.usefixtures("require_extra")


@require_provisioning
def test_pane_renders_a_page_image_and_captures(qapp, ui_shot):
    from snea_lib.proofing.widgets import ImagePane

    pane = ImagePane(reference_width=400)
    pane.resize(400, 300)
    pane.set_page("test/data/proofing-page.png")
    shot = ui_shot(pane, "pane-renders")
    assert shot.name == "pane-renders.png"


@require_provisioning
def test_region_overlay_draws_rectangle_and_polygon(qapp, ui_shot):
    from snea_lib.proofing.widgets import ImagePane, RegionOverlay

    pane = ImagePane(reference_width=400)
    pane.set_page("test/data/proofing-page.png")
    overlay = RegionOverlay(pane)
    overlay.set_regions([
        (((0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)), "red"),   # rectangle
        (((0.1, 0.1), (0.5, 0.0), (0.9, 0.9), (0.2, 0.8)), "blue"),  # polygon
    ])
    ui_shot(pane, "overlay-draws")
    assert overlay._regions


@require_provisioning
def test_side_by_side_two_panes(qapp, ui_shot):
    from PySide6.QtWidgets import QLabel
    from snea_lib.proofing.widgets import SideBySide

    sbs = SideBySide(QLabel("witness"), QLabel("page"))
    sbs.resize(640, 300)
    ui_shot(sbs, "side-by-side")
    assert sbs.count() == 2


@require_provisioning
def test_navigation_advances_selection(qapp, ui_shot):
    from snea_lib.proofing.widgets import Navigator

    nav = Navigator()
    nav.add_item("C31", {"span": "104-108"})
    nav.add_item("C32", {"span": "205-213"})
    nav.select(1)
    assert nav.current_payload()["span"] == "205-213"
    ui_shot(nav, "navigation")


@require_provisioning
def test_verdict_palette_applies_injected_content(qapp, ui_shot):
    from PySide6 import QtWidgets
    from snea_lib.proofing.widgets import VerdictPalette

    pressed = []
    palette = VerdictPalette(
        characters=[("ȣ", "OU ligature (U+0223)"), ("ꝏ", "double-o ligature (U+A74F)")],
        states=[("proofed", "approve the reading")],
    )
    palette.inserted.connect(pressed.append)
    palette.state_chosen.connect(pressed.append)
    buttons = palette.findChildren(QtWidgets.QPushButton)
    buttons[0].click()  # the ȣ character entry
    buttons[2].click()  # the proofed state
    ui_shot(palette, "palette")
    assert "ȣ" in pressed and "proofed" in pressed


@require_provisioning
def test_failure_time_capture(qapp, ui_shot):
    """SC-12: the failure-capture helper produces the FAILURE-live capture
    (helper-driven per the spec: "a deliberate-failure or helper-driven
    case produces the FAILURE-*.png capture")."""
    from PySide6 import QtWidgets

    pane = QtWidgets.QLabel("deliberate")
    ui_shot(pane, "before-failure")
    ui_shot.force_failure()
    shot = ui_shot.failure_capture()
    assert shot is not None and shot.exists() and shot.stat().st_size > 0


@require_provisioning
def test_geometry_persists_across_close_reopen(qapp):
    from PySide6 import QtWidgets
    import random
    from snea_lib.proofing.widgets import GeometryPersistence

    class W(QtWidgets.QWidget):
        pass

    session = f"sc7-{random.randint(0, 10**9)}"
    w1 = W()
    w1.setGeometry(30, 40, 900, 700)
    g1 = w1.geometry()
    GeometryPersistence("snea-lib-test", "proofing", session).save(w1)
    w2 = W()
    w2.resize(200, 150)
    assert GeometryPersistence("snea-lib-test", "proofing", session).restore(w2)
    # the restored geometry equals the saved widget's actual geometry
    assert w2.geometry().size() == g1.size()
    w1.close()
    w2.close()