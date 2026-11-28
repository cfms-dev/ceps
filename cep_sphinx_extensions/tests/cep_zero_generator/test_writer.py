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
    ("protocol_version", "expected"),
    [
        ("1", "     - :cep:`1 <361>`"),
        ("1, 2, 3", "     - :cep:`1 <361>`, :cep:`2 <361>`, :cep:`3 <719>`"),
        ("1, 4", "     - :cep:`1 <361>`, 4"),
        ("4", "     - 4"),
        ("", "     - "),
    ],
)
def test_emit_cep_row_links_protocol_version_to_release_cep(
    protocol_version,
    expected,
):
    # Arrange
    release_ceps = {
        1: 361,
        2: 361,
        3: 719,
    }
    cep0_writer = writer.CEPZeroWriter(release_ceps=release_ceps)

    # Act
    cep0_writer.emit_cep_row(
        shorthand="Active",
        number=999,
        title="Test CEP",
        authors="Test Author",
        protocol_version=protocol_version,
    )

    # Assert
    assert expected in cep0_writer.output


def test_emit_cep_row_omits_protocol_version_when_none():
    cep0_writer = writer.CEPZeroWriter(release_ceps={1: 361})

    cep0_writer.emit_cep_row(
        shorthand="Active",
        number=999,
        title="Test CEP",
        authors="Test Author",
        protocol_version=None,
    )

    assert cep0_writer.output == [
        "   * - Active",
        "     - :cep:`999 <999>`",
        "     - :cep:`Test CEP <999>`",
        "     - Test Author",
    ]
