"""Code to handle the output of CEP 0."""

from __future__ import annotations

import unicodedata
from typing import TYPE_CHECKING

from cep_sphinx_extensions.cep_processor.transforms.cep_headers import (
    ABBREVIATED_STATUSES,
    ABBREVIATED_TYPES,
)
from cep_sphinx_extensions.cep_zero_generator.constants import (
    DEAD_STATUSES,
    STATUS_ACCEPTED,
    STATUS_ACTIVE,
    STATUS_DEFERRED,
    STATUS_DRAFT,
    STATUS_FINAL,
    STATUS_PROVISIONAL,
    STATUS_REJECTED,
    STATUS_VALUES,
    STATUS_WITHDRAWN,
    SUBINDICES_BY_TOPIC,
    TYPE_INFO,
    TYPE_PROCESS,
    TYPE_VALUES,
)
from cep_sphinx_extensions.cep_zero_generator.errors import CEPError

if TYPE_CHECKING:
    from cep_sphinx_extensions.cep_zero_generator.parser import CEP

HEADER = """\
CEP: 0
Title: Index of CFMS Enhancement Proposals (CEPs)
Author: The CEP Editors
Status: Active
Type: Informational
Content-Type: text/x-rst
Created: 13-Jul-2000
"""

INTRO = """\
This CEP contains the index of all CFMS Enhancement Proposals,
known as CEPs.  CEP numbers are :cep:`assigned <1#cep-editors>`
by the CEP editors, and once assigned are never changed.  The
`version control history <https://github.com/cfms-dev/ceps>`_ of
the CEP texts represent their historical record.
"""


