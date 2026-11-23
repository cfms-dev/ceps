import datetime as dt

from release_management import ReleaseInfo, serialize

FAKE_RELEASE = ReleaseInfo(
    stage="X.Y.Z final",
    state="actual",
    date=dt.date(2000, 1, 1),
    note="These characters need escaping: \\ , ; \n",
)


def test_create_release_calendar_has_calendar_metadata() -> None:
    # Act
    cal_lines = serialize.create_release_schedule_calendar().split("\r\n")

    # Assert

    # Check calendar metadata
    assert cal_lines[:5] == [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CFMS//CFMS release schedule//EN",
        "X-WR-CALDESC:CFMS releases schedule from https://ceps.cfms.dev",
        "X-WR-CALNAME:CFMS releases schedule",
    ]
    assert cal_lines[-2:] == [
        "END:VCALENDAR",
        "",
    ]


def test_create_release_calendar_first_event() -> None:
    # Act
    releases = [(9999, FAKE_RELEASE)]
    cal_lines = serialize.release_schedule_calendar_lines(releases)

    # Assert
    assert cal_lines[5] == "BEGIN:VEVENT"
    assert cal_lines[6].startswith("DTSTAMP:")
    assert cal_lines[6].endswith("Z")
    assert cal_lines[7] == "UID:cfms-X.Y.Zfinal@releases.cfms.dev"
    assert cal_lines[8] == "DTSTART;VALUE=DATE:20000101"
    assert cal_lines[9] == "SUMMARY:CFMS X.Y.Z final"
    assert cal_lines[10] == (
        "DESCRIPTION:Note: These characters need escaping: \\\\ \\, \\; \\n"
    )
    assert cal_lines[11] == "URL:https://ceps.cfms.dev/cep-9999/"
    assert cal_lines[12] == "END:VEVENT"
