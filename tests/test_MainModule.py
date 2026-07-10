"""
Tests for the MainModule (src/MainModule.py).

Covers:
- RowFadeController construction
- toggle forward/backward
- setOpacity
- _on_animation_finished behaviour
- Correctness of the animation lifecycle
"""

from unittest.mock import MagicMock, patch, call, PropertyMock

import pytest


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_mock_widget(name="mock_widget"):
    """Return a MagicMock with the minimal surface RowFadeController needs."""
    w = MagicMock(name=name)
    w.objectName.return_value = name
    return w


@pytest.fixture(autouse=True)
def _mock_qgraphics():
    """Patch QGraphicsOpacityEffect in MainModule so tests don't need a
    real QApplication/QWidget parent chain.

    Each call to ``QGraphicsOpacityEffect(...)`` returns a fresh mock so
    tests can distinguish per-widget effects.
    """
    with patch("MainModule.QGraphicsOpacityEffect") as mock_cls:
        mock_cls.side_effect = lambda *a, **kw: MagicMock(name="QGraphicsOpacityEffect")
        yield


# ─── Constants ────────────────────────────────────────────────────────────────


class TestConstants:
    """RowFadeController class-level constants."""

    def test_anim_duration_ms(self):
        from MainModule import RowFadeController
        assert RowFadeController._ANIM_DURATION_MS == 500


# ─── Initialisation ──────────────────────────────────────────────────────────


class TestInit:
    """RowFadeController.__init__."""

    def test_stores_widget_list(self):
        from MainModule import RowFadeController
        w1, w2 = _make_mock_widget("a"), _make_mock_widget("b")
        ctrl = RowFadeController([w1, w2])
        assert ctrl.Widgets == [w1, w2]

    def test_creates_one_effect_per_widget(self):
        from MainModule import RowFadeController
        w1, w2 = _make_mock_widget("a"), _make_mock_widget("b")
        ctrl = RowFadeController([w1, w2])
        assert len(ctrl.Effects) == 2
        w1.setGraphicsEffect.assert_called_once()
        w2.setGraphicsEffect.assert_called_once()

    def test_animation_configured(self):
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        anim = ctrl.Animation
        assert anim.duration() == 500
        assert anim.parent() == ctrl  # tied to controller lifetime

    def test_animation_value_changed_connected(self):
        # valueChanged should be connected to setOpacity.
        # Patch before construction so the signal connects to the mock.
        with patch("MainModule.RowFadeController.setOpacity") as mock_set:
            from MainModule import RowFadeController
            w = _make_mock_widget()
            ctrl = RowFadeController([w])
            ctrl.Animation.valueChanged.emit(0.5)
            mock_set.assert_called_once_with(0.5)

    def test_animation_finished_connected(self):
        # Patch before construction so the finished signal connects to the mock
        with patch("MainModule.RowFadeController._on_animation_finished") as mock_fn:
            from MainModule import RowFadeController
            w = _make_mock_widget()
            ctrl = RowFadeController([w])
            ctrl.Animation.finished.emit()
            mock_fn.assert_called_once()


# ─── setOpacity ──────────────────────────────────────────────────────────────


class TestSetOpacity:
    """RowFadeController.setOpacity."""

    def test_sets_opacity_on_all_effects(self):
        from MainModule import RowFadeController
        w1, w2 = _make_mock_widget("a"), _make_mock_widget("b")
        ctrl = RowFadeController([w1, w2])
        effects = ctrl.Effects[:]  # snapshot before mutation
        ctrl.setOpacity(0.42)
        for effect in effects:
            effect.setOpacity.assert_called_once_with(0.42)


# ─── toggle ──────────────────────────────────────────────────────────────────


