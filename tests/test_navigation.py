"""
Tests for the navigation module (src/navigation.py).

Covers:
- Module-level global initial state
- AddWidgetDisplayInfo
- NewSignal utility
- NavigationManager start_loading / end_loading
- NavigationManager start_anim / anim_completed
- NavigationManager reload_window
"""

import sys
import time
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from navigation import (
    NavigationManager,
    NewSignal,
    AddWidgetDisplayInfo,
    WidgetDisplayInfo,
    ImpactedWidgetDisplay,
    CustomResizeFunctions,
    Loading,
    FirstStart,
)


# ─── Module-level globals ─────────────────────────────────────────────────────

class TestGlobals:
    def test_widget_display_info_starts_empty(self):
        """WidgetDisplayInfo dict is initially empty."""
        assert WidgetDisplayInfo == {}

    def test_impacted_widget_display_starts_empty(self):
        """ImpactedWidgetDisplay list is initially empty."""
        assert ImpactedWidgetDisplay == []

    def test_custom_resize_functions_starts_empty(self):
        """CustomResizeFunctions list is initially empty."""
        assert CustomResizeFunctions == []

    def test_loading_starts_false(self):
        """Loading flag starts False."""
        assert Loading is False

    def test_first_start_starts_true(self):
        """FirstStart flag starts True."""
        assert FirstStart is True


# ─── AddWidgetDisplayInfo ─────────────────────────────────────────────────────

class TestAddWidgetDisplayInfo:
    def test_adds_entry(self):
        """AddWidgetDisplayInfo adds a correct entry to the dict."""
        mock_widget = MagicMock()
        mock_widget.objectName.return_value = "TestWidget"

        AddWidgetDisplayInfo(mock_widget, (0.5, 0.5), (0.3, 0.2),
                             (0, 0), 1.5, MaximumSizeY=500)

        entry = WidgetDisplayInfo["TestWidget"]
        assert entry["CenterPositionRatio"] == (0.5, 0.5)
        assert entry["SizeRatio"] == (0.3, 0.2)
        assert entry["AnchorPoint"] == (0, 0)
        assert entry["AspectRatio"] == 1.5
        assert entry["MaximumSizeY"] == 500

    def test_default_maximum_size(self):
        """Default MaximumSizeY is 16777215."""
        mock_widget = MagicMock()
        mock_widget.objectName.return_value = "DefaultMax"

        AddWidgetDisplayInfo(mock_widget, (0, 0), (1, 1), (0.5, 0.5), 1.0)

        assert WidgetDisplayInfo["DefaultMax"]["MaximumSizeY"] == 16777215


# ─── NewSignal ────────────────────────────────────────────────────────────────

class TestNewSignal:
    def test_signal_fires(self):
        """Fire() emits the Signal, calling connected callbacks."""
        sig = NewSignal()
        called = False

        def handler():
            nonlocal called
            called = True

        sig.Connect(handler)
        sig.Fire()
        assert called

    def test_multiple_connects(self):
        """Multiple callbacks can be connected."""
        sig = NewSignal()
        results = []

        sig.Connect(lambda: results.append(1))
        sig.Connect(lambda: results.append(2))

        sig.Fire()
        assert results == [1, 2]

    def test_no_connect_does_not_crash(self):
        """Fire() with no connected handlers does nothing."""
        sig = NewSignal()
        sig.Fire()  # should not raise


# ─── NavigationManager ────────────────────────────────────────────────────────

class TestNavigationManagerInit:
    def test_stores_main_window(self):
        """NavigationManager stores a reference to the main window."""
        mw = MagicMock()
        nav = NavigationManager(mw)
        assert nav.main_window is mw

    def test_fade_controllers_starts_empty(self):
        """Internal fade controllers list is initially empty."""
        nav = NavigationManager(MagicMock())
        assert nav._fade_controllers == []


