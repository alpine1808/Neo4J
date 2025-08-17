import re
_LABEL = re.compile(r"^[A-Za-z0-9_]+$")
_REL = re.compile(r"^[A-Za-z0-9_]+$")
_PROP = re.compile(r"^[A-Za-z0-9_]+$")

def validate_label(label: str) -> str:
    if not label or not _LABEL.match(label):
        raise ValueError(f"Invalid label: {label!r}. Allowed: A-Z a-z 0-9 _")
    return label

def validate_rel(rel: str) -> str:
    if not rel or not _REL.match(rel):
        raise ValueError(f"Invalid relationship type: {rel!r}. Allowed: A-Z a-z 0-9 _")
    return rel

def validate_prop(prop: str) -> str:
    if not prop or not _PROP.match(prop):
        raise ValueError(f"Invalid property: {prop!r}. Allowed: A-Z a-z 0-9 _")
    return prop
