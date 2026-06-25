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


if __name__ == "__main__":
    unittest.main()
