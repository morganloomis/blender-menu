# Menu label formatting: convert raw folder/script names to display labels.

import re

_CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def format_menu_label(raw_name: str) -> str:
    """Split snake_case and camelCase into words, capitalizing each for menu display."""
    name = raw_name.replace("_", " ")
    name = _CAMEL_BOUNDARY.sub(" ", name)
    return " ".join(part.capitalize() for part in name.split())