class CEPZeroWriter:
    # This is a list of reserved CEP numbers.  Reservations are not to be used for
    # the normal CEP number allocation process - just give out the next available
    # CEP number.  These are for "special" numbers that may be used for semantic,
    # humorous, or other such reasons.
    #
    # CEP numbers may only be reserved with the approval of a CEP editor.  Fields
    # here are the CEP number being reserved and the claimants for the CEP.
    # Although the output is sorted when CEP 0 is generated, please keep this list
    # sorted as well.
    RESERVED: dict[int, str] = {}

    def __init__(self, release_ceps: dict[int, int] | None = None):
        self.output: list[str] = []
        self.release_ceps = release_ceps or {}

    def emit_text(self, content: str) -> None:
        # Appends content argument to the output list
        self.output.append(content)

    def emit_newline(self) -> None:
        self.output.append("")

    def emit_author_table_separator(self, max_name_len: int) -> None:
        author_table_separator = "=" * max_name_len + "  " + "=" * len("email address")
        self.output.append(author_table_separator)

    def emit_cep_row(
        self,
        *,
        shorthand: str,
        number: int,
        title: str,
        authors: str,
        protocol_version: str | None = None,
    ) -> None:
        self.emit_text(f"   * - {shorthand}")
        self.emit_text(f"     - :cep:`{number} <{number}>`")
        self.emit_text(f"     - :cep:`{title.replace('`', '')} <{number}>`")
        self.emit_text(f"     - {authors}")
        if protocol_version is not None:
            if protocol_version == "":
                self.emit_text("     - ")
            else:
                linked_versions = []
                for raw_version in map(str.strip, protocol_version.split(",")):
                    version = int(raw_version)
                    release_cep = self.release_ceps.get(version)
                    if release_cep is not None:
                        linked_versions.append(f":cep:`{version} <{release_cep}>`")
                    else:
                        linked_versions.append(str(version))
                self.emit_text(f"     - {', '.join(linked_versions)}")

    def emit_column_headers(self, *, include_version=True) -> None:
        """Output the column headers for the CEP indices."""
        self.emit_text(".. list-table::")
        self.emit_text("   :header-rows: 1")
        self.emit_text("   :widths: auto")
        self.emit_text("   :class: cep-zero-table")
        self.emit_newline()
        self.emit_text("   * - ")
        self.emit_text("     - CEP")
        self.emit_text("     - Title")
        self.emit_text("     - Authors")
        if include_version:
            self.emit_text("     - ")  # for Protocol-Version

    def emit_title(self, text: str, *, symbol: str = "=") -> None:
        self.output.append(text)
        self.output.append(symbol * len(text))
        self.emit_newline()

    def emit_subtitle(self, text: str) -> None:
        self.emit_title(text, symbol="-")

    def emit_table(self, ceps: list[CEP]) -> None:
        include_version = any(cep.details["protocol_version"] != "" for cep in ceps)
        self.emit_column_headers(include_version=include_version)
        for cep in ceps:
            details = cep.details
            if not include_version:
                details.pop("protocol_version")
            self.emit_cep_row(**details)
        # list-table must have at least one body row
        if len(ceps) == 0:
            self.emit_text("   * -")
            self.emit_text("     -")
            self.emit_text("     -")
            self.emit_text("     -")

    def emit_cep_category(self, category: str, ceps: list[CEP]) -> None:
        self.emit_subtitle(category)
        self.emit_table(ceps)
        self.emit_newline()

    def write_numerical_index(self, ceps: list[CEP]) -> str:
        """Write CEPs by number."""
        self.emit_text(".. _numerical-index:")
        self.emit_newline()

        self.emit_title("Numerical Index")
        self.emit_table(ceps)
        self.emit_newline()

        numerical_index_string = "\n".join(self.output)
        return numerical_index_string

    def write_cep0(
        self,
        ceps: list[CEP],
        header: str = HEADER,
        intro: str = INTRO,
        is_cep0: bool = True,
        builder: str = None,
    ) -> str:
        # CEP metadata
        self.emit_text(header)
        self.emit_newline()

        # Introduction
        self.emit_title("Introduction")
        self.emit_text(intro)
        self.emit_newline()

        # CEPs by topic
        if is_cep0:
            self.emit_title("Topics")
            self.emit_text(
                "CEPs for specialist subjects are :doc:`indexed by topic <topic/index>`."
            )
            self.emit_newline()
            for subindex in SUBINDICES_BY_TOPIC:
                target = (
                    f"topic/{subindex}.html"
                    if builder == "html"
                    else f"../topic/{subindex}/"
                )
                self.emit_text(f"* `{subindex.title()} CEPs <{target}>`_")
                self.emit_newline()
            self.emit_newline()

            self.emit_title("API")
            self.emit_text(
                "The `CEPS API </api/ceps.json>`__ is a JSON file of metadata about "
                "all the published CEPs. :doc:`Read more here <api/index>`."
            )
            self.emit_newline()

        # CEPs by number
        if is_cep0:
            self.emit_title("Numerical Index")
            self.emit_text(
                "The :doc:`numerical index </numerical>` contains "
                "a table of all CEPs, ordered by number."
            )
            self.emit_newline()

        # CEPs by category
        self.emit_title("Index by Category")
        (
            meta,
            info,
            provisional,
            accepted,
            open_,
            finished,
            historical,
            deferred,
            dead,
        ) = _classify_ceps(ceps)
        cep_categories = [
            ("Process and Meta-CEPs", meta),
            ("Other Informational CEPs", info),
            (
                "Provisional CEPs (provisionally accepted; interface may still change)",
                provisional,
            ),
            ("Accepted CEPs (accepted; may not be implemented yet)", accepted),
            ("Open CEPs (under consideration)", open_),
            ("Finished CEPs (done, with a stable interface)", finished),
            ("Historical Meta-CEPs and Informational CEPs", historical),
            ("Deferred CEPs (postponed pending further research or updates)", deferred),
            ("Rejected, Superseded, and Withdrawn CEPs", dead),
        ]
        if len(ceps) == 0 and not is_cep0:
            self.emit_text("None.")
            self.emit_newline()
        else:
            for category, ceps_in_category in cep_categories:
                # For sub-indices, only emit categories with entries.
                # For CEP 0, emit every category, but only with a table when it has entries.
                if len(ceps_in_category) > 0:
                    self.emit_cep_category(category, ceps_in_category)
                elif is_cep0:
                    # emit the category with no table
                    self.emit_subtitle(category)
                    self.emit_text("None.")
                    self.emit_newline()

        self.emit_newline()

        # Reserved CEP numbers
        if is_cep0:
            self.emit_title("Reserved CEP Numbers")
            if self.RESERVED:
                self.emit_column_headers(include_version=False)
                for number, claimants in sorted(self.RESERVED.items()):
                    self.emit_cep_row(
                        shorthand="",
                        number=number,
                        title="RESERVED",
                        authors=claimants,
                        protocol_version=None,
                    )
            else:
                self.emit_text("None.")

            self.emit_newline()

        # CEP types key
        self.emit_title("CEP Types Key")
        for type_ in sorted(TYPE_VALUES):
            self.emit_text(
                f"* **{type_[0]}** --- *{type_}*: {ABBREVIATED_TYPES[type_]}"
            )
            self.emit_newline()

        self.emit_text(":cep:`More info in CEP 1 <1#cep-types>`.")
        self.emit_newline()

        # CEP status key
        self.emit_title("CEP Status Key")
        for status in sorted(STATUS_VALUES):
            # Draft CEPs have no status displayed, Active shares a key with Accepted
            status_code = "<No letter>" if status == STATUS_DRAFT else status[0]
            self.emit_text(
                f"* **{status_code}** --- *{status}*: {ABBREVIATED_STATUSES[status]}"
            )
            self.emit_newline()

        self.emit_text(":cep:`More info in CEP 1 <1#cep-review-resolution>`.")
        self.emit_newline()

        if is_cep0:
            # CEP owners
            authors_dict = _verify_email_addresses(ceps)
            self.emit_title("Authors/Owners")
            if authors_dict:
                max_name_len = max(
                    max(len(author_name) for author_name in authors_dict),
                    len("Name"),
                )
                self.emit_author_table_separator(max_name_len)
                self.emit_text(f"{'Name':{max_name_len}}  Email Address")
                self.emit_author_table_separator(max_name_len)
                for author_name in _sort_authors(authors_dict):
                    # Use the email from authors_dict instead of the one from "author" as
                    # the author instance may have an empty email.
                    self.emit_text(
                        f"{author_name:{max_name_len}}  {authors_dict[author_name]}"
                    )
                self.emit_author_table_separator(max_name_len)
            else:
                self.emit_text("None.")
            self.emit_newline()
            self.emit_newline()

        cep0_string = "\n".join(self.output)
        return cep0_string


