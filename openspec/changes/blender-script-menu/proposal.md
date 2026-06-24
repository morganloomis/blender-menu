# Proposal: Blender Script Menu Add-on

## Why

Blender users often keep one-off or quick Python scripts in a folder, but running them requires manually opening the Text editor, loading the file, and executing—or remembering script paths and running from the system console. A configurable “script directory” that is scanned at startup and turned into menus gives a single place to drop scripts and run them with one click, with no manual registration. This reduces friction for quick scripts and keeps the Blender UI as the primary interface.

## What Changes

- Add a Blender add-on that, on startup (when the add-on is enabled), scans a user-configurable directory.
- For each folder in that directory, create a top-level menu; for each subfolder, create a submenu under the corresponding parent menu.
- Discover Python scripts in the directory tree: any `.py` file that defines a `main()` function becomes a menu item under the menu (or submenu) for its folder.
- When the user clicks a script menu item, the add-on executes that script’s `main()` function in a Blender-safe context (e.g., same thread and environment as other add-on code).
- The script root directory is configurable via add-on preferences (e.g., a path property), so users can point to their own script folder.
- Menu structure is built at registration time from the current folder layout; no manual menu registration per script.

## Capabilities

### New Capabilities

- **script-menu**: Dynamic menu hierarchy built from a configurable directory: one menu per folder, submenus per subfolder, and menu items for Python scripts that define `main()`, with execution of `main()` on click. Includes preference for the script root path and safe discovery/loading of scripts at startup.

### Modified Capabilities

- (None. The add-on will satisfy existing addon-boilerplate requirements and add this behavior without changing those specs.)

## Impact

- **Code**: New add-on package (or extension of existing boilerplate) with modules for preferences (script path), menu building (directory scan, folder/subfolder → menu/submenu), script discovery (find `.py` files and detect `main()`), and execution (invoke `main()` when a menu item is used). UI registration hook used to register the dynamic menus.
- **APIs**: Uses Blender’s `bpy` for menus, operators, and add-on preferences; Python’s filesystem and `importlib` (or equivalent) for safe script discovery and execution.
- **Dependencies**: Blender 5.0+, Python (stdlib only for file/import handling unless we specify otherwise).
- **Systems**: Add-on appears in Blender’s add-on list; menus appear in the chosen space (e.g., 3D Viewport or a designated editor). Scripts in the user’s directory run in Blender’s Python environment when their menu item is clicked.
