import check_ceps  # NoQA: inserted into sys.modules in conftest.py
import pytest


@pytest.mark.parametrize(
    "line",
    [
        "CEP: 0",
        "CEP:      12",
    ],
)
def test_validate_cep_number(line: str):
    warnings = [warning for (_, warning) in check_ceps._validate_cep_number(line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "0",
        "CEP:12",
        "CEP 0",
        "CEP 12",
        "CEP:0",
    ],
)
def test_validate_cep_number_invalid_header(line: str):
    warnings = [warning for (_, warning) in check_ceps._validate_cep_number(line)]
    assert warnings == ["CEP must begin with the 'CEP:' header"], warnings


@pytest.mark.parametrize(
    ("cep_number", "expected_warnings"),
    [
        # valid entries
        ("0", set()),
        ("1", set()),
        ("12", set()),
        ("20", set()),
        ("101", set()),
        ("801", set()),
        ("3099", set()),
        ("9999", set()),
        # empty
        ("", {"not blank"}),
        # leading zeros
        ("01", {"leading zeros"}),
        ("001", {"leading zeros"}),
        ("0001", {"leading zeros"}),
        ("00001", {"leading zeros"}),
        # non-numeric
        ("a", {"non-numeric"}),
        ("123abc", {"non-numeric"}),
        ("0123A", {"leading zeros", "non-numeric"}),
        ("０", {"non-numeric"}),
        ("10１", {"non-numeric"}),
        ("999９", {"non-numeric"}),
        ("𝟎", {"non-numeric"}),
        ("𝟘", {"non-numeric"}),
        ("𝟏𝟚", {"non-numeric"}),
        ("𝟸𝟬", {"non-numeric"}),
        ("-1", {"non-numeric"}),
        ("+1", {"non-numeric"}),
        # out of bounds
        ("10000", {"range"}),
        ("54321", {"range"}),
        ("99999", {"range"}),
        ("32768", {"range"}),
    ],
    # call str() on each parameterised value in the test ID.
    ids=str,
)
def test_cep_num_checker(cep_number: str, expected_warnings: set):
    warnings = [
        warning for (_, warning) in check_ceps._cep_num(1, cep_number, "<Prefix>")
    ]

    found_warnings = set()
    cep_number = cep_number.strip()

    if "not blank" in expected_warnings:
        found_warnings.add("not blank")
        expected = f"<Prefix> must not be blank: {cep_number!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "leading zeros" in expected_warnings:
        found_warnings.add("leading zeros")
        expected = f"<Prefix> must not contain leading zeros: {cep_number!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "non-numeric" in expected_warnings:
        found_warnings.add("non-numeric")
        expected = f"<Prefix> must be numeric: {cep_number!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "range" in expected_warnings:
        found_warnings.add("range")
        expected = f"<Prefix> must be between 0 and 9999: {cep_number!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if expected_warnings == set():
        assert warnings == [], warnings

    assert found_warnings == expected_warnings
