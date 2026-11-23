"""Sphinx extensions for performant CEP processing"""

from __future__ import annotations

import html
from pathlib import Path
from typing import TYPE_CHECKING, Any

from docutils.writers.html5_polyglot import HTMLTranslator
from sphinx import environment

from cep_sphinx_extensions.cep_processor.html import (
    cep_html_builder,
    cep_html_translator,
)
from cep_sphinx_extensions.cep_processor.parsing import (
    cep_banner_directive,
    cep_parser,
    cep_role,
)
from cep_sphinx_extensions.cep_processor.transforms import cep_footer, cep_references
from cep_sphinx_extensions.cep_zero_generator.cep_index_generator import create_cep_zero
from cep_sphinx_extensions.generate_rss import (
    create_rss_feed,
    get_from_doctree,
)
from cep_sphinx_extensions.lexers import get_custom_lexers

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def _update_config_for_builder(app: Sphinx) -> None:
    app.env.document_ids = {}  # For CEPReferenceRoleTitleText
    app.env.settings["builder"] = app.builder.name
    if app.builder.name == "dirhtml":
        app.env.settings["cep_url"] = "cep-{:0>4}/"

    app.connect("build-finished", _post_build)  # Post-build tasks


def _post_build(app: Sphinx, exception: Exception | None) -> None:
    from pathlib import Path

    from build import create_index_file

    if exception is not None:
        return

    # internal_builder exists if Sphinx is run by build.py
    if "internal_builder" not in app.tags:
        create_index_file(Path(app.outdir), app.builder.name)
    create_rss_feed(app.doctreedir, app.outdir)


def set_description(
    app: Sphinx, pagename: str, templatename: str, context: dict[str, Any], doctree
) -> None:
    if not pagename.startswith("cep-"):
        return

    full_path = Path(app.doctreedir) / f"{pagename}.doctree"
    abstract = get_from_doctree(full_path, "Abstract")
    if abstract:
        if len(abstract) > 256:
            abstract = abstract[:253] + "..."
        context["description"] = html.escape(abstract)
    else:
        context["description"] = "CFMS Enhancement Proposals (CEPs)"

    if pagename != "cep-0000":
        context.update(cep_footer.get_page_footer_context(pagename))


def setup(app: Sphinx) -> dict[str, bool]:
    """Initialize Sphinx extension."""

    environment.default_settings["cep_url"] = "cep-{:0>4}.html"
    environment.default_settings["halt_level"] = 2  # Fail on Docutils warning

    # Register plugin logic
    app.add_builder(cep_html_builder.FileBuilder, override=True)
    app.add_builder(cep_html_builder.DirectoryBuilder, override=True)

    app.add_source_parser(cep_parser.CEPParser)  # Add CEP transforms

    app.set_translator(
        "html", cep_html_translator.CEPTranslator
    )  # Docutils Node Visitor overrides (html builder)
    app.set_translator(
        "dirhtml", cep_html_translator.CEPTranslator
    )  # Docutils Node Visitor overrides (dirhtml builder)

    app.add_role(
        "cep", cep_role.CEPRole(), override=True
    )  # Transform CEP references to links

    app.add_post_transform(cep_references.CEPReferenceRoleTitleText)
    app.add_post_transform(cep_references.CEPIntersphinxTitleText)

    # Register custom directives
    app.add_directive("cep-banner", cep_banner_directive.CEPBanner)
    app.add_directive("canonical-doc", cep_banner_directive.CanonicalDocBanner)
    app.add_directive(
        "canonical-pypa-spec", cep_banner_directive.CanonicalPyPASpecBanner
    )
    app.add_directive(
        "canonical-typing-spec", cep_banner_directive.CanonicalTypingSpecBanner
    )
    app.add_directive("rejected", cep_banner_directive.RejectedBanner)
    app.add_directive("superseded", cep_banner_directive.SupersededBanner)
    app.add_directive("withdrawn", cep_banner_directive.WithdrawnBanner)

    # Register custom lexers
    for lexer in get_custom_lexers():
        app.add_lexer(lexer.name, lexer)

    # Register event callbacks
    app.connect(
        "builder-inited", _update_config_for_builder
    )  # Update configuration values for builder used
    app.connect("env-before-read-docs", create_cep_zero)  # CEP 0 hook
    app.connect("html-page-context", set_description)

    # Mathematics rendering
    inline_maths = HTMLTranslator.visit_math, None
    block_maths = HTMLTranslator.visit_math_block, None
    app.add_html_math_renderer(
        "maths_to_html", inline_maths, block_maths
    )  # Render maths to HTML

    # Parallel safety: https://www.sphinx-doc.org/en/master/extdev/index.html#extension-metadata
    return {"parallel_read_safe": True, "parallel_write_safe": True}
