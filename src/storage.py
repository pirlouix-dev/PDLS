"""
Storage persistence layer for PDLS.

Extracts all QSettings-backed persistence from main.py:
- Dish list save/load/backup
- Settings persistence (window size, position, versions)
- Backup/restore operations
"""

import time
from PyQt5.QtCore import QSettings

APP_ORGANIZATION = "Mathecorp"
APP_PRODUCT = "PlatdelaSemaine"
MAX_BACKUPS = 5


class StorageManager:
    """Wraps QSettings for the PDLS application."""

    def __init__(self, organization=None, product=None):
        self.settings = QSettings(
            organization or APP_ORGANIZATION,
            product or APP_PRODUCT,
        )

    # ─── Dish list ────────────────────────────────────────────────────────────

    def get_dish_list(self):
        """Return the current dish list (list of dicts)."""
        return self.settings.value("DishList") or []

    def save_dish_list(self, dish_list):
        """Persist the dish list."""
        self.settings.setValue("DishList", dish_list)

    def update_dish_list(self, new_dish_list):
        """Save current dish list to backup, then persist the new one."""
        old = self.get_dish_list()
        self.create_backup(old)
        self.save_dish_list(new_dish_list)

    # ─── Backup ───────────────────────────────────────────────────────────────

    def get_backup(self):
        """Return the full backup dict {timestamp: dish_list, ...}."""
        return self.settings.value("DishBackup") or {}

    def save_backup(self, backup_dict):
        """Persist the backup dict."""
        self.settings.setValue("DishBackup", backup_dict)

    def create_backup(self, dish_list):
        """
        Create a timestamped backup of *dish_list*.
        Keeps at most MAX_BACKUPS entries, removing the oldest.
        """
        backups = self.get_backup()
        timestamp = int(time.time())
        while len(backups) >= MAX_BACKUPS:
            oldest = min(backups.keys())
            del backups[oldest]
        backups[timestamp] = dish_list
        self.save_backup(backups)

    def restore_backup(self, timestamp):
        """Restore dish list from a specific backup timestamp."""
        backups = self.get_backup()
        return backups.get(timestamp, [])

    # ─── Window geometry ─────────────────────────────────────────────────────

    def get_window_size(self):
        """Return (width, height) tuple, or default."""
        return self.settings.value("WindowSize") or (868, 750)

    def save_window_size(self, size):
        """Persist window size as (width, height)."""
        self.settings.setValue("WindowSize", size)

    def get_window_pos(self):
        """Return (x, y) tuple, or default."""
        return self.settings.value("WindowPos") or (0, 0)

    def save_window_pos(self, pos):
        """Persist window position as (x, y)."""
        self.settings.setValue("WindowPos", pos)

    # ─── Version tracking ────────────────────────────────────────────────────

    def get_last_version(self):
        """Return the last known app version string."""
        return self.settings.value("LastVersion")

    def set_last_version(self, version):
        """Persist the last known app version."""
        self.settings.setValue("LastVersion", version)

    def get_expected_version(self):
        """Return the expected (next) app version string."""
        return self.settings.value("ExpectedVersion")

    def set_expected_version(self, version):
        """Persist the expected app version."""
        self.settings.setValue("ExpectedVersion", version)

    def is_version_update_expected(self, app_version):
        """Return True if the current version is behind ExpectedVersion."""
        expected = self.get_expected_version()
        if expected is None:
            return False
        from packaging.version import Version
        return Version(app_version) < Version(expected)

    # ─── Initialisation ──────────────────────────────────────────────────────

    def initialize_defaults(self, app_version, window_size=None):
        """
        Set default values for any settings keys that haven't been persisted yet.
        Call once at startup.
        """
        if self.settings.value("DishList") is None:
            self.settings.setValue("DishList", [])
        if self.settings.value("DishBackup") is None:
            self.settings.setValue("DishBackup", {})
        if self.settings.value("LastVersion") is None:
            self.settings.setValue("LastVersion", app_version)
        if self.settings.value("ExpectedVersion") is None:
            self.settings.setValue("ExpectedVersion", app_version)
        if self.settings.value("WindowSize") is None:
            self.settings.setValue(
                "WindowSize",
                window_size or (868, 750),
            )
        if self.settings.value("WindowPos") is None:
            self.settings.setValue("WindowPos", (0, 0))

    # ─── Debug / dev tools ───────────────────────────────────────────────────

    def erase_all_data(self):
        """Clear dish list and backup (debug / dev)."""
        self.settings.setValue("DishList", [])
        self.settings.setValue("DishBackup", {})
