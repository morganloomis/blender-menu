# Operator: run a user script's main() in an isolated namespace with bpy.
# Does not import the script into the add-on module graph.

import bpy


class BLENDERMENU_OT_run_script(bpy.types.Operator):
    bl_idname = "blender_menu.run_script"
    bl_label = "Run script"
    bl_description = "Run the script's main() function"

    script_path: bpy.props.StringProperty(name="Script path", options={"HIDDEN"})

    def execute(self, context):
        path = self.script_path
        if not path:
            self.report({"WARNING"}, "No script path")
            return {"CANCELLED"}
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
        except OSError as e:
            self.report({"ERROR"}, f"Cannot read script: {e}")
            return {"CANCELLED"}
        namespace = {"__builtins__": __builtins__, "bpy": bpy}
        try:
            exec(compile(source, path, "exec"), namespace)
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        main = namespace.get("main")
        if not callable(main):
            self.report({"WARNING"}, "Script has no main()")
            return {"CANCELLED"}
        try:
            main()
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        return {"FINISHED"}


class BLENDERMENU_OT_refresh_menus(bpy.types.Operator):
    bl_idname = "blender_menu.refresh_menus"
    bl_label = "Refresh script menus"
    bl_description = "Rebuild script menus from all configured script directories"

    def execute(self, context):
        from . import ui

        count = ui.rebuild_menus()
        state = ui.get_menu_build_state()
        if count > 0:
            self.report({"INFO"}, state["message"])
        else:
            self.report({"WARNING"}, state["message"])
        return {"FINISHED"}


class BLENDERMENU_OT_script_path_add(bpy.types.Operator):
    bl_idname = "blender_menu.script_path_add"
    bl_label = "Add script directory"
    bl_description = "Add a script directory to the list"

    def execute(self, context):
        from . import preferences, ui

        prefs = preferences.get_preferences()
        if prefs is None:
            return {"CANCELLED"}
        prefs.script_paths.add()
        ui.schedule_rebuild()
        return {"FINISHED"}


class BLENDERMENU_OT_script_path_remove(bpy.types.Operator):
    bl_idname = "blender_menu.script_path_remove"
    bl_label = "Remove script directory"
    bl_description = "Remove the selected script directory from the list"

    def execute(self, context):
        from . import preferences, ui

        prefs = preferences.get_preferences()
        if prefs is None or not prefs.script_paths:
            return {"CANCELLED"}
        index = prefs.script_paths_index
        if index < 0 or index >= len(prefs.script_paths):
            index = len(prefs.script_paths) - 1
        prefs.script_paths.remove(index)
        ui.schedule_rebuild()
        return {"FINISHED"}


def register():
    bpy.utils.register_class(BLENDERMENU_OT_run_script)
    bpy.utils.register_class(BLENDERMENU_OT_refresh_menus)
    bpy.utils.register_class(BLENDERMENU_OT_script_path_add)
    bpy.utils.register_class(BLENDERMENU_OT_script_path_remove)


def unregister():
    for cls in (
        BLENDERMENU_OT_script_path_remove,
        BLENDERMENU_OT_script_path_add,
        BLENDERMENU_OT_refresh_menus,
        BLENDERMENU_OT_run_script,
    ):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
