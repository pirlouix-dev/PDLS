from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtCore import QObject, QVariantAnimation


class RowFadeController(QObject):
    """Controls fade transitions on a list of widgets.

    Call :meth:`toggle` with ``FadeIn=True`` (forward direction) to
    animate opacity 1.0 -> 0.0 then hide widgets; with
    ``FadeIn=False`` (backward) to animate 0.0 -> 1.0.  A
    *ReturnFunction* callback is invoked when the animation completes.
    """

    _ANIM_DURATION_MS = 500

    def __init__(self, Widgets):
        super().__init__()
        self.Widgets = Widgets
        self._ReturnFunction = None
        self.Effects = []
        for Widget in Widgets:
            Effect = QGraphicsOpacityEffect(Widget, opacity=1.0)
            Widget.setGraphicsEffect(Effect)
            self.Effects.append(Effect)

        self.Animation = QVariantAnimation(self)
        self.Animation.setDuration(self._ANIM_DURATION_MS)
        self.Animation.setStartValue(1.0)
        self.Animation.setEndValue(0.0)
        self.Animation.valueChanged.connect(self.setOpacity)
        self.Animation.finished.connect(self._on_animation_finished)

    # ── public API ───────────────────────────────────────────────────────

    def toggle(self, FadeIn, ReturnFunction):
        self.Animation.stop()
        self._disconnect_return()
        self._ReturnFunction = ReturnFunction
        self.Animation.setDirection(
            self.Animation.Forward if FadeIn else self.Animation.Backward
        )
        self.Animation.start()

    # ── internal ─────────────────────────────────────────────────────────

    def _on_animation_finished(self):
        if self.Animation.direction() == self.Animation.Forward:
            for Widget in self.Widgets:
                Widget.hide()

        for Widget in self.Widgets:
            Widget.setGraphicsEffect(QGraphicsOpacityEffect(opacity=1.0))

        fn = self._ReturnFunction
        self._ReturnFunction = None
        if fn:
            fn()

    def _disconnect_return(self):
        self._ReturnFunction = None

    def setOpacity(self, Opacity):
        for Effect in self.Effects:
            Effect.setOpacity(Opacity)
            
    