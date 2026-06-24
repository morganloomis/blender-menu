# blenderMenu add-on
# This module is the add-on entry point. bl_info and register/unregister live here only.

bl_info = {
    "name": "blenderMenu",
    "author": "",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D",
    "description": "Script menus from a folder: menus per folder, menu items for scripts with main(). Script menus appear in the 3D Viewport header.",
    "warning": "",
    "doc_url": "",
    "category": "Interface",
}

import bpy

from . import preferences
from . import operators
from . import ui


def register():
    # Order: register preferences first, then operators, then UI (menus).
    preferences.register()
    operators.register()
    ui.register_ui()


def unregister():
    # Order: unregister in reverse — UI first, then operators, then preferences.
    ui.unregister_ui()
    operators.unregister()
    preferences.unregister()
