# Script discovery: scan directory for .py files with main(), build menu tree.
# Uses AST only; does not import or execute user code.

import ast
import os
from dataclasses import dataclass, field


@dataclass
class ScriptItem:
    """A script file that defines main(). label is the menu label (e.g. filename without .py)."""
    label: str
    path: str


@dataclass
class FolderNode:
    """A folder in the menu tree: subfolders and scripts, sorted by name."""
    subfolders: list[tuple[str, "FolderNode"]] = field(default_factory=list)
    scripts: list[ScriptItem] = field(default_factory=list)


def _has_main(source: str) -> bool:
    """Return True if the Python source defines a function named main. Uses AST only."""
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                return True
        return False
    except SyntaxError:
        return False


def _scan_folder(dir_path: str) -> FolderNode:
    """Scan a directory and build a FolderNode. Sorts subfolders and scripts lexicographically."""
    node = FolderNode()
    if not os.path.isdir(dir_path):
        return node
    try:
        entries = sorted(os.scandir(dir_path), key=lambda e: e.name.lower())
    except OSError:
        return node
    for entry in entries:
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            child = _scan_folder(entry.path)
            node.subfolders.append((entry.name, child))
        elif entry.is_file() and entry.name.endswith(".py"):
            try:
                with open(entry.path, "r", encoding="utf-8", errors="replace") as f:
                    source = f.read()
            except OSError:
                continue
            if _has_main(source):
                label = os.path.splitext(entry.name)[0]
                node.scripts.append(ScriptItem(label=label, path=entry.path))
    return node


def build_script_tree(root_path: str) -> FolderNode | None:
    """
    Build the menu tree for the given script root path.
    Returns a FolderNode with top-level subfolders and scripts, or None if root_path
    is invalid (missing, not a directory, or empty). Does not raise.
    """
    if not root_path or not root_path.strip():
        return None
    path = os.path.abspath(os.path.expanduser(root_path.strip()))
    if not os.path.isdir(path):
        return None
    return _scan_folder(path)
