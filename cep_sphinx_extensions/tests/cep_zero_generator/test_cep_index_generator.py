import json

from cep_sphinx_extensions.cep_zero_generator import cep_index_generator, parser

from ..conftest import CEP_ROOT


def test_create_cep_json():
    ceps = [
        parser.CEP(CEP_ROOT / "cep-0008.rst"),
        parser.CEP(CEP_ROOT / "cep-0361.rst"),
        parser.CEP(CEP_ROOT / "cep-0719.rst"),
    ]

    out = json.loads(cep_index_generator.create_cep_json(ceps))

    assert out["8"]["url"] == "https://cfms-dev.github.io/ceps/cep-0008/"
    assert out["8"]["protocol_version"] is None
    assert out["361"]["protocol_version"] == [1, 2]
    assert out["719"]["protocol_version"] == [3]


def test_build_release_ceps_links_individual_versions_from_joint_release_cep():
    ceps = [
        parser.CEP(CEP_ROOT / "cep-0361.rst"),  # "1, 2" joint release CEP
        parser.CEP(CEP_ROOT / "cep-0719.rst"),  # "3"
    ]

    release_ceps = cep_index_generator.build_release_ceps(ceps)

    assert release_ceps == {1: 361, 2: 361, 3: 719}
