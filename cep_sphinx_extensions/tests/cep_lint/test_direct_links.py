import check_ceps  # NoQA: inserted into sys.modules in conftest.py
import pytest


@pytest.mark.parametrize(
    "line",
    [
        "http://www.python.org/dev/ceps/cep-0000/",
        "https://www.python.org/dev/ceps/cep-0000/",
        "http://cfms-dev.github.io/ceps/cep-0000/",
        "https://cfms-dev.github.io/ceps/cep-0000/",
    ],
)
def test_check_direct_links_cep(line: str):
    warnings = [warning for (_, warning) in check_ceps.check_direct_links(1, line)]
    assert warnings == ["Use the :cep:`NNN` role to refer to CEPs"], warnings


@pytest.mark.parametrize(
    "line",
    [
        "http://www.rfc-editor.org/rfc/rfc2324",
        "https://www.rfc-editor.org/rfc/rfc2324",
        "http://datatracker.ietf.org/doc/html/rfc2324",
        "https://datatracker.ietf.org/doc/html/rfc2324",
    ],
)
def test_check_direct_links_rfc(line: str):
    warnings = [warning for (_, warning) in check_ceps.check_direct_links(1, line)]
    assert warnings == ["Use the :rfc:`NNN` role to refer to RFCs"], warnings
