from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx import parsers

from cep_sphinx_extensions.cep_processor.transforms import (
    cep_contents,
    cep_footer,
    cep_headers,
    cep_title,
)

if TYPE_CHECKING:
    from docutils import transforms


class CEPParser(parsers.RSTParser):
    """RST parser with custom CEP transforms."""

    supported = ("cep", "cfms-enhancement-proposal")  # for source_suffix in conf.py

    def __init__(self):
        """Mark the document as containing RFC 2822 headers."""
        super().__init__(rfc2822=True)

    def get_transforms(self) -> list[type[transforms.Transform]]:
        """Use our custom CEP transform rules."""
        return [
            cep_headers.CEPHeaders,
            cep_title.CEPTitle,
            cep_contents.CEPContents,
            cep_footer.CEPFooter,
        ]
