"""
Tests for dataset snapshot error reporting (Issue 2 — devdocs/scoped/2/).

A failed snapshot must expose the API failure reason (or, when no recognized
reason key is present, the raw status response as a fallback) plus the
snapshot_id — never the unhelpful literal "Snapshot failed: None".

Mocked at the boundary (get_status is patched) so no network is involved.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from brightdata.datasets.base import BaseDataset, DatasetError
from brightdata.datasets.models import SnapshotStatus


class _Dataset(BaseDataset):
    """Concrete dataset for tests (leading underscore → not collected by pytest)."""

    DATASET_ID = "gd_test"
    NAME = "test"


def _dataset() -> _Dataset:
    # The engine is never used in these tests (get_status is patched), but
    # BaseDataset stores it at construction.
    return _Dataset(engine=MagicMock())


class TestSnapshotStatusParsing:
    def test_reason_under_non_error_key_is_captured(self):
        data = {"status": "failed", "snapshot_id": "s1", "message": "quota exceeded"}
        status = SnapshotStatus.from_dict(data)
        assert status.status == "failed"
        assert status.error == "quota exceeded"
        assert status.raw == data  # full response retained, not just 7 named fields

    def test_failure_reason_key_is_captured(self):
        data = {"status": "failed", "id": "s2", "failure_reason": "bad filter"}
        status = SnapshotStatus.from_dict(data)
        assert status.error == "bad filter"

    def test_no_recognized_reason_leaves_error_none_but_keeps_raw(self):
        data = {"status": "failed", "id": "s3", "weird_key": "boom"}
        status = SnapshotStatus.from_dict(data)
        assert status.error is None
        assert status.raw == data  # raw is the fallback the download() message uses


class TestDownloadFailureMessage:
    async def test_failed_snapshot_surfaces_reason_and_id(self):
        ds = _dataset()
        ds.get_status = AsyncMock(
            return_value=SnapshotStatus.from_dict(
                {"status": "failed", "snapshot_id": "s1", "message": "quota exceeded"}
            )
        )
        with pytest.raises(DatasetError) as excinfo:
            await ds.download("s1")
        msg = str(excinfo.value)
        assert "quota exceeded" in msg
        assert "s1" in msg
        assert "None" not in msg  # the original bug must not reappear

    async def test_failed_snapshot_without_reason_falls_back_to_raw(self):
        ds = _dataset()
        raw = {"status": "failed", "snapshot_id": "s9", "weird_key": "boom"}
        ds.get_status = AsyncMock(return_value=SnapshotStatus.from_dict(raw))
        with pytest.raises(DatasetError) as excinfo:
            await ds.download("s9")
        msg = str(excinfo.value)
        assert "s9" in msg
        assert "boom" in msg  # raw response surfaced instead of None
        assert "Snapshot failed: None" not in msg

    async def test_timeout_message_includes_id_and_status(self):
        ds = _dataset()
        ds.get_status = AsyncMock(
            return_value=SnapshotStatus.from_dict({"status": "building", "snapshot_id": "s5"})
        )
        # timeout=-1 makes the timeout branch fire on the first poll (no sleep, no network).
        with pytest.raises(TimeoutError) as excinfo:
            await ds.download("s5", timeout=-1)
        msg = str(excinfo.value)
        assert "s5" in msg
        assert "building" in msg
