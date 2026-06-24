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


def register():
    bpy.utils.register_class(BLENDERMENU_OT_run_script)


def unregister():
    try:
        bpy.utils.unregister_class(BLENDERMENU_OT_run_script)
    except RuntimeError:
        pass
