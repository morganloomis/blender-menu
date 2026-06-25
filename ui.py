# UI registration hook: add menu/pie registration and unregistration here.
# register_ui() is called from the main package register(); unregister_ui() from unregister().
# Script menus are built from the script root preference and appear in the 3D Viewport header.

import bpy
from bpy.app.handlers import persistent

from . import preferences
from .discovery import FolderNode, ScriptItem, build_script_tree, tree_has_menus
from .operators import BLENDERMENU_OT_run_script

# Dynamic menu classes created at registration; unregistered in reverse order.
_registered_menu_classes: list[type] = []
_editor_menus_draws: list = []

# Coalesced deferred rebuild state.
_pending_rebuild = False
_rebuild_timer_registered = False
_load_post_handler = None

# Menu build state for preferences UI and operator reports.
REASON_OK = "ok"
REASON_NO_PATH = "no_path"
REASON_INVALID_PATH = "invalid_path"
REASON_EMPTY = "empty"

_menu_build_state = {
    "reason": REASON_NO_PATH,
    "message": "No menus: script root not set",
    "header_menu_count": 0,
}


def get_menu_build_state() -> dict:
    """Return a copy of the last menu build state."""
    return dict(_menu_build_state)


def _set_menu_build_state(reason: str, message: str, header_menu_count: int) -> None:
    _menu_build_state["reason"] = reason
    _menu_build_state["message"] = message
    _menu_build_state["header_menu_count"] = header_menu_count


def _count_scripts(node: FolderNode) -> int:
    count = len(node.scripts)
    for _name, child in node.subfolders:
        count += _count_scripts(child)
    return count


def _should_log_rebuild() -> bool:
    if bpy.app.debug_value:
        return True
    prefs = preferences.get_preferences()
    return bool(prefs and prefs.show_menu_build_log)


def _log_rebuild(
    path: str,
    source: str,
    tree: FolderNode | None,
    header_menu_count: int,
    reason: str,
) -> None:
    if not _should_log_rebuild():
        return
    subfolder_count = len(tree.subfolders) if tree else 0
    script_count = _count_scripts(tree) if tree else 0
    print(
        "[Blender Tree Menus] rebuild:"
        f" path={path!r}"
        f" source={source}"
        f" reason={reason}"
        f" subfolders={subfolder_count}"
        f" scripts={script_count}"
        f" header_menus={header_menu_count}"
    )


def _make_menu_class(
    node: FolderNode,
    label: str,
    name_prefix: str,
    counter: list[int],
) -> tuple[type, list[type]]:
    """Build a menu class for this node and all descendants."""
    child_classes_and_lists: list[tuple[type, list[type]]] = []
    for subname, child_node in node.subfolders:
        counter[0] += 1
        child_classes_and_lists.append(
            _make_menu_class(child_node, subname, f"{name_prefix}_{counter[0]}", counter)
        )

    child_menu_classes = [item[0] for item in child_classes_and_lists]
    child_names = [name for name, _ in node.subfolders]
    all_descendant = [cls for _, reg in child_classes_and_lists for cls in reg]

    def draw_menu(self, context):
        layout = self.layout
        for name, child_class in zip(child_names, child_menu_classes):
            layout.menu(child_class.bl_idname, text=name)
        for item in node.scripts:
            op = layout.operator(BLENDERMENU_OT_run_script.bl_idname, text=item.label)
            op.script_path = item.path

    counter[0] += 1
    bl_idname = f"BLENDERMENU_MT_script_{name_prefix}_{counter[0]}"
    menu_class = type(
        bl_idname,
        (bpy.types.Menu,),
        {
            "bl_idname": bl_idname,
            "bl_label": label,
            "draw": draw_menu,
        },
    )
    return menu_class, all_descendant + child_menu_classes + [menu_class]


def _make_root_scripts_menu(
    scripts: list[ScriptItem],
    name_prefix: str,
    counter: list[int],
) -> tuple[type, list[type]]:
    """Build a top-level menu for scripts directly under the script root."""

    def draw_menu(self, context):
        layout = self.layout
        for item in scripts:
            op = layout.operator(BLENDERMENU_OT_run_script.bl_idname, text=item.label)
            op.script_path = item.path

    counter[0] += 1
    bl_idname = f"BLENDERMENU_MT_script_{name_prefix}_{counter[0]}"
    menu_class = type(
        bl_idname,
        (bpy.types.Menu,),
        {
            "bl_idname": bl_idname,
            "bl_label": "Scripts",
            "draw": draw_menu,
        },
    )
    return menu_class, [menu_class]


