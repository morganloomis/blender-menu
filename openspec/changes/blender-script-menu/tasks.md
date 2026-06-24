## 1. Add-on structure

- [x] 1.1 Add bl_info (name, version, blender) and single-package layout with __init__.py as entry point
- [x] 1.2 Implement register() and unregister(); register preferences first, then UI; unregister in reverse order
- [x] 1.3 Add a dedicated UI registration hook (e.g. register_ui / unregister_ui) called from register() / unregister()

## 2. Preferences

- [x] 2.1 Add AddonPreferences subclass with script root path (StringProperty, subtype='DIR_PATH')
- [x] 2.2 Implement draw() so the path control is visible in Preferences → Add-ons when this add-on is selected
- [x] 2.3 Ensure add-on enables without error when script root is empty or unset (no menus registered)

## 3. Script discovery

- [x] 3.1 Implement filesystem scan of script root and subdirectories for .py files (respect sorted order)
- [x] 3.2 Implement AST-based check: parse each .py file and detect if it defines a function named main (no import/exec)
- [x] 3.3 Build an in-memory tree of (folders → subfolders, scripts with main) for a given root path; skip invalid path or non-directory without raising

## 4. Menu hierarchy

- [x] 4.1 Define menu class(es) and submenu draw that reflect the discovery tree (one menu per folder, one submenu per subfolder, sorted)
- [x] 4.2 Add menu items for each discovered script (label = script name without .py); sort script items lexicographically
- [x] 4.3 Register the top-level script menus in the chosen Blender space (e.g. 3D Viewport header) from the UI hook
- [x] 4.4 On invalid or missing script root, register no script menus (add-on still enables)

## 5. Script execution

- [x] 5.1 Implement an operator that, given a script file path, loads the file and exec()s it in a namespace that includes bpy and builtins, then calls main()
- [x] 5.2 Ensure the operator runs in the main thread and does not import the user script into the add-on module graph
- [x] 5.3 Wrap execution in try/except; on exception, report to the user (e.g. bpy.ops.wm.report or report box) and leave add-on enabled

## 6. Integration and documentation

- [x] 6.1 In register_ui(), read script root from preferences; if valid directory, run discovery and register menus with operators wired to script paths
- [x] 6.2 In unregister_ui(), unregister all dynamic menus and operators in reverse order
- [x] 6.3 Document where script menus appear (e.g. in add-on description or preferences tooltip: "Script menus appear in the 3D Viewport header.")