def _classify_ceps(ceps: list[CEP]) -> tuple[list[CEP], ...]:
    """Sort CEPs into meta, informational, accepted, open, finished,
    and essentially dead."""
    meta = []
    info = []
    provisional = []
    accepted = []
    open_ = []
    finished = []
    historical = []
    deferred = []
    dead = []
    for cep in ceps:
        # Order of 'if' statement important.  Key Status values take precedence
        # over Type value, and vice-versa.
        if cep.status == STATUS_DRAFT:
            open_.append(cep)
        elif cep.status == STATUS_DEFERRED:
            deferred.append(cep)
        elif cep.cep_type == TYPE_PROCESS:
            if cep.status in {STATUS_ACCEPTED, STATUS_ACTIVE}:
                meta.append(cep)
            elif cep.status in {STATUS_WITHDRAWN, STATUS_REJECTED}:
                dead.append(cep)
            else:
                historical.append(cep)
        elif cep.status in DEAD_STATUSES:
            dead.append(cep)
        elif cep.cep_type == TYPE_INFO:
            # Hack until the conflict between the use of "Final"
            # for both API definition CEPs and other (actually
            # obsolete) CEPs is addressed
            if (
                cep.status == STATUS_ACTIVE
                or "release schedule" not in cep.title.lower()
            ):
                info.append(cep)
            else:
                historical.append(cep)
        elif cep.status == STATUS_PROVISIONAL:
            provisional.append(cep)
        elif cep.status in {STATUS_ACCEPTED, STATUS_ACTIVE}:
            accepted.append(cep)
        elif cep.status == STATUS_FINAL:
            finished.append(cep)
        else:
            raise CEPError(
                f"Unsorted ({cep.cep_type}/{cep.status})", cep.filename, cep.number
            )
    return (
        meta,
        info,
        provisional,
        accepted,
        open_,
        finished,
        historical,
        deferred,
        dead,
    )


def _verify_email_addresses(ceps: list[CEP]) -> dict[str, str]:
    authors_dict: dict[str, list[str]] = {}
    for cep in ceps:
        for author in cep.authors:
            # If this is the first time we have come across an author, add them.
            if author.full_name not in authors_dict:
                authors_dict[author.full_name] = []

            # If the new email is an empty string, move on.
            if not author.email:
                continue
            # If the email has not been seen, add it to the list.
            emails = authors_dict[author.full_name]
            if author.email not in emails:
                emails.append(author.email)

    # Combine multiple email addresses with commas. Since ceps is
    # sorted by CEP number, this should produce a deterministic
    # output.
    return {name: ", ".join(emails) for name, emails in authors_dict.items()}


def _sort_authors(authors_dict: dict[str, str]) -> list[str]:
    return sorted(authors_dict, key=_author_sort_by)


def _author_sort_by(author_name: str) -> str:
    """Skip lower-cased words in surname when sorting."""
    surname, *_ = author_name.split(",")
    surname_parts = surname.split()
    for i, part in enumerate(surname_parts):
        if part[0].isupper():
            base = " ".join(surname_parts[i:]).lower()
            return unicodedata.normalize("NFKD", base)
    # If no capitals, use the whole string
    return unicodedata.normalize("NFKD", surname.lower())
