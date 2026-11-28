from pathlib import Path

import check_ceps  # NoQA: inserted into sys.modules in conftest.py

from ..conftest import CEP_ROOT

CEP_9002 = Path(__file__).parent.parent / "ceps" / "cep-9002.rst"


def test_with_fake_cep():
    content = CEP_9002.read_text(encoding="utf-8").splitlines()
    warnings = list(check_ceps.check_ceps(CEP_9002, content))
    assert warnings == [
        (1, "CEP must begin with the 'CEP:' header"),
        (6, "Must not have invalid header: Version"),
        (9, "Must not have duplicate header: Sponsor "),
        (10, "Must not have invalid header: Horse-Guards"),
        (15, "Must not have invalid header: Content-Type"),
        (1, "Must have required header: CEP"),
        (1, "Must have required header: Type"),
        (
            1,
            "Headers must be in CEP 12 order. Correct order: Title, Author, "
            "Sponsor, BDFL-Delegate, Discussions-To, Status, Topic, Requires, "
            "Created, Protocol-Version, Post-History, Resolution",
        ),
        (4, "Author continuation lines must end with a comma"),
        (5, "Author line must not be over-indented"),
        (7, "Protocol-Version must be a positive integer: 4.0"),
        (8, "Sponsor entries must begin with a valid 'Name': ''"),
        (9, "Sponsor entries must begin with a valid 'Name': ''"),
        (11, "Created must be a 'DD-mmm-YYYY' date: '1-Jan-1989'"),
        (12, "Delegate entries must begin with a valid 'Name': 'Barry!'"),
        (13, "Status must be a valid CEP status"),
        (14, "Topic must not contain duplicates"),
        (14, "Topic must be properly capitalised (Title Case)"),
        (14, "Topic must be for a valid sub-index"),
        (14, "Topic must be sorted lexicographically"),
        (16, "CEP references must be separated by comma-spaces (', ')"),
        (17, "Discussions-To must be a valid thread URL, mailing list, or 'Pending'"),
        (18, "Post-History must be a 'DD-mmm-YYYY' date: '2-Feb-2000'"),
        (18, "Post-History must be a valid thread URL"),
        (19, "Post-History must be a 'DD-mmm-YYYY' date: '3-Mar-2001'"),
        (19, "Post-History must be a valid thread URL"),
        (20, "Resolution must be a valid thread URL"),
        (23, "Use the :cep:`NNN` role to refer to CEPs"),
    ]


def test_skip_direct_cep_link_check():
    filename = CEP_ROOT / "cep-0009.rst"  # in SKIP_DIRECT_CEP_LINK_CHECK
    content = filename.read_text(encoding="utf-8").splitlines()
    warnings = list(check_ceps.check_ceps(filename, content))
    assert warnings == []
