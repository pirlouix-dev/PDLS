"""
Tests for the storage module (src/storage.py).

Covers:
- StorageManager initialisation and defaults
- Dish list CRUD
- Backup creation, limits, and restore
- Window geometry persistence
- Version tracking
- Data erasure
"""

import time
import pytest
from unittest.mock import PropertyMock, patch

import storage


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def store():
    """Return a StorageManager with a clean, isolated QSettings backend."""
    # Use a unique product name so tests never collide with real app data
    mgr = storage.StorageManager(
        organization="PDLS_Test_Org",
        product="PDLS_Test_Product",
    )
    mgr.settings.clear()
    return mgr


SAMPLE_DISHES = [
    {"Name": "Pasta", "Type": 1, "Season": [1, 2, 3, 4], "Desc": "Italian"},
    {"Name": "Salad", "Type": 0, "Season": [2, 3], "Desc": ""},
    {"Name": "Steak", "Type": 1, "Season": [1, 2], "Desc": "Medium rare"},
]


# ─── Initialisation / defaults ───────────────────────────────────────────────

class TestInitializeDefaults:
    def test_sets_all_keys_when_empty(self, store):
        """All default keys are written when storage is fresh."""
        store.settings.clear()
        store.initialize_defaults("3.0.0")
        assert store.get_dish_list() == []
        assert store.get_backup() == {}
        assert store.get_last_version() == "3.0.0"
        assert store.get_expected_version() == "3.0.0"

    def test_preserves_existing_values(self, store):
        """Existing values are not overwritten by initialize_defaults."""
        store.settings.clear()
        store.settings.setValue("DishList", ["existing"])
        store.initialize_defaults("3.0.0")
        assert store.get_dish_list() == ["existing"]


# ─── Dish list ────────────────────────────────────────────────────────────────

class TestDishList:
    def test_default_is_empty(self, store):
        """Fresh storage returns an empty dish list."""
        store.settings.clear()
        assert store.get_dish_list() == []

    def test_save_and_retrieve(self, store):
        """Round-trip save/load."""
        store.save_dish_list(SAMPLE_DISHES)
        assert store.get_dish_list() == SAMPLE_DISHES

    def test_update_dish_list_creates_backup(self, store):
        """update_dish_list stores the old list as a backup before saving new."""
        store.save_dish_list([{"Name": "Old"}])
        store.update_dish_list([{"Name": "New"}])
        assert store.get_dish_list() == [{"Name": "New"}]
        backups = store.get_backup()
        assert len(backups) == 1
        # The backup should contain the old list
        one_backup = list(backups.values())[0]
        assert one_backup == [{"Name": "Old"}]


# ─── Backup ───────────────────────────────────────────────────────────────────

class TestBackup:
    def test_create_backup_stores_timestamped_copy(self, store):
        """create_backup adds an entry to the backup dict."""
        store.create_backup(SAMPLE_DISHES)
        backups = store.get_backup()
        assert len(backups) == 1
        ts = list(backups.keys())[0]
        assert isinstance(ts, (int, float))
        assert backups[ts] == SAMPLE_DISHES

    def test_backup_limits_entries(self, store):
        """At most MAX_BACKUPS entries are kept."""
        for i in range(storage.MAX_BACKUPS + 2):
            store.create_backup([{"Name": f"Dish {i}"}])
        backups = store.get_backup()
        assert len(backups) <= storage.MAX_BACKUPS

    def test_backup_evicts_oldest(self, store):
        """When over limit, the oldest timestamp is removed."""
        store.create_backup([{"Name": "Oldest"}])
        time.sleep(0.01)  # ensure distinct timestamps
        for i in range(storage.MAX_BACKUPS):
            store.create_backup([{"Name": f"New {i}"}])
        backups = store.get_backup()
        names = [v[0]["Name"] for v in backups.values()]
        assert "Oldest" not in names

    def test_restore_backup_returns_correct_list(self, store):
        """restore_backup retrieves the dish list for a given timestamp."""
        store.create_backup([{"Name": "BackupMeal"}])
        ts = list(store.get_backup().keys())[0]
        restored = store.restore_backup(ts)
        assert restored == [{"Name": "BackupMeal"}]

    def test_restore_nonexistent_backup(self, store):
        """Restoring a non-existent timestamp returns an empty list."""
        assert store.restore_backup(9999999999) == []


# ─── Window geometry ─────────────────────────────────────────────────────────

class TestWindowGeometry:
    def test_default_window_size(self, store):
        """Default window size is returned when no value is stored."""
        store.settings.clear()
        size = store.get_window_size()
        assert isinstance(size, tuple)
        assert len(size) == 2

    def test_save_and_get_window_size(self, store):
        """Round-trip window size."""
        store.save_window_size((1024, 768))
        assert store.get_window_size() == (1024, 768)

    def test_save_and_get_window_pos(self, store):
        """Round-trip window position."""
        store.save_window_pos((100, 50))
        assert store.get_window_pos() == (100, 50)


# ─── Version tracking ─────────────────────────────────────────────────────────

class TestVersionTracking:
    def test_last_version_default(self, store):
        """Fresh storage returns None for last version."""
        store.settings.clear()
        assert store.get_last_version() is None

    def test_set_and_get_last_version(self, store):
        """Round-trip last version."""
        store.set_last_version("3.0.0")
        assert store.get_last_version() == "3.0.0"

    def test_set_and_get_expected_version(self, store):
        """Round-trip expected version."""
        store.set_expected_version("3.1.0")
        assert store.get_expected_version() == "3.1.0"

    def test_is_version_update_expected_true(self, store):
        """Returns True when the app version is behind expected."""
        store.set_expected_version("3.5.0")
        assert store.is_version_update_expected("3.0.0") is True

    def test_is_version_update_expected_false(self, store):
        """Returns False when the app version matches expected."""
        store.set_expected_version("3.0.0")
        assert store.is_version_update_expected("3.0.0") is False

    def test_is_version_update_expected_no_expected(self, store):
        """Returns False when expected version has not been set."""
        store.settings.clear()
        assert store.is_version_update_expected("3.0.0") is False


# ─── Debug / erasure ──────────────────────────────────────────────────────────

class TestDataErasure:
    def test_erase_all_data_clears_dish_list_and_backup(self, store):
        """erase_all_data removes both DishList and DishBackup."""
        store.save_dish_list(SAMPLE_DISHES)
        store.create_backup(SAMPLE_DISHES)
        store.erase_all_data()
        assert store.get_dish_list() == []
        assert store.get_backup() == {}


# ─── Module-level constants ───────────────────────────────────────────────────

class TestConstants:
    def test_app_organization(self):
        assert storage.APP_ORGANIZATION == "Mathecorp"

    def test_app_product(self):
        assert storage.APP_PRODUCT == "PlatdelaSemaine"

    def test_max_backups(self):
        assert storage.MAX_BACKUPS == 5
