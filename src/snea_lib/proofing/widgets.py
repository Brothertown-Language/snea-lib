# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""The GUI components (extra-gated ``proofing``): the shared machinery the
three family implementations repeatedly re-derived. Content is injectable
at every seam — vocabularies, palette contents, geometry callbacks, register
writers; the library never knows a store path.

Requires pyside6 via the ``proofing`` extra:

    uv sync --extra proofing

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError as exc:  # the named provisioning instruction lives here
    raise ImportError(
        "snea_lib.proofing.widgets requires the proofing extra: "
        "uv sync --extra proofing"
    ) from exc

PROOFING_MARKER = "proofing_ui"
PROVISION_INSTRUCTION = "uv sync --extra proofing"


class ImagePane(QtWidgets.QLabel):
    """The page-image pane: renders a page image at reference metrics."""

    def __init__(self, reference_width: int = 1280, parent=None):
        super().__init__(parent)
        self._reference_width = reference_width
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._original: QtGui.QPixmap | None = None

    def set_page(self, path: str) -> None:
        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            raise FileNotFoundError(f"page image {path!r} did not load")
        self._original = pixmap
        self._rescale()

    def _rescale(self) -> None:
        if self._original is not None:
            self.setPixmap(
                self._original.scaledToWidth(
                    self._reference_width,
                    QtCore.Qt.TransformationMode.SmoothTransformation,
                )
            )


class RegionOverlay(QtWidgets.QWidget):
    """Region overlays supporting rectangles and polygons, drawn in relative
    coordinates over the pane's current contents."""

    def __init__(self, pane: ImagePane, parent=None):
        super().__init__(pane)
        self._pane = pane
        self._regions: list = []  # (points, color-name) pairs
        pane.installEventFilter(self)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_regions(self, regions: list[tuple]) -> None:
        self._regions = list(regions)
        self.update()

    def eventFilter(self, watched, event):  # noqa: N802 (Qt naming)
        if watched is self._pane and event.type() == QtCore.QEvent.Type.Resize:
            self.setGeometry(self._pane.rect())
        return super().eventFilter(watched, event)

    def paintEvent(self, event):  # noqa: N802 (Qt naming)
        painter = QtGui.QPainter(self)
        pm = self._pane.pixmap()
        if pm is None:
            return
        sx = self.width() / pm.width() if pm.width() else 1
        sy = self.height() / pm.height() if pm.height() else 1
        for (points, color) in self._regions:
            pts = [QtCore.QPointF(px * sx, py * sy) for (px, py) in points]
            poly = QtGui.QPolygonF(pts)
            pen = QtGui.QPen(QtGui.QColor(color))
            pen.setWidth(2)
            painter.setPen(pen)
            if len(pts) == 2:
                a, b = pts[0], pts[1]
                painter.drawRect(QtCore.QRectF(a.x(), a.y(), b.x() - a.x(), b.y() - a.y()))
            else:
                painter.drawPolygon(poly)


class SideBySide(QtWidgets.QSplitter):
    """The side-by-side two-pane comparison: witness/crop pane against the
    page or text pane."""

    def __init__(self, left: QtWidgets.QWidget, right: QtWidgets.QWidget, parent=None):
        super().__init__(QtCore.Qt.Orientation.Horizontal, parent)
        self.addWidget(left)
        self.addWidget(right)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 1)


class _Signal(QtCore.QObject):
    changed = QtCore.Signal(object)


class Navigator(QtWidgets.QListWidget):
    """Item/region navigation: selection state among registered items."""

    selection_changed = QtCore.Signal(int)

    def add_item(self, title: str, payload) -> None:
        item = QtWidgets.QListWidgetItem(title)
        item.setData(QtCore.Qt.ItemDataRole.UserRole, payload)
        self.addItem(item)

    def select(self, index: int) -> None:
        self.setCurrentRow(index)
        self.selection_changed.emit(index)

    def current_payload(self):
        item = self.currentItem()
        return item.data(QtCore.Qt.ItemDataRole.UserRole) if item else None


class VerdictPalette(QtWidgets.QWidget):
    """A verdict palette whose character/content set is injected: one button
    per palette entry (insertable characters) and one per verdict state."""

    inserted = QtCore.Signal(str)
    state_chosen = QtCore.Signal(str)

    def __init__(self, characters: list[tuple[str, str]],
                 states: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        row = QtWidgets.QHBoxLayout(self)
        for char, tooltip in characters:
            b = QtWidgets.QPushButton(char)
            b.setToolTip(f"insert {tooltip}")
            b.clicked.connect(lambda _, c=char: self.inserted.emit(c))
            row.addWidget(b)
        for state, tooltip in states:
            b = QtWidgets.QPushButton(state)
            b.setToolTip(tooltip)
            b.clicked.connect(lambda _, s=state: self.state_chosen.emit(s))
            row.addWidget(b)


class GeometryPersistence:
    """Window-geometry persistence and restore (QSettings, per session key)."""

    def __init__(self, org: str, app: str, session: str):
        self._settings = QtCore.QSettings(org, app)
        self._session = session

    def save(self, window: QtWidgets.QWidget) -> None:
        self._settings.setValue(f"{self._session}/geometry", window.saveGeometry())

    def restore(self, window: QtWidgets.QWidget) -> bool:
        geo = self._settings.value(f"{self._session}/geometry")
        if geo is None:
            return False
        window.restoreGeometry(geo)
        return True