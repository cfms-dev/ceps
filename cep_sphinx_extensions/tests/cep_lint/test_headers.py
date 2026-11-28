import check_ceps  # NoQA: inserted into sys.modules in conftest.py
import pytest


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        # capitalisation
        ("Header:", "Header"),
        ("header:", "header"),
        ("hEADER:", "hEADER"),
        ("hEaDeR:", "hEaDeR"),
        # trailing spaces
        ("Header: ", "Header"),
        ("Header:  ", "Header"),
        ("Header:   \t", "Header"),
        # trailing content
        ("Header: Text", "Header"),
        ("Header: 123", "Header"),
        ("Header: !", "Header"),
        # separators
        ("Hyphenated-Header:", "Hyphenated-Header"),
    ],
)
def test_header_pattern(test_input, expected):
    assert check_ceps.HEADER_PATTERN.match(test_input)[1] == expected


@pytest.mark.parametrize(
    "test_input",
    [
        # trailing content
        "Header:Text",
        "Header:123",
        "Header:!",
        # colon position
        "Header",
        "Header : ",
        "Header :",
        "SemiColonHeader;",
        # separators
        "Underscored_Header:",
        "Spaced Header:",
        "Plus+Header:",
    ],
)
def test_header_pattern_no_match(test_input):
    assert check_ceps.HEADER_PATTERN.match(test_input) is None


def test_validate_required_headers():
    found_headers = dict.fromkeys(
        ("CEP", "Title", "Author", "Status", "Type", "Created")
    )
    warnings = [
        warning for (_, warning) in check_ceps._validate_required_headers(found_headers)
    ]
    assert warnings == [], warnings


def test_validate_required_headers_missing():
    found_headers = dict.fromkeys(("CEP", "Title", "Author", "Type"))
    warnings = [
        warning for (_, warning) in check_ceps._validate_required_headers(found_headers)
    ]
    assert warnings == [
        "Must have required header: Status",
        "Must have required header: Created",
    ], warnings


def test_validate_required_headers_order():
    found_headers = dict.fromkeys(
        ("CEP", "Title", "Sponsor", "Author", "Type", "Status", "Replaces", "Created")
    )
    warnings = [
        warning for (_, warning) in check_ceps._validate_required_headers(found_headers)
    ]
    assert warnings == [
        "Headers must be in CEP 12 order. Correct order: CEP, Title, Author, Sponsor, Status, Type, Created, Replaces"
    ], warnings


@pytest.mark.parametrize(
    "line",
    [
        "!",
        "The Zen of Python",
        "A title that is exactly 79 characters long, but shorter than 80 characters long",
    ],
)
def test_validate_title(line: str):
    warnings = [warning for (_, warning) in check_ceps._validate_title(1, line)]
    assert warnings == [], warnings


def test_validate_title_blank():
    warnings = [warning for (_, warning) in check_ceps._validate_title(1, "-" * 80)]
    assert warnings == ["CEP title must be less than 80 characters"], warnings


def test_validate_title_too_long():
    warnings = [warning for (_, warning) in check_ceps._validate_title(1, "")]
    assert warnings == ["CEP must have a title"], warnings


@pytest.mark.parametrize(
    "line",
    [
        "Accepted",
        "Active",
        "April Fool!",
        "Deferred",
        "Draft",
        "Final",
        "Provisional",
        "Rejected",
        "Superseded",
        "Withdrawn",
    ],
)
def test_validate_status_valid(line: str):
    warnings = [warning for (_, warning) in check_ceps._validate_status(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "Standards Track",
        "Informational",
        "Process",
        "accepted",
        "active",
        "april fool!",
        "deferred",
        "draft",
        "final",
        "provisional",
        "rejected",
        "superseded",
        "withdrawn",
    ],
)
def test_validate_status_invalid(line: str):
    warnings = [warning for (_, warning) in check_ceps._validate_status(1, line)]
    assert warnings == ["Status must be a valid CEP status"], warnings


@pytest.mark.parametrize(
    "line",
    [
        "Standards Track",
        "Informational",
        "Process",
    ],
)
def test_validate_type_valid(line: str):
    warnings = [warning for (_, warning) in check_ceps._validate_type(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "standards track",
        "informational",
        "process",
        "Accepted",
        "Active",
        "April Fool!",
        "Deferred",
        "Draft",
        "Final",
        "Provisional",
        "Rejected",
        "Superseded",
        "Withdrawn",
    ],
)
def test_validate_type_invalid(line: str):
    warnings = [warning for (_, warning) in check_ceps._validate_type(1, line)]
    assert warnings == ["Type must be a valid CEP type"], warnings


