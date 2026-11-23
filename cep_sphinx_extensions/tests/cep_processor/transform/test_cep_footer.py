from cep_sphinx_extensions.cep_processor.transforms import cep_footer


def test_get_page_footer_context(monkeypatch):
    monkeypatch.setitem(
        cep_footer._LAST_MODIFIED_TIMES, "cep-0008", "2022-01-25 15:20:55"
    )
    out = cep_footer.get_page_footer_context("cep-0008")

    assert out["source_link"] == (
        "https://github.com/cfms-dev/ceps/blob/main/ceps/cep-0008.rst"
    )
    assert out["commit_link"] == (
        "https://github.com/cfms-dev/ceps/commits/main/ceps/cep-0008.rst"
    )
    assert out["last_modified"] == "2022-01-25 15:20:55"


def test_get_page_footer_context_no_history():
    out = cep_footer.get_page_footer_context("cep-not-found")

    # No git history -> only the static source link
    assert out == {
        "source_link": "https://github.com/cfms-dev/ceps/blob/main/ceps/cep-not-found.rst",
    }


def test_get_last_modified_timestamps():
    out = cep_footer._get_last_modified_timestamps()

    assert isinstance(out, dict)
