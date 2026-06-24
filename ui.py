# UI registration hook: add menu/pie registration and unregistration here.
# register_ui() is called from the main package register(); unregister_ui() from unregister().
# Script menus are built from the script root preference and appear in the 3D Viewport header.

import bpy
from . import preferences
from .discovery import build_script_tree, FolderNode
from .operators import BLENDERMENU_OT_run_script

# Dynamic menu classes created at registration; unregistered in reverse order.
_registered_menu_classes: list[type] = []
_root_menu_idname: str | None = None
_editor_menus_draw = None  # Stored so we can remove it on unregister.


def _make_menu_class(node: FolderNode, name_prefix: str, counter: list[int]) -> tuple[type, list[type]]:
    """Build a menu class for this node and all descendants. Returns (class, flat list to register, this last)."""
    child_classes_and_lists: list[tuple[type, list[type]]] = []
    for subname, child_node in node.subfolders:
        counter[0] += 1
        child_classes_and_lists.append(_make_menu_class(child_node, f"{name_prefix}_{counter[0]}", counter))

    child_menu_classes = [t[0] for t in child_classes_and_lists]
    child_names = [name for name, _ in node.subfolders]
    all_descendant = [c for _, reg in child_classes_and_lists for c in reg]

    # Build a class that draws this node's submenus and script items.
    def draw_menu(self, context):
        layout = self.layout
        for (name, child_class) in zip(child_names, child_menu_classes):
            layout.menu(child_class.bl_idname, text=name)
        for item in node.scripts:
            op = layout.operator(BLENDERMENU_OT_run_script.bl_idname, text=item.label)
            op.script_path = item.path

    counter[0] += 1
    bl_idname = f"BLENDERMENU_MT_script_{name_prefix}_{counter[0]}"
    menu_class = type(
        "BLENDERMENU_MT_script_dyn",
        (bpy.types.Menu,),
        {
            "bl_idname": bl_idname,
            "bl_label": "Scripts",
            "draw": lambda self, context: draw_menu(self, context),
        },
    )
    return (menu_class, all_descendant + child_menu_classes + [menu_class])


def register_ui():
    """Register script menus from preferences script root; no menus if path invalid or empty."""
    prefs = preferences.get_preferences()
    script_root = (prefs.script_root or "") if prefs else ""
    tree = build_script_tree(script_root)
    if tree is None:
        return
    # Build dynamic menu classes (post-order so we can register leafs first).
    counter = [0]
    root_class, all_classes = _make_menu_class(tree, "0", counter)
    for cls in all_classes:
        bpy.utils.register_class(cls)
        _registered_menu_classes.append(cls)
    global _root_menu_idname, _editor_menus_draw
    _root_menu_idname = root_class.bl_idname

    def _draw(self, context):
        self.layout.menu(_root_menu_idname)

    _editor_menus_draw = _draw
    bpy.types.VIEW3D_MT_editor_menus.append(_editor_menus_draw)


def unregister_ui():
    """Unregister UI in reverse order of register_ui()."""
    global _root_menu_idname, _editor_menus_draw
    if _editor_menus_draw is not None:
        try:
            bpy.types.VIEW3D_MT_editor_menus.remove(_editor_menus_draw)
        except ValueError:
            pass
        _editor_menus_draw = None
    _root_menu_idname = None
    for cls in reversed(_registered_menu_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    _registered_menu_classes.clear()