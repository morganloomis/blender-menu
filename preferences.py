# Add-on preferences. Register/unregister are called from the main package __init__.py.

import bpy

# Extension installs use a qualified module name (e.g. bl_ext.user_default.blender_menu).
# Legacy add-on installs use the short package name. __package__ matches both at runtime.
_ADDON_MODULE = __package__


class BLENDERMENU_preferences(bpy.types.AddonPreferences):
    bl_idname = _ADDON_MODULE

    script_root: bpy.props.StringProperty(
        name="Script root",
        description=(
            "Folder to scan for scripts. Each subfolder becomes a menu; "
            "each .py file with main() becomes a menu item. "
            "Menus appear in the 3D Viewport header."
        ),
        default="",
        subtype="DIR_PATH",
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Turn a folder on disk into script menus in the 3D Viewport.")
        box.prop(self, "script_root")
        hint = box.column(align=True)
        hint.scale_y = 0.9
        hint.label(
            text="Folders become menus; scripts with main() become items.",
            icon="INFO",
        )
        hint.label(text="Disable and re-enable the add-on to refresh after changes.")


def register():
    bpy.utils.register_class(BLENDERMENU_preferences)


def get_preferences():
    """Return this add-on's preferences instance or None."""
    addons = getattr(bpy.context.preferences, "addons", None)
    if not addons:
        return None
    addon = addons.get(_ADDON_MODULE)
    return getattr(addon, "preferences", None) if addon else None


def unregister():
    try:
        bpy.utils.unregister_class(BLENDERMENU_preferences)
    except RuntimeError:
        pass
