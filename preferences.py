# Add-on preferences. Register/unregister are called from the main package __init__.py.

import os

import bpy

# Extension installs use a qualified module name (e.g. bl_ext.user_default.blender_menu).
# Legacy add-on installs use the short package name. __package__ matches both at runtime.
_ADDON_MODULE = __package__


def _on_script_root_updated(self, context):
    from . import ui

    ui.schedule_rebuild()


class BLENDERMENU_preferences(bpy.types.AddonPreferences):
    bl_idname = _ADDON_MODULE

    script_root: bpy.props.StringProperty(
        name="Script root",
        description=(
            "Folder to scan for scripts. Each subfolder becomes a header menu; "
            "each .py file with main() becomes a menu item. "
            "Menus appear in the 3D Viewport header."
        ),
        default="",
        subtype="DIR_PATH",
        update=_on_script_root_updated,
    )

    show_menu_build_log: bpy.props.BoolProperty(
        name="Show menu build log",
        description="Print menu build details to the system console on each rebuild",
        default=False,
    )

    def draw(self, context):
        from . import ui

        layout = self.layout
        box = layout.box()
        box.label(text="Turn a folder on disk into script menus in the 3D Viewport.")
        box.prop(self, "script_root")
        hint = box.column(align=True)
        hint.scale_y = 0.9
        hint.label(
            text="Top-level folders become header menus; scripts with main() become items.",
            icon="INFO",
        )
        hint.label(text="Use Refresh script menus after changing the path or folder contents.")

        status = ui.get_menu_build_state()
        status_box = layout.box()
        status_box.label(text="Menu build status", icon="FILE_REFRESH")
        status_box.label(text=status["message"])

        row = layout.row()
        row.operator("blender_menu.refresh_menus", text="Refresh script menus", icon="FILE_REFRESH")

        layout.prop(self, "show_menu_build_log")


def register():
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


def get_script_root() -> tuple[str, str]:
    """Return (resolved_path, lookup_source). Path is empty when unset."""
    prefs, source = _find_addon_preferences()
    if prefs is None:
        return "", source

    raw = (prefs.script_root or "").strip()
    if not raw:
        return "", source

    return os.path.abspath(os.path.expanduser(raw)), source


def unregister():
    try:
        bpy.utils.unregister_class(BLENDERMENU_preferences)
    except RuntimeError:
        pass
