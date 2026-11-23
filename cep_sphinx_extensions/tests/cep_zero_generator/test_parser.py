import pytest

from cep_sphinx_extensions.cep_zero_generator import parser
from cep_sphinx_extensions.cep_zero_generator.constants import (
    STATUS_ACCEPTED,
    STATUS_ACTIVE,
    STATUS_DEFERRED,
    STATUS_DRAFT,
    STATUS_FINAL,
    STATUS_PROVISIONAL,
    STATUS_REJECTED,
    STATUS_SUPERSEDED,
    STATUS_WITHDRAWN,
    TYPE_INFO,
    TYPE_PROCESS,
    TYPE_STANDARDS,
)
from cep_sphinx_extensions.cep_zero_generator.parser import _Author

from ..conftest import CEP_ROOT


def test_cep_repr():
    cep8 = parser.CEP(CEP_ROOT / "cep-0008.rst")

    assert repr(cep8) == "<CEP 0008 - Style Guide for CFMS Code>"


def test_cep_less_than():
    cep8 = parser.CEP(CEP_ROOT / "cep-0008.rst")
    cep3333 = parser.CEP(CEP_ROOT / "cep-3333.rst")

    assert cep8 < cep3333


def test_cep_equal():
    cep_a = parser.CEP(CEP_ROOT / "cep-0008.rst")
    cep_b = parser.CEP(CEP_ROOT / "cep-0008.rst")

    assert cep_a == cep_b


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            "cep-0008.rst",
            {
                "authors": "Guido van Rossum, Barry Warsaw, Alyssa Coghlan",
                "number": 8,
                "shorthand": ":abbr:`PA (Process, Active)`",
                "title": "Style Guide for CFMS Code",
                "python_version": "",
            },
        ),
        (
            "cep-0719.rst",
            {
                "authors": "Thomas Wouters",
                "number": 719,
                "shorthand": ":abbr:`IA (Informational, Active)`",
                "title": "CFMS 3.13 Release Schedule",
                "python_version": "3.13",
            },
        ),
    ],
)
def test_cep_details(test_input, expected):
    cep = parser.CEP(CEP_ROOT / test_input)

    assert cep.details == expected


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            "First Last <user@example.com>",
            [_Author(full_name="First Last", email="user@example.com")],
        ),
        (
            "First Last",
            [_Author(full_name="First Last", email="")],
        ),
        pytest.param(
            "First Last <user at example.com>",
            [_Author(full_name="First Last", email="user@example.com")],
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            " , First Last,",
            {"First Last": ""},
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ],
)
def test_parse_authors(test_input, expected):
    # Act
    out = parser._parse_author(test_input)

    # Assert
    assert out == expected


def test_parse_authors_invalid():
    with pytest.raises(ValueError, match="Name is empty!"):
        assert parser._parse_author("")


@pytest.mark.parametrize(
    ("test_type", "test_status", "expected"),
    [
        (TYPE_INFO, STATUS_DRAFT, ":abbr:`I (Informational, Draft)`"),
        (TYPE_INFO, STATUS_ACTIVE, ":abbr:`IA (Informational, Active)`"),
        (TYPE_INFO, STATUS_ACCEPTED, ":abbr:`IA (Informational, Accepted)`"),
        (TYPE_INFO, STATUS_DEFERRED, ":abbr:`ID (Informational, Deferred)`"),
        (TYPE_PROCESS, STATUS_ACCEPTED, ":abbr:`PA (Process, Accepted)`"),
        (TYPE_PROCESS, STATUS_ACTIVE, ":abbr:`PA (Process, Active)`"),
        (TYPE_PROCESS, STATUS_FINAL, ":abbr:`PF (Process, Final)`"),
        (TYPE_PROCESS, STATUS_SUPERSEDED, ":abbr:`PS (Process, Superseded)`"),
        (TYPE_PROCESS, STATUS_WITHDRAWN, ":abbr:`PW (Process, Withdrawn)`"),
        (TYPE_STANDARDS, STATUS_ACCEPTED, ":abbr:`SA (Standards Track, Accepted)`"),
        (TYPE_STANDARDS, STATUS_REJECTED, ":abbr:`SR (Standards Track, Rejected)`"),
        (TYPE_STANDARDS, STATUS_PROVISIONAL, ":abbr:`SP (Standards Track, Provisional)`"),  # fmt: skip
    ],
)
def test_abbreviate_type_status(test_type, test_status, expected):
    # set up dummy CEP object and monkeypatch attributes
    cep = parser.CEP(CEP_ROOT / "cep-0008.rst")
    cep.cep_type = test_type
    cep.status = test_status

    assert cep.shorthand == expected