@pytest.mark.parametrize(
    ("line", "expected_warnings"),
    [
        # valid entries
        ("Governance", set()),
        ("Packaging", set()),
        ("Typing", set()),
        ("Release", set()),
        ("Governance, Packaging", set()),
        ("Packaging, Typing", set()),
        # duplicates
        ("Governance, Governance", {"duplicates"}),
        ("Release, Release", {"duplicates"}),
        ("Packaging, Packaging", {"duplicates"}),
        ("Spam, Spam", {"duplicates", "valid"}),
        ("lobster, lobster", {"duplicates", "capitalisation", "valid"}),
        ("governance, governance", {"duplicates", "capitalisation"}),
        # capitalisation
        ("governance", {"capitalisation"}),
        ("packaging", {"capitalisation"}),
        ("typing", {"capitalisation"}),
        ("release", {"capitalisation"}),
        ("Governance, release", {"capitalisation"}),
        # validity
        ("Spam", {"valid"}),
        ("lobster", {"capitalisation", "valid"}),
        # sorted
        ("Packaging, Governance", {"sorted"}),
        ("Typing, Release", {"sorted"}),
        ("Release, Governance", {"sorted"}),
        ("spam, packaging", {"capitalisation", "valid", "sorted"}),
    ],
    # call str() on each parameterised value in the test ID.
    ids=str,
)
def test_validate_topic(line: str, expected_warnings: set):
    warnings = [warning for (_, warning) in check_ceps._validate_topic(1, line)]

    found_warnings = set()

    if "duplicates" in expected_warnings:
        found_warnings.add("duplicates")
        expected = "Topic must not contain duplicates"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "capitalisation" in expected_warnings:
        found_warnings.add("capitalisation")
        expected = "Topic must be properly capitalised (Title Case)"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "valid" in expected_warnings:
        found_warnings.add("valid")
        expected = "Topic must be for a valid sub-index"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "sorted" in expected_warnings:
        found_warnings.add("sorted")
        expected = "Topic must be sorted lexicographically"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if expected_warnings == set():
        assert warnings == [], warnings

    assert found_warnings == expected_warnings


@pytest.mark.parametrize(
    "line",
    [
        "0, 1, 8, 12, 20,",
        "101, 801,",
        "3099, 9999",
    ],
)
def test_validate_cep_references(line: str):
    warnings = [
        warning for (_, warning) in check_ceps._validate_cep_references(1, line)
    ]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "0,1,8, 12, 20,",
        "101,801,",
        "3099, 9998,9999",
    ],
)
def test_validate_cep_references_separators(line: str):
    warnings = [
        warning for (_, warning) in check_ceps._validate_cep_references(1, line)
    ]
    assert warnings == [
        "CEP references must be separated by comma-spaces (', ')"
    ], warnings


@pytest.mark.parametrize(
    ("line", "expected_warnings"),
    [
        # valid entries
        ("1", set()),
        ("2", set()),
        ("10", set()),
        ("999", set()),
        ("1, 2", set()),
        ("31, 32", set()),
        # non-integers / empty / negative / signed / dotted / missing space / non-ASCII
        ("", {"positive_int"}),
        ("-1", {"positive_int"}),
        ("+1", {"positive_int"}),
        ("1.0", {"positive_int"}),
        ("3.13", {"positive_int"}),
        ("4.0", {"positive_int"}),
        ("31,32", {"positive_int"}),
        ("a", {"positive_int"}),
        ("1x", {"positive_int"}),
        ("١", {"positive_int"}),
        # zero
        ("0", {"positive_int"}),
        # leading zeros
        ("01", {"leading_zeros"}),
        ("007", {"leading_zeros"}),
        ("00", {"leading_zeros", "positive_int"}),
    ],
    # call str() on each parameterised value in the test ID.
    ids=str,
)
def test_validate_protocol_version(line: str, expected_warnings: set):
    warnings = [
        warning for (_, warning) in check_ceps._validate_protocol_version(1, line)
    ]

    found_warnings = set()

    if "positive_int" in expected_warnings:
        found_warnings.add("positive_int")
        expected = f"Protocol-Version must be a positive integer: {line}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "leading_zeros" in expected_warnings:
        found_warnings.add("leading_zeros")
        expected = f"Protocol-Version must not have leading zeros: {line}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if expected_warnings == set():
        assert warnings == [], warnings

    assert found_warnings == expected_warnings


@pytest.mark.parametrize(
    ("line", "expected_warnings"),
    [
        (
            "31, 4.0",
            ["Protocol-Version must be a positive integer: 4.0"],
        ),
        (
            "31, 02",
            ["Protocol-Version must not have leading zeros: 02"],
        ),
        (
            "31, 0",
            ["Protocol-Version must be a positive integer: 0"],
        ),
        (
            "31, ",
            ["Protocol-Version must be a positive integer: "],
        ),
    ],
)
def test_validate_protocol_version_multiple(line: str, expected_warnings: list):
    warnings = [
        warning for (_, warning) in check_ceps._validate_protocol_version(1, line)
    ]
    assert warnings == expected_warnings, warnings
