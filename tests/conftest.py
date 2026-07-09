"""
Shared fixtures for PDLS tests.

Sets up a QApplication stub so PyQt5 imports work in headless mode,
and resets updater globals between tests.
"""

import sys
import os
import pytest
from PyQt5.QtWidgets import QApplication

# Make src/ importable
_SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# Prevent Qt from trying to open a display
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(autouse=True)
def _reset_updater():
    """Reset updater module globals before each test."""
    import updater
    # Reset globals to initial state before each test
    updater.ResetAPIData()
    # Re-set default UpdateCommands and AutoUpdateSupport
    updater.AutoUpdateSupport = sys.platform in ("darwin", "win32")
    yield


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication singleton for the entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app