class TestStartLoading:
    def test_sets_loading_true_and_creates_fade(self):
        """start_loading sets Loading=True and creates a RowFadeController."""
        mw = MagicMock()
        nav = NavigationManager(mw)

        with patch("navigation.RowFadeController") as mock_rfc:
            mock_ctrl = MagicMock()
            mock_rfc.return_value = mock_ctrl

            loader = MagicMock()
            nav.start_loading([MagicMock(), MagicMock()], loader)

            # The RowFadeController was instantiated
            mock_rfc.assert_called_once()
            args, _ = mock_rfc.call_args
            assert len(args[0]) == 2  # two widgets passed

            # It was told to fade out (True = fade out)
            mock_ctrl.toggle.assert_called_once_with(True, loader)

    def test_skip_if_already_loading(self):
        """start_loading is a no-op if already loading."""
        import navigation
        navigation.Loading = True

        nav = NavigationManager(MagicMock())
        with patch("navigation.RowFadeController") as mock_rfc:
            nav.start_loading([MagicMock()], MagicMock())
            mock_rfc.assert_not_called()

        navigation.Loading = False  # cleanup


class TestEndLoading:
    def test_returns_new_signal(self):
        """end_loading returns a NewSignal instance."""
        mw = MagicMock()
        nav = NavigationManager(mw)

        with patch("navigation.RowFadeController") as mock_rfc:
            mock_ctrl = MagicMock()
            mock_rfc.return_value = mock_ctrl

            result = nav.end_loading([MagicMock()])
            assert isinstance(result, NewSignal)

    def test_loading_reset_after_completion(self):
        """Loading is reset to False once the fade-in finishes."""
        import navigation
        navigation.Loading = True  # pretend we were loading

        mw = MagicMock()
        nav = NavigationManager(mw)

        with patch("navigation.RowFadeController") as mock_rfc:
            mock_ctrl = MagicMock()
            mock_rfc.return_value = mock_ctrl

            nav.end_loading([MagicMock()])

            # Grab the callback that was passed to toggle(False, callback)
            callback = mock_ctrl.toggle.call_args[0][1]

            # Fire the callback — this should reset Loading
            assert navigation.Loading is True  # still true before callback
            callback()
            assert navigation.Loading is False

        navigation.Loading = False  # extra cleanup


class TestReloadWindow:
    def test_emits_resize_event(self):
        """reload_window calls the main_window's resizeEvent."""
        mw = MagicMock()
        mw.width.return_value = 800
        mw.height.return_value = 600

        nav = NavigationManager(mw)
        nav.reload_window()

        mw.resizeEvent.assert_called_once()
        event = mw.resizeEvent.call_args[0][0]
        # Verify it's a QResizeEvent-like object
        assert event.size().width() == 800
        assert event.size().height() == 600


class TestStartAnim:
    def test_normal_start(self):
        """start_anim starts the animation when stop_all_anim is False."""
        mw = MagicMock()
        mw.StopAllAnim = False
        mw.StopAllAnimTimer = 0.0

        anim = MagicMock()
        on_ended = MagicMock()

        NavigationManager.start_anim(mw, anim, on_ended)

        anim.start.assert_called_once()
        anim.finished.connect.assert_called_once_with(on_ended)

    def test_stopped_recently_jumps_to_end(self):
        """When stopped recently, anim jumps to end value."""
        mw = MagicMock()
        mw.StopAllAnim = True
        mw.StopAllAnimTimer = time.time()  # just now

        anim = MagicMock()
        end_value = MagicMock()
        anim.endValue.return_value = end_value
        on_ended = MagicMock()

        NavigationManager.start_anim(mw, anim, on_ended)

        anim.targetObject().move.assert_called_once_with(end_value)
        on_ended.assert_called_once()
        anim.start.assert_not_called()

    def test_stale_flag_proceeds(self):
        """When StopAllAnimTimer is more than 50 ms old, start normally."""
        mw = MagicMock()
        mw.StopAllAnim = True
        mw.StopAllAnimTimer = time.time() - 1.0  # 1 second ago (stale)

        anim = MagicMock()
        on_ended = MagicMock()

        NavigationManager.start_anim(mw, anim, on_ended)

        anim.start.assert_called_once()
        anim.finished.connect.assert_called_once_with(on_ended)


class TestAnimCompleted:
    def test_schedules_flag_clear(self):
        """anim_completed schedules a timer to clear CurrentlyAnimating."""
        mw = MagicMock()
        mw.CurrentlyAnimating = True

        with patch("navigation.QTimer.singleShot") as mock_singleshot:
            NavigationManager.anim_completed(mw)

            mock_singleshot.assert_called_once()
            args, _ = mock_singleshot.call_args
            assert args[0] == 50  # 50 ms delay
            # The callback should set CurrentlyAnimating to False
            args[1]()  # invoke the callback
            assert mw.CurrentlyAnimating is False
