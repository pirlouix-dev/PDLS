# -*- coding: utf-8 -*-
"""
Navigation manager for PDLS.

Extracted from main.py to isolate UI orchestration:
  - Screen transition logic (StartLoading / EndLoading with fade)
  - Widget display-info system for proportional resizing
  - Window resize helper (ReloadWindow)
  - Animation orchestration helpers
  - NewSignal utility signal class

This is a mechanical extraction — no behaviour changes.
"""

import time
from PyQt5 import sip
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import QObject, QSize, QPropertyAnimation, QTimer, pyqtSignal
from PyQt5.QtGui import QResizeEvent
from MainModule import RowFadeController


# ─── Utility signal ───────────────────────────────────────────────────────────

class NewSignal(QObject):
    """One-shot signal that can be .Fire()'d and .Connect()'d."""
    Signal = pyqtSignal()

    def Fire(self):
        self.Signal.emit()

    def Connect(self, Func):
        self.Signal.connect(Func)


# ─── Global display / resize state ───────────────────────────────────────────

WidgetDisplayInfo = {}           # object-name → display metadata
ImpactedWidgetDisplay = []       # widgets to reposition on resize
CustomResizeFunctions = []       # extra resize callbacks
Loading = False                  # fade animation in progress
FirstStart = True                # very first LoadMainMenu call


def AddWidgetDisplayInfo(Widget, CenterPositionRatio, SizeRatio,
                         AnchorPoint, AspectRatio, MaximumSizeY=16777215):
    """Register a widget for automatic proportional resize."""
    global WidgetDisplayInfo
    WidgetDisplayInfo[Widget.objectName()] = {
        "CenterPositionRatio": CenterPositionRatio,
        "SizeRatio": SizeRatio,
        "AnchorPoint": AnchorPoint,
        "AspectRatio": AspectRatio,
        "MaximumSizeY": MaximumSizeY,
    }


# ─── NavigationManager ───────────────────────────────────────────────────────

class NavigationManager:
    """Owns screen-transition and resize orchestration for MainWindow."""

    def __init__(self, main_window):
        """
        Parameters
        ----------
        main_window : MainWindow
            The QMainWindow subclass this manager controls.
        """
        self.main_window = main_window
        # Keep a reference to each RowFadeController so it isn't GC'd
        # while its animation is running.
        self._fade_controllers = []

    # ── Transitions ───────────────────────────────────────────────────────

    def start_loading(self, old_widgets, new_loader):
        """Fade out *old_widgets* (bypass if already loading)."""
        global Loading
        if Loading:
            return
        Loading = True

        ctrl = RowFadeController(old_widgets)
        self._fade_controllers = [ctrl]
        ctrl.toggle(True, new_loader)

    def end_loading(self, new_widgets):
        """Fade in *new_widgets* and return a NewSignal fired when done."""
        ended = NewSignal()

        def _on_fade_in_ended():
            global Loading
            Loading = False
            ended.Fire()

        ctrl = RowFadeController(new_widgets)
        self._fade_controllers = [ctrl]
        ctrl.toggle(False, _on_fade_in_ended)
        return ended

    # ── Resize ────────────────────────────────────────────────────────────

    def reload_window(self):
        """Trigger a synthetic resize event, forcing all registered
        display-info callbacks to reposition their widgets."""
        mw = self.main_window
        cur = QSize(mw.width(), mw.height())
        mw.resizeEvent(QResizeEvent(cur, cur))

    # ── Animation helpers (used by ChooseMenu) ────────────────────────────

    @staticmethod
    def start_anim(main_window, anim, on_ended):
        """Start a QPropertyAnimation, respecting the stop-all-anim
        flag on *main_window* (used by CancelAllAnim during resizes).

        Preserves the original logic including the `StoppAllAnim` typo.
        """
        if not main_window.StopAllAnim:
            anim.start()
            anim.finished.connect(on_ended)
        elif time.time() - main_window.StopAllAnimTimer > 0.05:
            main_window.StoppAllAnim = False  # intentional typo preserved
            anim.start()
            anim.finished.connect(on_ended)
        else:
            anim.targetObject().move(anim.endValue())
            on_ended()

    @staticmethod
    def anim_completed(main_window):
        """Schedule clearing of the CurrentlyAnimating flag on
        *main_window* after 50 ms."""
        QTimer.singleShot(50, lambda: setattr(main_window,
                                               'CurrentlyAnimating', False))
