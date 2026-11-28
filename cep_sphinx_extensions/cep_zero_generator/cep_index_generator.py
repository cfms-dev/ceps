"""Automatically create CEP 0 (the CEP index),

This file generates and writes the CEP index to disk, ready for later
processing by Sphinx. Firstly, we parse the individual CEP files, getting the
RFC2822 header, and parsing and then validating that metadata.

After collecting and validating all the CEP data, the creation of the index
itself is in three steps:

    1. Output static text.
    2. Format an entry for the CEP.
    3. Output the CEP (both by the category and numerical index).

We then add the newly created CEP 0 file to two Sphinx environment variables
to allow it to be processed as normal.

"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from cep_sphinx_extensions.cep_zero_generator import parser, subindices, writer
from cep_sphinx_extensions.cep_zero_generator.constants import SUBINDICES_BY_TOPIC
from release_management.serialize import (
    create_release_cycle,
    create_release_json,
    create_release_schedule_calendar,
)

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


def _parse_ceps(path: Path) -> list[parser.CEP]:
    # Read from root directory
    ceps: list[parser.CEP] = []

    for file_path in path.iterdir():
        if not file_path.is_file():
            continue  # Skip directories etc.
        if file_path.match("cep-0000*"):
            continue  # Skip pre-existing CEP 0 files
        if file_path.match("cep-????.rst"):
            cep = parser.CEP(path.joinpath(file_path).absolute())
            ceps.append(cep)

    return sorted(ceps)


def create_cep_json(ceps: list[parser.CEP]) -> str:
    return json.dumps({cep.number: cep.full_details for cep in ceps}, indent=1)


def write_ceps_json(ceps: list[parser.CEP], path: Path) -> None:
    # Create ceps.json
    json_ceps = create_cep_json(ceps)
    os.makedirs(os.path.join(path, "api"), exist_ok=True)
    Path(path, "api", "ceps.json").write_text(json_ceps, encoding="utf-8")


def build_release_ceps(ceps: list[parser.CEP]) -> dict[int, int]:
    """Map each protocol version to its release-schedule CEP number.

    Handles release CEPs that cover multiple versions jointly
    (e.g. "1, 2"), so individual versions also resolve.
    """
    release_ceps: dict[int, int] = {}

    for cep in ceps:
        if cep.protocol_version is not None and "release" in cep.topic:
            for version in cep.protocol_version:
                release_ceps[version] = cep.number

    return release_ceps


def create_cep_zero(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    ceps = _parse_ceps(Path(app.srcdir))

    release_ceps = build_release_ceps(ceps)

    numerical_index_text = writer.CEPZeroWriter(release_ceps).write_numerical_index(
        ceps
    )
    subindices.update_sphinx("numerical", numerical_index_text, docnames, env)

    cep0_text = writer.CEPZeroWriter(release_ceps).write_cep0(
        ceps, builder=env.settings["builder"]
    )
    cep0_path = subindices.update_sphinx("cep-0000", cep0_text, docnames, env)
    ceps.append(parser.CEP(cep0_path))

    subindices.generate_subindices(
        SUBINDICES_BY_TOPIC,
        ceps,
        release_ceps,
        docnames,
        env,
    )

    write_ceps_json(ceps, Path(app.outdir))

    release_cycle = create_release_cycle()
    app.outdir.joinpath("api/release-cycle.json").write_text(
        release_cycle, encoding="utf-8"
    )

    release_json = create_release_json()
    app.outdir.joinpath("api/cfms-releases.json").write_text(
        release_json, encoding="utf-8"
    )

    release_ical = create_release_schedule_calendar()
    app.outdir.joinpath("release-schedule.ics").write_text(
        release_ical, encoding="utf-8"
    )
