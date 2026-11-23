from pathlib import Path

from docutils import nodes, transforms, utils
from docutils.parsers.rst import roles, states


class CEPTitle(transforms.Transform):
    """Add CEP title and organise document hierarchy."""

    # needs to run before docutils.transforms.frontmatter.DocInfo and after
    # cep_processor.transforms.cep_title.CEPTitle
    default_priority = 335

    def apply(self) -> None:
        if not Path(self.document["source"]).match("cep-*"):
            return  # not a CEP file, exit early

        # Directory to hold the CEP's RFC2822 header details, to extract a title string
        cep_header_details = {}

        # Iterate through the header fields, which are the first section of the document
        desired_fields = {"CEP", "Title"}
        fields_to_remove = []
        for field in self.document[0]:
            # Hold details of the attribute's tag against its details
            row_attributes = {sub.tagname: sub.rawsource for sub in field}
            cep_header_details[row_attributes["field_name"]] = row_attributes[
                "field_body"
            ]

            # Store the redundant fields in the table for removal
            if row_attributes["field_name"] in desired_fields:
                fields_to_remove.append(field)

            # We only need the CEP number and title
            if cep_header_details.keys() >= desired_fields:
                break

        # Create the title string for the CEP
        cep_number = int(cep_header_details["CEP"])
        cep_title = cep_header_details["Title"]
        cep_title_string = (
            f"CEP {cep_number} -- {cep_title}"  # double hyphen for en dash
        )

        # Generate the title section node and its properties
        title_nodes = _line_to_nodes(cep_title_string)
        cep_title_node = nodes.section(
            "",
            nodes.title("", "", *title_nodes, classes=["page-title"]),
            names=["cep-content"],
        )

        # Insert the title node as the root element, move children down
        document_children = self.document.children
        self.document.children = [cep_title_node]
        cep_title_node.extend(document_children)
        self.document.note_implicit_target(cep_title_node, cep_title_node)

        # Remove the now-redundant fields
        for field in fields_to_remove:
            field.parent.remove(field)


def _line_to_nodes(text: str) -> list[nodes.Node]:
    """Parse RST string to nodes."""
    document = utils.new_document("<inline-rst>")
    # patch settings
    document.settings.pep_references = document.settings.rfc_references = False
    # do parsing
    states.RSTStateMachine(
        state_classes=states.state_classes, initial_state="Body"
    ).run([text], document)
    # restore the "default" default role after parsing a document
    roles._roles.pop("", None)
    return document[0].children
