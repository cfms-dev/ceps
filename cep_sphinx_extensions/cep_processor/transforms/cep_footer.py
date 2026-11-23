import subprocess
import time
from pathlib import Path

from docutils import nodes, transforms


class CEPFooter(transforms.Transform):
    """Footer transforms for CEPs.

    - Remove the References/Footnotes section if it is empty when rendered.
    """

    # Uses same priority as docutils.transforms.TargetNotes
    default_priority = 520

    def apply(self) -> None:
        cep_source_path = Path(self.document["source"])
        if not cep_source_path.match("cep-????.???"):
            return  # not a CEP file, exit early

        # Iterate through sections from the end of the document
        for section in reversed(self.document[0]):
            if not isinstance(section, nodes.section):
                continue
            title_words = {*section[0].astext().lower().split()}
            if {"references", "footnotes"} & title_words:
                # Remove references/footnotes sections if there is no displayed
                # content (i.e. they only have title & link target nodes)
                to_hoist = []
                types = set()
                for node in section:
                    types.add(type(node))
                    if isinstance(node, nodes.target):
                        to_hoist.append(node)
                if types <= {nodes.title, nodes.target, nodes.system_message}:
                    section.parent.extend(to_hoist)
                    section.parent.remove(section)


def get_page_footer_context(cep_stem: str) -> dict[str, str]:
    """Template context for the page footer, rendered by ``page.html``."""
    context = {
        "source_link": (
            f"https://github.com/cfms-dev/ceps/blob/main/ceps/{cep_stem}.rst"
        ),
    }
    iso_time = _LAST_MODIFIED_TIMES.get(cep_stem, "")
    if iso_time:
        context["last_modified"] = iso_time
        context["commit_link"] = (
            f"https://github.com/cfms-dev/ceps/commits/main/ceps/{cep_stem}.rst"
        )
    return context


def _get_last_modified_timestamps():
    # get timestamps and changed files from all commits (without paging results)
    args = ("git", "--no-pager", "log", "--format=#%at", "--name-only")
    ret = subprocess.run(args, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    if ret.returncode:  # non-zero return code
        return {}
    all_modified = ret.stdout

    # remove "ceps/" prefix from file names
    all_modified = all_modified.replace("\nceps/", "\n")

    # set up the dictionary with the *current* files
    ceps_dir = Path(__file__, "..", "..", "..", "..", "ceps").resolve()
    last_modified = {path.stem: "" for path in ceps_dir.glob("cep-????.rst")}

    # iterate through newest to oldest, updating per file timestamps
    change_sets = all_modified.removeprefix("#").split("#")
    for change_set in change_sets:
        timestamp, files = change_set.split("\n", 1)
        for file in files.strip().split("\n"):
            if not file.startswith("cep-") or not file.endswith((".rst", ".txt")):
                continue  # not a CEP
            file = file[:-4]
            if last_modified.get(file) != "":
                continue  # most recent modified date already found
            try:
                y, m, d, hh, mm, ss, *_ = time.gmtime(float(timestamp))
            except ValueError:
                continue  # if float conversion fails
            last_modified[file] = f"{y:04}-{m:02}-{d:02} {hh:02}:{mm:02}:{ss:02}"

    return last_modified


_LAST_MODIFIED_TIMES = _get_last_modified_timestamps()
