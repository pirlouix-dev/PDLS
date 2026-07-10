"""
Tests for standalone helper functions defined in src/main.py.

Covers:
- GetStyleSheet        (CSS template formatting)
- TwoChar              (zero-padded number formatting)
- Plurial              (French plural helper)
- OSName               (platform name mapping)
- Warn                 (warning printer)
- MakeTextFitByCropping (text cropping logic)
- MakeTextFitWithSize   (font size reduction)
- MessageStyleSheet     (message box styling)
"""

from unittest.mock import MagicMock, patch, PropertyMock

import pytest


# ─── GetStyleSheet ────────────────────────────────────────────────────────────


class TestGetStyleSheet:
    """GetStyleSheet should produce a valid CSS block with interpolated RGBA."""

    def test_inserts_rgba_values(self):
        """The four RGBA values appear in order in the output."""
        from main import GetStyleSheet
        result = GetStyleSheet((10, 20, 30, 255))
        assert "rgba(10, 20, 30, 255)" in result

    def test_accepts_tuple(self):
        from main import GetStyleSheet
        result = GetStyleSheet((100, 149, 237, 200))
        assert "rgba(100, 149, 237, 200)" in result

    def test_accepts_list(self):
        from main import GetStyleSheet
        result = GetStyleSheet([50, 100, 150, 128])
        assert "rgba(50, 100, 150, 128)" in result

    def test_returns_stylesheet_string(self):
        from main import GetStyleSheet
        result = GetStyleSheet((255, 255, 255, 255))
        assert result.startswith("\n        MainWindow {")
        assert "background-color:" in result
        assert "background-position: center;" in result
        assert result.strip().endswith("}")


# ─── TwoChar ─────────────────────────────────────────────────────────────────


class TestTwoChar:
    """TwoChar pads single-digit integers with a leading zero."""

    def test_single_digit(self):
        from main import TwoChar
        assert TwoChar(3) == "03"

    def test_single_digit_string(self):
        from main import TwoChar
        assert TwoChar("7") == "07"

    def test_double_digit(self):
        from main import TwoChar
        assert TwoChar(12) == "12"

    def test_double_digit_string(self):
        from main import TwoChar
        assert TwoChar("42") == "42"

    def test_zero(self):
        from main import TwoChar
        assert TwoChar(0) == "00"

    def test_negative(self):
        from main import TwoChar
        # str(-5) == "-5", len 2 → no padding
        assert TwoChar(-5) == "-5"

    def test_large_number(self):
        from main import TwoChar
        assert TwoChar(999) == "999"


# ─── Plurial ──────────────────────────────────────────────────────────────────


class TestPlurial:
    """Plurial returns French plural suffix: '' for 0/1, 's' otherwise."""

    def test_zero_returns_empty(self):
        from main import Plurial
        assert Plurial(0) == ""

    def test_one_returns_empty(self):
        from main import Plurial
        assert Plurial(1) == ""

    def test_two_returns_s(self):
        from main import Plurial
        assert Plurial(2) == "s"

    def test_large_number_returns_s(self):
        from main import Plurial
        assert Plurial(100) == "s"

    def test_accepts_string(self):
        from main import Plurial
        assert Plurial("0") == ""
        assert Plurial("1") == ""
        assert Plurial("3") == "s"


# ─── OSName ───────────────────────────────────────────────────────────────────


class TestOSName:
    """OSName maps sys.platform values to human-readable names."""

    def test_darwin(self):
        from main import OSName
        assert OSName("darwin") == "MacOS"

    def test_win32(self):
        from main import OSName
        assert OSName("win32") == "Windows"

    def test_linux(self):
        from main import OSName
        assert OSName("linux") == "linux"

    def test_other_platform(self):
        from main import OSName
        assert OSName("cygwin") == "cygwin"

    def test_case_sensitive(self):
        """Only exact lowercase values are mapped."""
        from main import OSName
        assert OSName("Darwin") == "Darwin"


# ─── Warn ─────────────────────────────────────────────────────────────────────


class TestWarn:
    """Warn prints a formatted warning message to stdout."""

    def test_prints_message(self, capsys):
        from main import Warn
        Warn("something is off")
        captured = capsys.readouterr()
        assert "Warning:" in captured.out
        assert "something is off" in captured.out

    def test_prints_multiple_args(self, capsys):
        from main import Warn
        Warn("a", "b", "c")
        captured = capsys.readouterr()
        assert "a b c" in captured.out

    def test_returns_none(self):
        from main import Warn
        assert Warn("ok") is None


# ─── MakeTextFitByCropping ────────────────────────────────────────────────────


