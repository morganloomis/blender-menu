# Add-on preferences. Register/unregister are called from the main package __init__.py.

import os

import bpy

# Extension installs use a qualified module name (e.g. bl_ext.user_default.blender_menu).
# Legacy add-on installs use the short package name. __package__ matches both at runtime.
_ADDON_MODULE = __package__


def _schedule_menu_rebuild():
    from . import ui

    ui.schedule_rebuild()


def _on_script_path_updated(self, context):
    _schedule_menu_rebuild()


class BLENDERMENU_script_path(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(
        name="Script directory",
        description="Folder to scan for scripts",
        default="",
        subtype="DIR_PATH",
        update=_on_script_path_updated,
    )


class BLENDERMENU_UL_script_paths(bpy.types.UIList):
    bl_idname = "BLENDERMENU_UL_script_paths"

    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):
        layout.prop(item, "path", text="")


class BLENDERMENU_preferences(bpy.types.AddonPreferences):
    bl_idname = _ADDON_MODULE

    script_paths: bpy.props.CollectionProperty(type=BLENDERMENU_script_path)
    script_paths_index: bpy.props.IntProperty(name="Active script path index", default=0)

    show_menu_build_log: bpy.props.BoolProperty(
        name="Show menu build log",
        description="Print menu build details to the system console on each rebuild",
        default=False,
    )

    def draw(self, context):
        from . import ui

        layout = self.layout
        box = layout.box()
        box.label(text="Turn folders on disk into script menus in the 3D Viewport.")
        row = box.row()
        row.template_list(
            "BLENDERMENU_UL_script_paths",
            "",
            self,
            "script_paths",
            self,
            "script_paths_index",
            rows=3,
        )
        col = row.column(align=True)
        col.operator("blender_menu.script_path_add", icon="ADD", text="")
        col.operator("blender_menu.script_path_remove", icon="REMOVE", text="")
        hint = box.column(align=True)
        hint.scale_y = 0.9
        hint.label(
            text="Top-level folders become header menus; scripts with main() become items.",
            icon="INFO",
        )
        hint.label(
            text="Paths are merged in list order; later entries override same-named scripts.",
        )
        hint.label(text="Use Refresh script menus after changing paths or folder contents.")

        status = ui.get_menu_build_state()
        status_box = layout.box()
        status_box.label(text="Menu build status", icon="FILE_REFRESH")
        status_box.label(text=status["message"])

        row = layout.row()
        row.operator("blender_menu.refresh_menus", text="Refresh script menus", icon="FILE_REFRESH")

        layout.prop(self, "show_menu_build_log")


def register():
    bpy.utils.register_class(BLENDERMENU_script_path)
    bpy.utils.register_class(BLENDERMENU_UL_script_paths)
    bpy.utils.register_class(BLENDERMENU_preferences)


def _find_addon_preferences():
    """Return (preferences, lookup_source) or (None, 'none')."""
    addons = getattr(bpy.context.preferences, "addons", None)
    if not addons:
        return None, "none"

    addon = addons.get(_ADDON_MODULE)
    if addon:
        return getattr(addon, "preferences", None), f"addons.get({_ADDON_MODULE})"

    for key in addons.keys():
        if key == "blender_menu" or key.endswith(".blender_menu"):
            addon = addons.get(key)
            if addon:
                return getattr(addon, "preferences", None), f"addons.get({key})"

    return None, "none"


def get_preferences():
    """Return this add-on's preferences instance or None."""
    prefs, _source = _find_addon_preferences()
    return prefs


def get_script_roots() -> tuple[list[str], str]:
    """Return (resolved_paths, lookup_source). Paths are absolute; blank entries omitted."""
    prefs, source = _find_addon_preferences()
    if prefs is None:
        return [], source

    paths: list[str] = []
    for item in prefs.script_paths:
        raw = (item.path or "").strip()
        if not raw:
            continue
        paths.append(os.path.abspath(os.path.expanduser(raw)))
    return paths, source


def unregister():
    for cls in (
        BLENDERMENU_preferences,
        BLENDERMENU_UL_script_paths,
        BLENDERMENU_script_path,
    ):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
