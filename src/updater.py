"""
updater.py — Network/update logic for PDLS.

Extracted from main.py for testability and separation of concerns.
Contains API data retrieval, update availability checking, and
download/installation logic originally mixed into the MainWindow class.
"""

import os
import sys
import json
from packaging.version import Version
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply

# ─── Constants ────────────────────────────────────────────────────────────────

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
        f"(curl -s {MacOSUpdateUrl} > /private/tmp/PDLS_Script.sh;"
        f" sh /private/tmp/PDLS_Script.sh;"
        f" rm /private/tmp/PDLS_Script.sh) > /dev/null 2>&1 &"
    ),
    "win32": (
        f'start /min cmd /c "curl -s -o PDLS_Installer.bat {WindowsUpdateUrl}'
        f' && PDLS_Installer.bat && del PDLS_Installer.bat >nul 2>&1"'
    ),
}
AutoUpdateSupport = sys.platform in ("darwin", "win32")

APIUrl = os.getenv(
    "API_BASE_URL",
    "https://676d02470e299dd2ddfe1998.mockapi.io/PDLS/v1",
)

# ─── Global state (set by HandleAPIData) ─────────────────────────────────────

RequestSuccessful = False
FeedbackURL: str | None = None
LatestVersion: str | None = None
DownloadFolder: str | None = None
UpdateDescription: str | None = None

# Keep a reference to the active QNetworkAccessManager to prevent GC.
_network_manager: QNetworkAccessManager | None = None


# ─── API helpers ──────────────────────────────────────────────────────────────

def IsUpdateAvailable(app_version: str, force_update: bool = False) -> bool:
    """Return True when a newer version is available from the API."""
    if not RequestSuccessful:
        return False
    return force_update or Version(app_version) < Version(LatestVersion)


def HandleAPIData(reply: QNetworkReply) -> None:
    """Parse the API JSON response and store results in module globals."""
    global RequestSuccessful, FeedbackURL, LatestVersion, DownloadFolder, \
        UpdateDescription

    error = reply.error()
    if error == QNetworkReply.NoError:
        raw = str(reply.readAll(), "utf-8")
        data = json.loads(raw)[0]

        FeedbackURL = data.get("feedback-url")
        LatestVersion = data.get("latest-version")
        DownloadFolder = data.get("download-folder")
        UpdateDescription = data.get("update-description")
        RequestSuccessful = True
    else:
        RequestSuccessful = False


def RetreiveAPIData(api_url: str | None = None) -> QNetworkAccessManager:
    """Start an asynchronous GET request to the PDLS API.

    Returns the QNetworkAccessManager so callers can keep a reference
    alive; this module also retains one internally.
    """
    global _network_manager, APIUrl

    url = api_url if api_url is not None else APIUrl
    request = QNetworkRequest(QUrl(url))
    request.setTransferTimeout(5000)

    manager = QNetworkAccessManager()
    manager.finished.connect(HandleAPIData)
    manager.get(request)

    # Keep a reference so the reply/manager aren't GC'd.
    _network_manager = manager
    return manager


def ResetAPIData() -> None:
    """Reset all API-related globals (useful for testing)."""
    global RequestSuccessful, FeedbackURL, LatestVersion, DownloadFolder, \
        UpdateDescription, _network_manager
    RequestSuccessful = False
    FeedbackURL = None
    LatestVersion = None
    DownloadFolder = None
    UpdateDescription = None
    _network_manager = None