class TestMakeTextFitByCropping:
    """MakeTextFitByCropping crops text with '…' when it overflows the label."""

    def _make_label_mock(self, font=None, contents_rect_size=(200, 50)):
        """Build a label MagicMock with configurable font/rect."""
        from PyQt5.QtCore import QSize, QRect, QPoint, Qt
        from PyQt5.QtGui import QFont

        label = MagicMock()
        label.font.return_value = font or QFont()
        label.contentsRect.return_value = QRect(QPoint(0, 0), QSize(*contents_rect_size))
        return label

    def test_text_fits_returns_original(self):
        """When text fits, return (original_text, True)."""
        from main import MakeTextFitByCropping
        from PyQt5.QtGui import QFontMetrics, QFont

        label = self._make_label_mock()
        text = "Short text"
        # Make bounding rect small enough to fit
        with patch("main.QFontMetrics.boundingRect") as mock_br:
            mock_br.return_value.size.return_value.height.side_effect = [10, 10]
            result, fits = MakeTextFitByCropping(text, label, 1, "")
        assert result == text
        assert fits is True

    def test_crops_when_overflow(self):
        """When text is too tall, cropping occurs and fits is False."""
        from main import MakeTextFitByCropping

        label = self._make_label_mock(contents_rect_size=(200, 20))  # small label
        text = "A very long text that should be cropped because it is way too long"

        # Each call to boundingRect returns a rect whose height decreases
        # (simulating text getting shorter as we crop)
        call_count = [0]

        def rect_with_decreasing_height(*args, **kwargs):
            rect_mock = MagicMock()
            call_count[0] += 1
            c = call_count[0]
            if c == 1:
                h = 100   # initial: too tall
            else:
                h = 10    # subsequent: short enough after cropping
            rect_mock.size.return_value.height.return_value = h
            return rect_mock

        with patch("main.QFontMetrics.boundingRect", side_effect=rect_with_decreasing_height):
            result, fits = MakeTextFitByCropping(text, label, 1, "")
        assert fits is False
        assert result.endswith("...")

    def test_returns_tuple_of_length_two(self):
        """Function returns a (str, bool) tuple."""
        from main import MakeTextFitByCropping

        label = self._make_label_mock()
        text = "Hi"
        with patch("main.QFontMetrics.boundingRect") as mock_br:
            mock_br.return_value.size.return_value.height.return_value = 10
            result = MakeTextFitByCropping(text, label, 1, "")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], bool)


# ─── MakeTextFitWithSize ──────────────────────────────────────────────────────


class TestMakeTextFitWithSize:
    """MakeTextFitWithSize reduces font pixel size until text fits."""

    def _make_label_mock(self, width=200, pixel_size=20):
        """Build a label with configurable width and font."""
        from PyQt5.QtGui import QFont
        label = MagicMock()
        label.width.return_value = width
        font = QFont()
        font.setPixelSize(pixel_size)
        label.font.return_value = font
        return label

    def test_returns_font_when_text_fits(self):
        """When text already fits, return the original font unchanged."""
        from main import MakeTextFitWithSize

        label = self._make_label_mock(width=500, pixel_size=20)
        with patch("main.QFontMetrics.horizontalAdvance") as mock_adv:
            mock_adv.return_value = 100  # fits in 500px
            result = MakeTextFitWithSize("Hi", label, 1, 0)
        assert result is label.font()

    def test_reduces_font_when_text_overflow(self):
        """When text is too wide, pixel size is decreased."""
        from main import MakeTextFitWithSize

        label = self._make_label_mock(width=100, pixel_size=20)
        with patch("main.QFontMetrics.horizontalAdvance") as mock_adv:
            # First call: too wide, subsequent: fits
            mock_adv.side_effect = [200, 50]
            result = MakeTextFitWithSize("A longer text that overflows", label, 1, 0)
        assert result is not None
        # The returned font should have been reduced
        assert result.pixelSize() < 20  # reduced from original

    def test_returns_font(self):
        """Function must return a QFont-like object."""
        from main import MakeTextFitWithSize
        from PyQt5.QtGui import QFont

        label = self._make_label_mock(width=500)
        with patch("main.QFontMetrics.horizontalAdvance") as mock_adv:
            mock_adv.return_value = 50
            result = MakeTextFitWithSize("Tiny", label, 1, 0)
        assert result is not None

    def test_accepts_line_count_param(self):
        """LineCount multiplies the effective label width."""
        from main import MakeTextFitWithSize

        label = self._make_label_mock(width=200)
        with patch("main.QFontMetrics.horizontalAdvance") as mock_adv:
            mock_adv.return_value = 50
            result = MakeTextFitWithSize("Text", label, 3, 0)
        assert result is not None

    def test_accepts_offset_param(self):
        """Offset reduces the available width."""
        from main import MakeTextFitWithSize

        label = self._make_label_mock(width=200)
        with patch("main.QFontMetrics.horizontalAdvance") as mock_adv:
            mock_adv.return_value = 50
            result = MakeTextFitWithSize("Text", label, 1, 30)
        assert result is not None


# ─── MessageStyleSheet ────────────────────────────────────────────────────────


class TestMessageStyleSheet:
    """MessageStyleSheet returns a CSS string with the message box palette colour."""

    def _make_message_box_mock(self, color_name="#rrggbb"):
        """Build a MessageBox MagicMock that returns a given colour name."""
        msgbox = MagicMock()
        palette = MagicMock()
        window = MagicMock()
        window.color.return_value.name.return_value = color_name
        palette.window.return_value = window
        msgbox.palette.return_value = palette
        return msgbox

    def test_contains_qpushbutton_rules(self):
        from main import MessageStyleSheet
        msgbox = self._make_message_box_mock()
        result = MessageStyleSheet(msgbox)
        assert "QPushButton" in result
        assert "background-color:" in result
        assert "border-radius:" in result

    def test_interpolates_background_color(self):
        from main import MessageStyleSheet
        msgbox = self._make_message_box_mock("#abcdef")
        result = MessageStyleSheet(msgbox)
        assert "solid #abcdef" in result

    def test_contains_hover_state(self):
        from main import MessageStyleSheet
        msgbox = self._make_message_box_mock()
        result = MessageStyleSheet(msgbox)
        assert "QPushButton:hover" in result
        assert "background-color:" in result

    def test_contains_focus_state(self):
        from main import MessageStyleSheet
        msgbox = self._make_message_box_mock()
        result = MessageStyleSheet(msgbox)
        assert "QPushButton:focus" in result

    def test_returns_string(self):
        from main import MessageStyleSheet
        msgbox = self._make_message_box_mock()
        result = MessageStyleSheet(msgbox)
        assert isinstance(result, str)
        assert len(result) > 50