def _register_menu_class(cls: type) -> None:
    if hasattr(bpy.types, cls.__name__):
        try:
            bpy.utils.unregister_class(getattr(bpy.types, cls.__name__))
        except RuntimeError:
            pass
    bpy.utils.register_class(cls)
    _registered_menu_classes.append(cls)


def _append_header_menu(menu_idname: str) -> None:
    def draw(self, context):
        self.layout.menu(menu_idname)

    _editor_menus_draws.append(draw)
    bpy.types.VIEW3D_MT_editor_menus.append(draw)


def _unregister_dynamic_menus() -> None:
    """Remove header menu draws and unregister dynamic menu classes."""
    for draw in reversed(_editor_menus_draws):
        try:
            bpy.types.VIEW3D_MT_editor_menus.remove(draw)
        except ValueError:
            pass
    _editor_menus_draws.clear()

    for cls in reversed(_registered_menu_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    _registered_menu_classes.clear()

    for cls in reversed(bpy.types.Menu.__subclasses__()):
        if cls.__name__.startswith("BLENDERMENU_MT_script_"):
            try:
                bpy.utils.unregister_class(cls)
            except RuntimeError:
                pass


def build_menus() -> int:
    """Build header menus from the current script root. Returns header menu count."""
    raw_path, source = preferences.get_script_root()

    if not raw_path:
        message = "No menus: script root not set"
        _set_menu_build_state(REASON_NO_PATH, message, 0)
        _log_rebuild("", source, None, 0, REASON_NO_PATH)
        return 0

    tree = build_script_tree(raw_path)
    if tree is None:
        message = f"No menus: path invalid ({raw_path})"
        _set_menu_build_state(REASON_INVALID_PATH, message, 0)
        _log_rebuild(raw_path, source, None, 0, REASON_INVALID_PATH)
        return 0

    if not tree_has_menus(tree):
        message = f"No menus: no scripts with main() in {raw_path}"
        _set_menu_build_state(REASON_EMPTY, message, 0)
        _log_rebuild(raw_path, source, tree, 0, REASON_EMPTY)
        return 0

    counter = [0]
    header_menu_count = 0

    for folder_name, child_node in tree.subfolders:
        menu_class, all_classes = _make_menu_class(child_node, folder_name, folder_name, counter)
        for cls in all_classes:
            _register_menu_class(cls)
        _append_header_menu(menu_class.bl_idname)
        header_menu_count += 1

    if tree.scripts:
        scripts_menu, all_classes = _make_root_scripts_menu(tree.scripts, "root_scripts", counter)
        for cls in all_classes:
            _register_menu_class(cls)
        _append_header_menu(scripts_menu.bl_idname)
        header_menu_count += 1

    message = f"{header_menu_count} menu{'s' if header_menu_count != 1 else ''} registered from {raw_path}"
    _set_menu_build_state(REASON_OK, message, header_menu_count)
    _log_rebuild(raw_path, source, tree, header_menu_count, REASON_OK)
    return header_menu_count


def rebuild_menus() -> int:
    """Unregister prior dynamic menus and rebuild from the current script root."""
    _unregister_dynamic_menus()
    return build_menus()


def _run_deferred_rebuild() -> None:
    global _pending_rebuild, _rebuild_timer_registered
    _pending_rebuild = False
    _rebuild_timer_registered = False
    rebuild_menus()


def _deferred_rebuild_timer() -> None:
    _run_deferred_rebuild()
    return None


def schedule_rebuild() -> None:
    """Schedule a single coalesced menu rebuild on the next timer tick."""
    global _pending_rebuild, _rebuild_timer_registered
    _pending_rebuild = True
    if _rebuild_timer_registered:
        return
    _rebuild_timer_registered = True
    bpy.app.timers.register(_deferred_rebuild_timer, first_interval=0.0)


@persistent
def _on_load_post(_dummy) -> None:
    schedule_rebuild()


def register_ui() -> None:
    """Register lifecycle hooks and schedule the first deferred menu rebuild."""
    global _load_post_handler
    schedule_rebuild()
    if _load_post_handler is None:
        _load_post_handler = _on_load_post
        bpy.app.handlers.load_post.append(_load_post_handler)


def unregister_ui() -> None:
    """Unregister UI, handlers, and pending rebuild state."""
    global _pending_rebuild, _rebuild_timer_registered, _load_post_handler

    _pending_rebuild = False
    _rebuild_timer_registered = False

    if _load_post_handler is not None:
        try:
            bpy.app.handlers.load_post.remove(_load_post_handler)
        except ValueError:
            pass
        _load_post_handler = None

    _unregister_dynamic_menus()
