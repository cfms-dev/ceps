from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

TYPE_CHECKING = False
if TYPE_CHECKING:
    import datetime as dt
    from typing import Literal, TypeAlias

    ReleaseState: TypeAlias = Literal["actual", "expected"]
    ReleaseSchedules: TypeAlias = dict[tuple[str, ReleaseState], list["ReleaseInfo"]]
    VersionStatus: TypeAlias = Literal[
        "feature", "prerelease", "bugfix", "security", "end-of-life"
    ]

RELEASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = RELEASE_DIR.parent
CEP_ROOT = ROOT_DIR / "ceps"

dc_kw = {"kw_only": True, "slots": True} if sys.version_info[:2] >= (3, 10) else {}


@dataclass(frozen=True, **dc_kw)
class CFMSReleases:
    metadata: dict[str, VersionMetadata]
    releases: dict[str, list[ReleaseInfo]]


@dataclass(frozen=True, **dc_kw)
class VersionMetadata:
    """Metadata for a given version (MAJOR.MINOR)."""

    cep: int
    status: VersionStatus
    branch: str
    release_manager: str
    start_of_development: dt.date
    feature_freeze: dt.date
    first_release: dt.date
    end_of_bugfix: dt.date  # a.k.a. security mode or source-only releases
    end_of_life: dt.date

    @classmethod
    def from_toml(cls, data: dict[str, int | str | dt.date]):
        return cls(**{k.replace("-", "_"): v for k, v in data.items()})


@dataclass(frozen=True, **dc_kw)
class ReleaseInfo:
    """Information about a release."""

    stage: str
    state: ReleaseState
    date: dt.date
    note: str = ""  # optional note / comment, displayed in the schedule

    @property
    def schedule_bullet(self):
        """Return a formatted bullet point for the schedule list."""
        return f"- {self.stage}: {self.date:%A, %Y-%m-%d}"


def load_cfms_releases() -> CFMSReleases:
    with open(RELEASE_DIR / "cfms-releases.toml", "rb") as f:
        cfms_releases = tomllib.load(f)
    all_metadata = {
        v: VersionMetadata.from_toml(metadata)
        for v, metadata in cfms_releases.get("metadata", {}).items()
    }
    all_releases = {
        v: [ReleaseInfo(**r) for r in releases]
        for v, releases in cfms_releases.get("release", {}).items()
    }
    return CFMSReleases(metadata=all_metadata, releases=all_releases)
