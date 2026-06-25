import importlib.util
import os
import sys
import tempfile
import types
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
PKG = "blender_menu"


def _load_addon_module(name: str):
    if PKG not in sys.modules:
        pkg = types.ModuleType(PKG)
        pkg.__path__ = [ROOT]
        sys.modules[PKG] = pkg
    full = f"{PKG}.{name}"
    path = os.path.join(ROOT, f"{name}.py")
    spec = importlib.util.spec_from_file_location(full, path, submodule_search_locations=[ROOT])
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = PKG
    sys.modules[full] = mod
    spec.loader.exec_module(mod)
    return mod


labels = _load_addon_module("labels")
discovery = _load_addon_module("discovery")
format_menu_label = labels.format_menu_label
build_script_tree = discovery.build_script_tree
merge_folder_nodes = discovery.merge_folder_nodes
build_merged_script_tree = discovery.build_merged_script_tree
FolderNode = discovery.FolderNode
ScriptItem = discovery.ScriptItem


class TestFormatMenuLabel(unittest.TestCase):
    def test_snake_case(self):
        self.assertEqual(format_menu_label("export_fbx"), "Export Fbx")
        self.assertEqual(format_menu_label("my_script_name"), "My Script Name")

    def test_camel_case(self):
        self.assertEqual(format_menu_label("steamRoller"), "Steam Roller")
        self.assertEqual(format_menu_label("rigControls"), "Rig Controls")
        self.assertEqual(format_menu_label("exportMesh"), "Export Mesh")

    def test_lowercase(self):
        self.assertEqual(format_menu_label("steamroller"), "Steamroller")

    def test_already_spaced(self):
        self.assertEqual(format_menu_label("Already Nice"), "Already Nice")

    def test_mixed_snake_and_camel(self):
        self.assertEqual(format_menu_label("my_toolName"), "My Tool Name")


class TestDiscoveryLabels(unittest.TestCase):
    def test_script_label_formatted(self):
        with tempfile.TemporaryDirectory() as root:
            script_path = os.path.join(root, "rigControls.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write("def main():\n    pass\n")
            tree = build_script_tree(root)
            self.assertEqual(len(tree.scripts), 1)
            self.assertEqual(tree.scripts[0].label, "Rig Controls")

    def test_subfolder_sort_uses_raw_names(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "zebraFolder"))
            os.makedirs(os.path.join(root, "alpha_folder"))
            for name in ("zebraFolder", "alpha_folder"):
                script_path = os.path.join(root, name, "run.py")
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write("def main():\n    pass\n")
            tree = build_script_tree(root)
            names = [name for name, _ in tree.subfolders]
            self.assertEqual(names, ["alpha_folder", "zebraFolder"])


def _write_main_script(path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("def main():\n    pass\n")


class TestMergeFolderNodes(unittest.TestCase):
    def test_merge_subfolders_with_same_name(self):
        tools_a = FolderNode()
        tools_a.scripts.append(ScriptItem(label="Alpha", path="/a/tools/alpha.py"))
        node_a = FolderNode(subfolders=[("tools", tools_a)])

        tools_b = FolderNode()
        tools_b.scripts.append(ScriptItem(label="Beta", path="/b/tools/beta.py"))
        node_b = FolderNode(subfolders=[("tools", tools_b)])

        merged = merge_folder_nodes([node_a, node_b])
        self.assertEqual(len(merged.subfolders), 1)
        name, child = merged.subfolders[0]
        self.assertEqual(name, "tools")
        labels = [s.label for s in child.scripts]
        self.assertEqual(labels, ["Alpha", "Beta"])

    def test_later_path_wins_same_script_label(self):
        tools_a = FolderNode()
        tools_a.scripts.append(ScriptItem(label="Export", path="/official/tools/export.py"))
        node_a = FolderNode(subfolders=[("tools", tools_a)])

        tools_b = FolderNode()
        tools_b.scripts.append(ScriptItem(label="Export", path="/personal/tools/export.py"))
        node_b = FolderNode(subfolders=[("tools", tools_b)])

        merged = merge_folder_nodes([node_a, node_b])
        child = merged.subfolders[0][1]
        self.assertEqual(len(child.scripts), 1)
        self.assertEqual(child.scripts[0].path, "/personal/tools/export.py")

    def test_root_level_scripts_merged(self):
        node_a = FolderNode(scripts=[ScriptItem(label="One", path="/a/one.py")])
        node_b = FolderNode(scripts=[ScriptItem(label="Two", path="/b/two.py")])

        merged = merge_folder_nodes([node_a, node_b])
        labels = [s.label for s in merged.scripts]
        self.assertEqual(labels, ["One", "Two"])

    def test_post_merge_sort_order(self):
        node_a = FolderNode(
            scripts=[
                ScriptItem(label="Zebra", path="/a/zebra.py"),
                ScriptItem(label="Alpha", path="/a/alpha.py"),
            ]
        )
        merged = merge_folder_nodes([node_a])
        labels = [s.label for s in merged.scripts]
        self.assertEqual(labels, ["Alpha", "Zebra"])


class TestBuildMergedScriptTree(unittest.TestCase):
    def test_valid_multi_path_merge(self):
        with tempfile.TemporaryDirectory() as root_a, tempfile.TemporaryDirectory() as root_b:
            os.makedirs(os.path.join(root_a, "rigging"))
            _write_main_script(os.path.join(root_a, "rigging", "pose.py"))
            os.makedirs(os.path.join(root_b, "export"))
            _write_main_script(os.path.join(root_b, "export", "fbx.py"))

            tree, skipped = build_merged_script_tree([root_a, root_b])
            self.assertEqual(skipped, [])
            self.assertIsNotNone(tree)
            names = [name for name, _ in tree.subfolders]
            self.assertEqual(names, ["export", "rigging"])

    def test_skipped_invalid_paths(self):
        with tempfile.TemporaryDirectory() as valid_root:
            _write_main_script(os.path.join(valid_root, "run.py"))

            tree, skipped = build_merged_script_tree([valid_root, "/nonexistent/path"])
            self.assertEqual(len(skipped), 1)
            self.assertIsNotNone(tree)
            self.assertEqual(len(tree.scripts), 1)

    def test_all_invalid_returns_none(self):
        tree, skipped = build_merged_script_tree(["/nonexistent/a", "/nonexistent/b"])
        self.assertIsNone(tree)
        self.assertEqual(len(skipped), 2)

    def test_valid_paths_but_empty_tree(self):
        with tempfile.TemporaryDirectory() as root_a, tempfile.TemporaryDirectory() as root_b:
            tree, skipped = build_merged_script_tree([root_a, root_b])
            self.assertEqual(skipped, [])
            self.assertIsNotNone(tree)
            self.assertEqual(tree.subfolders, [])
            self.assertEqual(tree.scripts, [])


if __name__ == "__main__":
    unittest.main()
