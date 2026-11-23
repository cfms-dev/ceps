"""Holds type and status constants for CEP 0 generation."""

STATUS_ACCEPTED = "Accepted"
STATUS_ACTIVE = "Active"
STATUS_DEFERRED = "Deferred"
STATUS_DRAFT = "Draft"
STATUS_FINAL = "Final"
STATUS_PROVISIONAL = "Provisional"
STATUS_REJECTED = "Rejected"
STATUS_SUPERSEDED = "Superseded"
STATUS_WITHDRAWN = "Withdrawn"

# Valid values for the Status header.
STATUS_VALUES = {
    STATUS_ACCEPTED,
    STATUS_PROVISIONAL,
    STATUS_REJECTED,
    STATUS_WITHDRAWN,
    STATUS_DEFERRED,
    STATUS_FINAL,
    STATUS_ACTIVE,
    STATUS_DRAFT,
    STATUS_SUPERSEDED,
}
# Map of invalid/special statuses to their valid counterparts
SPECIAL_STATUSES = {
    "April Fool!": STATUS_REJECTED,  # See CEP 401 :)
}
# Draft CEPs have no status displayed
HIDE_STATUS = {STATUS_DRAFT}
# Dead CEP statuses
DEAD_STATUSES = {STATUS_REJECTED, STATUS_WITHDRAWN, STATUS_SUPERSEDED}

TYPE_INFO = "Informational"
TYPE_PROCESS = "Process"
TYPE_STANDARDS = "Standards Track"

# Valid values for the Type header.
TYPE_VALUES = {TYPE_STANDARDS, TYPE_INFO, TYPE_PROCESS}
# Active CEPs can only be for Informational or Process CEPs.
ACTIVE_ALLOWED = {TYPE_PROCESS, TYPE_INFO}

# map of topic -> additional description
SUBINDICES_BY_TOPIC = {
    "governance": """\
These CEPs detail CFMS's governance, including governance model proposals
and selection.
    """,
    "packaging": """\
Packaging CEPs propose major additions or changes to packaging specifications.
""",
    "release": """\
A CEP is written to specify the release cycle for each feature release of CFMS.
""",
    "typing": """\
These CEPs propose changes to the static type system
or otherwise relate to type annotations.
They are listed here for reference.
""",
}
