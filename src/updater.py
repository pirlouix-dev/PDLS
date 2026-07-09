# -*- coding: utf-8 -*-
"""
Network / update logic extracted from main.py.

Contains API data retrieval, update detection, download/install commands,
and all related module-level state.
"""

import os
import sys
import json
import webbrowser
from packaging.version import Version
from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
import pyperclip


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MacOSUpdateUrl = os.getenv(
    "MACOS_UPDATE_SCRIPT_URL",
    "https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Scripts/MacOS.sh",
)
WindowsUpdateUrl = os.getenv(
    "WINDOWS_UPDATE_SCRIPT_URL",
    "https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Scripts/Windows.bat",
)
UpdateCommands = {
    "darwin": (
        f"(curl -s {MacOSUpdateUrl} > /private/tmp/PDLS_Script.sh; "
        f"sh /private/tmp/PDLS_Script.sh; rm /private/tmp/PDLS_Script.sh) "
        f"> /dev/null 2>&1 &"
    ),
    "win32": (
        f'start /min cmd /c "curl -s -o PDLS_Installer.bat {WindowsUpdateUrl} '
        f'&& PDLS_Installer.bat && del PDLS_Installer.bat >nul 2>&1"'
    ),
}
AutoUpdateSupport = sys.platform in ("darwin", "win32")

APIUrl = os.getenv(
    "API_BASE_URL",
    "https://676d02470e299dd2ddfe1998.mockapi.io/PDLS/v1",
)

# ---------------------------------------------------------------------------
# Mutable module-level state (set by HandleAPIData / parse_api_response)
# ---------------------------------------------------------------------------

RequestSuccessful = False
FeedbackURL = None
LatestVersion = None
DownloadFolder = None
UpdateDescription = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def Warn(*args):
    """Print a warning to stderr in a clear format."""
    print("--------\nWarning: ", *args, "\n--------", file=sys.stderr)


def IsUpdateAvailable(force_update, app_version):
    """Return True when a newer version exists on the API side."""
    if not RequestSuccessful:
        return False
    return force_update or Version(app_version) < Version(LatestVersion)


def OSName(platform_name):
    """Human-readable OS name."""
    if platform_name == "darwin":
        return "MacOS"
    elif platform_name == "win32":
        return "Windows"
    return platform_name


# ---------------------------------------------------------------------------
# API Manager
# ---------------------------------------------------------------------------

class APIManager(QObject):
    """Handles the single API request that fetches app metadata.
    Updates module-level globals via parse_api_reply().
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._manager = QNetworkAccessManager(self)
        self._manager.finished.connect(self._on_reply)

    # -- public API ---------------------------------------------------------

    def retrieve(self):
        """Start the async API GET."""
        request = QNetworkRequest(QUrl(APIUrl))
        request.setTransferTimeout(5000)
        self._manager.get(request)

    # -- internal ------------------------------------------------------------

    def _on_reply(self, reply):
        parse_api_reply(reply)


# ---------------------------------------------------------------------------
# Reply parser  (standalone so it can be used from both signals and callbacks)
# ---------------------------------------------------------------------------

def parse_api_reply(reply):
    """Parse the API JSON reply and update module-level globals.

    Returns True on success, False otherwise.
    """
    global RequestSuccessful, FeedbackURL, LatestVersion, DownloadFolder, UpdateDescription

    error = reply.error()
    if error == QNetworkReply.NoError:
        try:
            answer_json = str(reply.readAll(), "utf-8")
            answer = json.loads(answer_json)[0]

            FeedbackURL = answer["feedback-url"]
            LatestVersion = answer["latest-version"]
            DownloadFolder = answer["download-folder"]
            UpdateDescription = answer["update-description"]
            RequestSuccessful = True
            return True
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            Warn("Failed to parse API response:", exc)
            RequestSuccessful = False
            return False
    else:
        RequestSuccessful = False
        Warn("Failed to retrieve data —", error)
        return False


# ---------------------------------------------------------------------------
# Update / install helpers
# ---------------------------------------------------------------------------

def run_update_command():
    """Execute the platform-specific update shell command (fire-and-forget)."""
    cmd = UpdateCommands.get(sys.platform)
    if cmd is None:
        Warn(f"No update command defined for platform {sys.platform}")
        return
    os.system(cmd)


def open_manual_update_page(download_folder):
    """Open the download URL in the default browser."""
    if download_folder:
        webbrowser.open(download_folder)


def copy_download_link(download_folder):
    """Copy download URL to clipboard."""
    pyperclip.copy(download_folder)