class TestToggle:
    """RowFadeController.toggle."""

    def test_forward_direction_for_true(self):
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        ctrl.toggle(True, lambda: None)
        assert ctrl.Animation.direction() == ctrl.Animation.Forward

    def test_backward_direction_for_false(self):
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        ctrl.toggle(False, lambda: None)
        assert ctrl.Animation.direction() == ctrl.Animation.Backward

    def test_stores_return_function(self):
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        fn = lambda: None
        ctrl.toggle(True, fn)
        assert ctrl._ReturnFunction is fn

    def test_starts_animation(self):
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        with patch.object(ctrl.Animation, "start") as mock_start:
            ctrl.toggle(True, lambda: None)
            mock_start.assert_called_once()

    def test_stops_previous_animation_first(self):
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        with patch.object(ctrl.Animation, "stop") as mock_stop:
            ctrl.toggle(True, lambda: None)
            mock_stop.assert_called_once()

    def test_disconnects_previous_return_function(self):
        """Calling toggle twice replaces the previous return function."""
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        ctrl._ReturnFunction = MagicMock(name="stale")
        fresh_fn = MagicMock(name="fresh")
        ctrl.toggle(True, fresh_fn)
        # The stale function should be gone
        assert ctrl._ReturnFunction is fresh_fn

    def test_double_toggle_no_stale_callback(self):
        """
        When toggle() is called twice on the same controller, only the
        most recent return function should fire on animation completion.
        """
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        stale = MagicMock(name="stale")
        fresh = MagicMock(name="fresh")

        ctrl.toggle(True, stale)
        ctrl.toggle(False, fresh)

        # Simulate animation completion
        ctrl.Animation.finished.emit()

        stale.assert_not_called()
        fresh.assert_called_once()




# ─── _on_animation_finished ──────────────────────────────────────────────────


class TestOnAnimationFinished:
    """RowFadeController._on_animation_finished."""

    def test_forward_hides_widgets(self):
        from MainModule import RowFadeController
        w1, w2 = _make_mock_widget("a"), _make_mock_widget("b")
        ctrl = RowFadeController([w1, w2])
        ctrl.Animation.setDirection(ctrl.Animation.Forward)
        ctrl._ReturnFunction = lambda: None
        ctrl._on_animation_finished()
        w1.hide.assert_called_once()
        w2.hide.assert_called_once()

    def test_backward_does_not_hide_widgets(self):
        from MainModule import RowFadeController
        w1, w2 = _make_mock_widget("a"), _make_mock_widget("b")
        ctrl = RowFadeController([w1, w2])
        ctrl.Animation.setDirection(ctrl.Animation.Backward)
        ctrl._ReturnFunction = lambda: None
        ctrl._on_animation_finished()
        w1.hide.assert_not_called()
        w2.hide.assert_not_called()

    def test_resets_graphics_effect(self):
        from MainModule import RowFadeController
        w1, w2 = _make_mock_widget("a"), _make_mock_widget("b")
        ctrl = RowFadeController([w1, w2])
        ctrl._ReturnFunction = lambda: None
        ctrl._on_animation_finished()
        # Each widget gets a setGraphicsEffect call (one from __init__, one here)
        assert w1.setGraphicsEffect.call_count == 2
        assert w2.setGraphicsEffect.call_count == 2

    def test_calls_return_function(self):
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        fn = MagicMock()
        ctrl._ReturnFunction = fn
        ctrl._on_animation_finished()
        fn.assert_called_once()

    def test_clears_return_function_after_call(self):
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        ctrl._ReturnFunction = MagicMock()
        ctrl._on_animation_finished()
        assert ctrl._ReturnFunction is None

    def test_does_not_crash_without_return_function(self):
        from MainModule import RowFadeController
        w = _make_mock_widget()
        ctrl = RowFadeController([w])
        ctrl._ReturnFunction = None
        ctrl._on_animation_finished()  # should not raise

    def test_forward_then_backward_complete_lifecycle(self):
        """Simulate a full navigation lifecycle with two controllers."""
        from MainModule import RowFadeController
        w_old, w_new = _make_mock_widget("old"), _make_mock_widget("new")
        loader_cb = MagicMock()
        done_cb = MagicMock()

        # start_loading: fade out old widgets
        ctrl_out = RowFadeController([w_old])
        ctrl_out.toggle(True, loader_cb)
        ctrl_out.Animation.finished.emit()
        loader_cb.assert_called_once()
        w_old.hide.assert_called_once()

        # end_loading: fade in new widgets
        ctrl_in = RowFadeController([w_new])
        ctrl_in.toggle(False, done_cb)
        ctrl_in.Animation.finished.emit()
        done_cb.assert_called_once()
        w_new.hide.assert_not_called()
