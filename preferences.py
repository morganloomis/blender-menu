# Add-on preferences. Register/unregister are called from the main package __init__.py.

import bpy


class BLENDERMENU_preferences(bpy.types.AddonPreferences):
    bl_idname = "blenderMenu"

    script_root: bpy.props.StringProperty(
        name="Script root",
        description="Folder to scan for scripts. One menu per subfolder; scripts with main() become menu items. Script menus appear in the 3D Viewport header.",
        default="",
        subtype="DIR_PATH",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "script_root")


def register():
    bpy.utils.register_class(BLENDERMENU_preferences)


def get_preferences():
    """Return this add-on's preferences instance or None."""
    addons = getattr(bpy.context.preferences, "addons", None)
    if not addons:
        return None
    addon = addons.get("blenderMenu")
    return getattr(addon, "preferences", None) if addon else None


def unregister():
    bpy.utils.unregister_class(BLENDERMENU_preferences)
