"""
Data models for Datasets API responses.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Literal


@dataclass
class DatasetInfo:
    """Dataset info returned by list()."""

    id: str
    name: str
    size: int = 0  # record count


@dataclass
class DatasetField:
    """Field metadata within a dataset."""

    type: str  # "text", "number", "url", "array", "object", "boolean"
    active: bool = True
    required: bool = False
    description: Optional[str] = None


@dataclass
class DatasetMetadata:
    """Dataset metadata returned by get_metadata()."""

    id: str
    fields: Dict[str, DatasetField] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetMetadata":
        """Create from API response."""
        fields = {}
        for name, field_data in data.get("fields", {}).items():
            if isinstance(field_data, dict):
                fields[name] = DatasetField(
                    type=field_data.get("type", "text"),
                    active=field_data.get("active", True),
                    required=field_data.get("required", False),
                    description=field_data.get("description"),
                )
        return cls(id=data.get("id", ""), fields=fields)


@dataclass
class SnapshotStatus:
    """Snapshot status returned by get_status()."""

    id: str
    status: Literal["scheduled", "building", "ready", "failed"]
    dataset_id: Optional[str] = None
    dataset_size: Optional[int] = None  # records in snapshot
    file_size: Optional[int] = None  # bytes
    cost: Optional[float] = None
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SnapshotStatus":
        """Create from API response."""
        return cls(
            id=data.get("id", data.get("snapshot_id", "")),
            status=data.get("status", "scheduled"),
            dataset_id=data.get("dataset_id"),
            dataset_size=data.get("dataset_size"),
            file_size=data.get("file_size"),
            cost=data.get("cost"),
            error=data.get("error", data.get("error_message")),
        )
