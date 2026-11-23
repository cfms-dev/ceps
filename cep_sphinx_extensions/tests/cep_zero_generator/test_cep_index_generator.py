from cep_sphinx_extensions.cep_zero_generator import cep_index_generator, parser

from ..conftest import CEP_ROOT


def test_create_cep_json():
    ceps = [parser.CEP(CEP_ROOT / "cep-0008.rst")]

    out = cep_index_generator.create_cep_json(ceps)

    assert '"url": "https://ceps.cfms.dev/cep-0008/"' in out


def test_build_release_ceps_links_individual_versions_from_joint_release_cep():
    ceps = [
        parser.CEP(CEP_ROOT / "cep-0361.rst"),  # "2.6, 3.0" joint release CEP
    ]

    release_ceps = cep_index_generator.build_release_ceps(ceps)

    assert release_ceps == {"2.6": 361, "3.0": 361}
