from pathlib import Path

import pytest

from cep_sphinx_extensions.cep_zero_generator import parser, writer


def test_cep_zero_writer_emit_text_newline():
    cep0_writer = writer.CEPZeroWriter()
    cep0_writer.emit_text("my text 1")
    cep0_writer.emit_newline()
    cep0_writer.emit_text("my text 2")

    assert cep0_writer.output == ["my text 1", "", "my text 2"]


def test_cep_zero_writer_emit_title():
    cep0_writer = writer.CEPZeroWriter()
    cep0_writer.emit_title("My Title")
    cep0_writer.emit_subtitle("My Subtitle")

    assert cep0_writer.output == [
        "My Title",
        "========",
        "",
        "My Subtitle",
        "-----------",
        "",
    ]


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            "cep-9000.rst",
            {
                "Francis Fussyreverend": "one@example.com",
                "Javier Soulfulcommodore": "two@example.com",
            },
        ),
        (
            "cep-9001.rst",
            {"Francis Fussyreverend": "", "Javier Soulfulcommodore": ""},
        ),
    ],
)
def test_verify_email_addresses(test_input, expected):
    # Arrange
    ceps = [parser.CEP(Path(f"cep_sphinx_extensions/tests/ceps/{test_input}"))]

    # Act
    out = writer._verify_email_addresses(ceps)

    # Assert
    assert out == expected


def test_verify_email_addresses_multiple_emails():
    # Arrange
    ceps = [
        parser.CEP(Path("cep_sphinx_extensions/tests/ceps/cep-9000.rst")),
        parser.CEP(Path("cep_sphinx_extensions/tests/ceps/cep-9003.rst")),
    ]

    # Act
    out = writer._verify_email_addresses(ceps)

    # Assert: Francis has two emails combined, Javier's single email is not duplicated
    assert out == {
        "Francis Fussyreverend": "one@example.com, different@example.com",
        "Javier Soulfulcommodore": "two@example.com",
    }


def test_sort_authors():
    # Arrange
    authors_dict = {
        "Zebra, Zoë": "zoe@example.com",
        "lowercase, laurence": "laurence@example.com",
        "Aardvark, Alfred": "alfred@example.com",
    }

    # Act
    out = writer._sort_authors(authors_dict)

    # Assert
    assert out == ["Aardvark, Alfred", "lowercase, laurence", "Zebra, Zoë"]


@pytest.mark.parametrize(
    ("python_version", "expected"),
    [
        ("3.14", "     - :cep:`3.14 <745>`"),
        (
            "2.4, 2.5, 2.6",
            "     - :cep:`2.4 <320>`, :cep:`2.5 <356>`, :cep:`2.6 <361>`",
        ),
        ("2.4, 2.9", "     - :cep:`2.4 <320>`, 2.9"),
        ("1.5.2", "     - 1.5.2"),
        ("", "     - "),
    ],
)
def test_emit_cep_row_links_python_version_to_release_cep(
    python_version,
    expected,
):
    # Arrange
    release_ceps = {
        "2.4": 320,
        "2.5": 356,
        "2.6": 361,
        "3.14": 745,
    }
    cep0_writer = writer.CEPZeroWriter(release_ceps=release_ceps)

    # Act
    cep0_writer.emit_cep_row(
        shorthand="Active",
        number=999,
        title="Test CEP",
        authors="Test Author",
        python_version=python_version,
    )

    # Assert
    assert expected in cep0_writer.output
