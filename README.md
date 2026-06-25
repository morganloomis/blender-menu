# Blender Tree Menus

Blender add-on that turns a folder on disk into menus in the 3D Viewport. Put Python scripts in that folder (and subfolders); any script that defines `main()` becomes a menu item. Click to run it.

## Install

Install or update the add-on from Blender’s extension system:

1. Open **Edit → Preferences → Get Extensions → Repositories**.
2. Click **Add Remote Repository** and paste the **full** repository URL:

   `https://morganloomis.github.io/blender-menu/index.json`

3. In **Edit → Preferences → System → Network**, ensure **Allow Online Access** is enabled.
4. Open the **Repositories** menu (▼) → **Refresh Remote**, then install **Blender Tree Menus** from the catalog.

## Usage

1. **Set the script root**  
   In Blender: **Edit → Preferences → Add-ons** → enable **Blender Tree Menus** → set **Script root** to a folder you control (e.g. a folder in your Documents or project).  
   Use a path outside the add-on so your scripts survive add-on updates.

2. **Add folders and scripts**  
   - **Top-level folders** under the script root become **header menus** in the 3D Viewport (menu label = folder name). **Subfolders** become submenus (sorted alphabetically).  
   - **Python files** (`.py`) that define a `main()` function become menu items; scripts without `main()` are ignored.  
   - Scripts placed directly under the script root (not in a subfolder) appear under a header menu labeled **Scripts**.

3. **Run a script**  
   Open the 3D Viewport → header → the menu that matches your folder name (or **Scripts** for root-level files). Click a script name to run its `main()` in Blender (with `bpy` available). Errors are reported in the UI; the add-on stays enabled.

4. **Refresh the menus**  
   Menus rebuild when the add-on is enabled and after loading a `.blend` file. After changing the script root or adding/removing scripts on disk, open the add-on preferences and click **Refresh script menus**. The status line shows how many menus were registered or why none were built.

## Troubleshooting

| Status message | What to check |
|----------------|---------------|
| **No menus: script root not set** | Set **Script root** in add-on preferences to your scripts folder. |
| **No menus: path invalid (...)** | The path does not exist or is not a folder. Fix the path or create the folder. |
| **No menus: no scripts with main() in ...** | The folder exists but has no `.py` files with a `def main():` function. Add qualifying scripts or use subfolders that contain them. |

Enable **Show menu build log** in preferences (or run Blender with a non-zero debug value) to print rebuild details to the system console.
