from __future__ import annotations

import dataclasses
import datetime as dt
import json

from release_management import load_cfms_releases

TYPE_CHECKING = False
if TYPE_CHECKING:
    from release_management import ReleaseInfo, VersionMetadata

# Seven years captures the full lifecycle from prereleases to end-of-life
TODAY = dt.date.today()
SEVEN_YEARS_AGO = TODAY.replace(year=TODAY.year - 7)

# https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.11
CALENDAR_ESCAPE_TEXT = str.maketrans(
    {
        "\\": r"\\",
        ";": r"\;",
        ",": r"\,",
        "\n": r"\n",
    }
)


def create_release_json() -> str:
    cfms_releases = dataclasses.asdict(load_cfms_releases())
    return json.dumps(
        cfms_releases,
        indent=2,
        sort_keys=False,
        ensure_ascii=False,
        default=str,
    )


def create_release_cycle() -> str:
    metadata = load_cfms_releases().metadata
    all_versions = sorted(
        ((d.first_release, v) for v, d in metadata.items()), reverse=True
    )
    versions = [v for _date, v in all_versions if version_to_tuple(v) >= (2, 6)]
    release_cycle = {version: version_info(metadata[version]) for version in versions}
    rc_json = json.dumps(release_cycle, indent=2, sort_keys=False, ensure_ascii=False)
    return f"{rc_json}\n"


def version_to_tuple(version: str, /) -> tuple[int, ...]:
    return tuple(map(int, version.split(".")))


def version_info(metadata: VersionMetadata, /) -> dict[str, str | int]:
    end_of_life = metadata.end_of_life.isoformat()
    if metadata.status != "end-of-life":
        end_of_life = end_of_life.removesuffix("-01")
    return {
        "branch": metadata.branch,
        "cep": metadata.cep,
        "status": metadata.status,
        "first_release": metadata.first_release.isoformat(),
        "end_of_life": end_of_life,
        "release_manager": metadata.release_manager,
    }


def create_release_schedule_calendar() -> str:
    cfms_releases = load_cfms_releases()
    releases = []
    for version, all_releases in cfms_releases.releases.items():
        cep_number = cfms_releases.metadata[version].cep
        for release in all_releases:
            # Keep size reasonable by omitting releases older than 7 years
            if release.date < SEVEN_YEARS_AGO:
                continue
            releases.append((cep_number, release))
    releases.sort(key=lambda r: r[1].date)
    lines = release_schedule_calendar_lines(releases)
    return "\r\n".join(lines)


def release_schedule_calendar_lines(
    releases: list[tuple[int, ReleaseInfo]], /
) -> list[str]:
    dtstamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CFMS//CFMS release schedule//EN",
        "X-WR-CALDESC:CFMS releases schedule from https://ceps.cfms.dev",
        "X-WR-CALNAME:CFMS releases schedule",
    ]
    for cep_number, release in releases:
        normalised_stage = release.stage.replace(" ", "")
        normalised_stage = normalised_stage.translate(CALENDAR_ESCAPE_TEXT)
        if release.note:
            normalised_note = release.note.translate(CALENDAR_ESCAPE_TEXT)
            note = (f"DESCRIPTION:Note: {normalised_note}",)
        else:
            note = ()
        lines += (
            "BEGIN:VEVENT",
            f"DTSTAMP:{dtstamp}",
            f"UID:cfms-{normalised_stage}@releases.cfms.dev",
            f'DTSTART;VALUE=DATE:{release.date.strftime("%Y%m%d")}',
            f"SUMMARY:CFMS {release.stage}",
            *note,
            f"URL:https://ceps.cfms.dev/cep-{cep_number:04d}/",
            "END:VEVENT",
        )
    lines += (
        "END:VCALENDAR",
        "",
    )
    return lines
