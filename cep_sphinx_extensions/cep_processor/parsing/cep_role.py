from docutils import nodes
from sphinx import roles


class CEPRole(roles.ReferenceRole):
    """Override the :cep: role"""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        # Get CEP URI from role text.
        cep_str, _, fragment = self.target.partition("#")
        try:
            cep_num = int(cep_str)
        except ValueError:
            msg = self.inliner.reporter.error(
                f"invalid CEP number {self.target}", line=self.lineno
            )
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]
        cep_base = self.inliner.document.settings.cep_url.format(cep_num)
        if self.inliner.document.settings.builder == "dirhtml":
            cep_base = "../" + cep_base
        if "topic" in self.get_location():
            cep_base = "../" + cep_base
        if fragment:
            ref_uri = f"{cep_base}#{fragment}"
        else:
            ref_uri = cep_base
        if self.has_explicit_title:
            title = self.title
        else:
            title = f"CEP {cep_num}"

        return [
            nodes.reference(
                "",
                title,
                internal=True,
                refuri=ref_uri,
                classes=["cep"],
                _title_tuple=(cep_num, fragment),
            )
        ], []
