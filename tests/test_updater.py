"""
Tests for the updater module (src/updater.py).

Covers:
- Initial state
- ResetAPIData
- IsUpdateAvailable
- HandleAPIData
- RetreiveAPIData (smoke test — network-dep)
"""

import sys
import pytest
from unittest.mock import MagicMock, patch

import updater


# ─── Initial state ────────────────────────────────────────────────────────────

class TestInitialState:
    def test_constants_exist(self):
        """Module-level constants are defined."""
        assert updater.MacOSUpdateUrl.startswith("http")
        assert updater.WindowsUpdateUrl.startswith("http")
        assert isinstance(updater.AutoUpdateSupport, bool)
        assert updater.APIUrl.startswith("http")

    def test_globals_default_to_false_or_none(self):
        """API globals start in their 'no data' state."""
        assert updater.RequestSuccessful is False
        assert updater.LatestVersion is None
        assert updater.FeedbackURL is None
        assert updater.DownloadFolder is None
        assert updater.UpdateDescription is None


# ─── ResetAPIData ─────────────────────────────────────────────────────────────

class TestResetAPIData:
    def test_reset_clears_everything(self):
        """ResetAPIData restores initial state."""
        updater.RequestSuccessful = True
        updater.LatestVersion = "99.99.99"
        updater.FeedbackURL = "https://example.com"
        updater.DownloadFolder = "https://dl.example.com"
        updater.UpdateDescription = "Some desc"

        updater.ResetAPIData()

        assert updater.RequestSuccessful is False
        assert updater.LatestVersion is None
        assert updater.FeedbackURL is None
        assert updater.DownloadFolder is None
        assert updater.UpdateDescription is None


# ─── IsUpdateAvailable ────────────────────────────────────────────────────────

class TestIsUpdateAvailable:
    def test_returns_false_when_no_data(self):
        """Without API data, no update is available."""
        assert updater.IsUpdateAvailable("3.0.0") is False

    def test_returns_false_when_same_version(self):
        """Same version → no update."""
        updater.RequestSuccessful = True
        updater.LatestVersion = "3.0.0"
        assert updater.IsUpdateAvailable("3.0.0") is False

    def test_returns_false_when_newer_local(self):
        """Local version is newer → no update."""
        updater.RequestSuccessful = True
        updater.LatestVersion = "3.0.0"
        assert updater.IsUpdateAvailable("3.1.0") is False

    def test_returns_true_when_newer_remote(self):
        """Remote is newer → update available."""
        updater.RequestSuccessful = True
        updater.LatestVersion = "3.2.0"
        assert updater.IsUpdateAvailable("3.0.0") is True

    def test_force_update_wins(self):
        """force_update=True always returns True if RequestSuccessful."""
        updater.RequestSuccessful = True
        updater.LatestVersion = "1.0.0"
        assert updater.IsUpdateAvailable("3.0.0", force_update=True) is True

    def test_force_update_requires_request(self):
        """force_update=True still returns False if API never responded."""
        assert updater.IsUpdateAvailable("3.0.0", force_update=True) is False

    def test_version_parsing(self):
        """Handles semantic version strings correctly."""
        updater.RequestSuccessful = True
        updater.LatestVersion = "3.0.10"
        assert updater.IsUpdateAvailable("3.0.9") is True
        assert updater.IsUpdateAvailable("3.0.10") is False
        assert updater.IsUpdateAvailable("3.1.0") is False

    def test_pre_release_versions(self):
        """pre-release versions are handled by packaging.Version."""
        updater.RequestSuccessful = True
        updater.LatestVersion = "3.0.0"
        assert updater.IsUpdateAvailable("3.0.0b1") is True


# ─── HandleAPIData ────────────────────────────────────────────────────────────

class TestHandleAPIData:
    def _mock_reply(self, error, data=None):
        """Build a mock QNetworkReply."""
        reply = MagicMock()
        reply.error.return_value = error
        if data is not None:
            import json
            reply.readAll.return_value = json.dumps(data).encode("utf-8")
        return reply

    def test_success_sets_globals(self):
        """Successful reply populates all global fields."""
        payload = [{
            "feedback-url": "https://fb.example.com",
            "latest-version": "3.5.0",
            "download-folder": "https://dl.example.com/v3.5.0",
            "update-description": "Bug fixes and improvements",
        }]
        from PyQt5.QtNetwork import QNetworkReply
        reply = self._mock_reply(QNetworkReply.NoError, payload)

        updater.HandleAPIData(reply)

        assert updater.RequestSuccessful is True
        assert updater.FeedbackURL == "https://fb.example.com"
        assert updater.LatestVersion == "3.5.0"
        assert updater.DownloadFolder == "https://dl.example.com/v3.5.0"
        assert updater.UpdateDescription == "Bug fixes and improvements"

    def test_network_error_clears_flag(self):
        """Error response sets RequestSuccessful to False."""
        from PyQt5.QtNetwork import QNetworkReply
        reply = self._mock_reply(QNetworkReply.ConnectionRefusedError)

        updater.RequestSuccessful = True  # was previously successful
        updater.HandleAPIData(reply)

        assert updater.RequestSuccessful is False

    def test_partial_data_still_succeeds(self):
        """Partial JSON still populates available fields, others are None."""
        payload = [{"latest-version": "3.5.0"}]
        from PyQt5.QtNetwork import QNetworkReply
        reply = self._mock_reply(QNetworkReply.NoError, payload)

        updater.HandleAPIData(reply)

        assert updater.RequestSuccessful is True
        assert updater.LatestVersion == "3.5.0"
        assert updater.FeedbackURL is None  # not in payload
        assert updater.DownloadFolder is None
        assert updater.UpdateDescription is None


# ─── RetreiveAPIData ──────────────────────────────────────────────────────────

class TestRetreiveAPIData:
    def test_returns_network_access_manager(self, qapp):
        """RetreiveAPIData instantiates and returns a QNetworkAccessManager."""
        manager = updater.RetreiveAPIData()
        from PyQt5.QtNetwork import QNetworkAccessManager
        assert isinstance(manager, QNetworkAccessManager)

    def test_stores_reference_to_prevent_gc(self, qapp):
        """Internal _network_manager reference is kept."""
        prev = updater._network_manager
        updater.RetreiveAPIData()
        assert updater._network_manager is not None
