"""Code for handling object representation of a CEP."""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable, Sequence
from email.parser import HeaderParser
from pathlib import Path

from cep_sphinx_extensions.cep_zero_generator.constants import (
    ACTIVE_ALLOWED,
    HIDE_STATUS,
    SPECIAL_STATUSES,
    STATUS_ACTIVE,
    STATUS_PROVISIONAL,
    STATUS_VALUES,
    TYPE_STANDARDS,
    TYPE_VALUES,
)
from cep_sphinx_extensions.cep_zero_generator.errors import CEPError


@dataclasses.dataclass(order=True, frozen=True)
class _Author:
    """Represent CEP authors."""

    full_name: str  # The author's name.
    email: str  # The author's email address.


class CEP:
    """Representation of CEPs.

    Attributes:
        number : CEP number.
        title : CEP title.
        cep_type : The type of CEP.  Can only be one of the values from TYPE_VALUES.
        status : The CEP's status.  Value must be found in STATUS_VALUES.
        authors : A list of the authors.

    """

    # The required RFC 822 headers for all CEPs.
    required_headers = {"CEP", "Title", "Author", "Status", "Type", "Created"}

    def __init__(self, filename: Path):
        """Init object from an open CEP file object.

        cep_file is full text of the CEP file, filename is path of the CEP file, author_lookup is author exceptions file

        """
        self.filename: Path = filename

        # Parse the headers.
        cep_text = filename.read_text(encoding="utf-8")
        metadata = HeaderParser().parsestr(cep_text)
        required_header_misses = CEP.required_headers - set(metadata.keys())
        if required_header_misses:
            _raise_cep_error(
                self, f"CEP is missing required headers {required_header_misses}"
            )

        try:
            self.number = int(metadata["CEP"])
        except ValueError:
            _raise_cep_error(self, "CEP number isn't an integer")

        # Check CEP number matches filename
        if self.number != int(filename.stem[4:]):
            _raise_cep_error(
                self, f"CEP number does not match file name ({filename})", cep_num=True
            )

        # Title
        self.title: str = metadata["Title"]

        # Type
        self.cep_type: str = metadata["Type"]
        if self.cep_type not in TYPE_VALUES:
            _raise_cep_error(
                self, f"{self.cep_type} is not a valid Type value", cep_num=True
            )

        # Status
        status = metadata["Status"]
        if status in SPECIAL_STATUSES:
            status = SPECIAL_STATUSES[status]
        if status not in STATUS_VALUES:
            _raise_cep_error(
                self, f"{status} is not a valid Status value", cep_num=True
            )

        # Special case for Active CEPs.
        if status == STATUS_ACTIVE and self.cep_type not in ACTIVE_ALLOWED:
            msg = "Only Process and Informational CEPs may have an Active status"
            _raise_cep_error(self, msg, cep_num=True)

        # Special case for Provisional CEPs.
        if status == STATUS_PROVISIONAL and self.cep_type != TYPE_STANDARDS:
            msg = "Only Standards Track CEPs may have a Provisional status"
            _raise_cep_error(self, msg, cep_num=True)
        self.status: str = status

        # Parse CEP authors
        self.authors: list[_Author] = _parse_author(metadata["Author"])
        if not self.authors:
            raise _raise_cep_error(self, "no authors found", cep_num=True)

        # Topic (for sub-indices)
        _topic = metadata.get("Topic", "").lower().split(",")
        self.topic: set[str] = {
            topic for topic_raw in _topic if (topic := topic_raw.strip())
        }

        # Other headers
        self.created = metadata["Created"]
        self.discussions_to = metadata["Discussions-To"]
        self.python_version = metadata["Python-Version"]
        self.replaces = metadata["Replaces"]
        self.requires = metadata["Requires"]
        self.resolution = metadata["Resolution"]
        self.superseded_by = metadata["Superseded-By"]
        if metadata["Post-History"]:
            # Squash duplicate whitespace
            self.post_history = " ".join(metadata["Post-History"].split())
        else:
            self.post_history = None

    def __repr__(self) -> str:
        return f"<CEP {self.number:0>4} - {self.title}>"

    def __lt__(self, other: CEP) -> bool:
        return self.number < other.number

    def __eq__(self, other):
        return self.number == other.number

    @property
    def _author_names(self) -> Iterable[str]:
        """An iterator of the authors' full names."""
        return (author.full_name for author in self.authors)

    @property
    def shorthand(self) -> str:
        """Return reStructuredText tooltip for the CEP type and status."""
        type_code = self.cep_type[0].upper()
        if self.status in HIDE_STATUS:
            return f":abbr:`{type_code} ({self.cep_type}, {self.status})`"
        status_code = self.status[0].upper()
        return f":abbr:`{type_code}{status_code} ({self.cep_type}, {self.status})`"

    @property
    def details(self) -> dict[str, str | int]:
        """Return the line entry for the CEP."""
        return {
            "number": self.number,
            "title": self.title,
            # a tooltip representing the type and status
            "shorthand": self.shorthand,
            # the comma-separated list of authors
            "authors": ", ".join(self._author_names),
            # The targeted Python-Version (if present) or the empty string
            "python_version": self.python_version or "",
        }

    @property
    def full_details(self) -> dict[str, str | int | Sequence[str]]:
        """Returns all headers of the CEP as a dict."""
        return {
            "number": self.number,
            "title": self.title,
            "authors": ", ".join(self._author_names),
            "discussions_to": self.discussions_to,
            "status": self.status,
            "type": self.cep_type,
            "topic": ", ".join(sorted(self.topic)),
            "created": self.created,
            "python_version": self.python_version,
            "post_history": self.post_history,
            "resolution": self.resolution,
            "requires": self.requires,
            "replaces": self.replaces,
            "superseded_by": self.superseded_by,
            # extra non-header keys for use in ``ceps.json``
            "author_names": tuple(self._author_names),
            "url": f"https://ceps.cfms.dev/cep-{self.number:0>4}/",
        }


def _raise_cep_error(cep: CEP, msg: str, cep_num: bool = False) -> None:
    if cep_num:
        raise CEPError(msg, cep.filename, cep_number=cep.number)
    raise CEPError(msg, cep.filename)


jr_placeholder = ",Jr"


def _parse_author(data: str) -> list[_Author]:
    """Return a list of author names and emails."""

    author_list = []
    data = (
        data.replace("\n", " ")
        .replace(", Jr", jr_placeholder)
        .rstrip()
        .removesuffix(",")
    )
    for author_email in data.split(", "):
        if " <" in author_email:
            author, email = author_email.removesuffix(">").split(" <")
        else:
            author, email = author_email, ""

        author = author.strip()
        if author == "":
            raise ValueError("Name is empty!")

        author = author.replace(jr_placeholder, ", Jr")
        email = email.lower()
        author_list.append(_Author(author, email))
    return author_list
