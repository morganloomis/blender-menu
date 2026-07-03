# Blender Tree Menus

Blender add-on that turns folders on disk into menus in the 3D Viewport. Put Python scripts in those folders (and subfolders); any script that defines `main()` becomes a menu item. Click to run it.

## Install

Install or update the add-on from Blender’s extension system:

1. Open **Edit → Preferences → Get Extensions → Repositories**.
2. Click **Add Remote Repository** and paste the **full** repository URL:

   `https://morganloomis.github.io/blender-menu/index.json`

3. In **Edit → Preferences → System → Network**, ensure **Allow Online Access** is enabled.
4. Open the **Repositories** menu (▼) → **Refresh Remote**, then install **Blender Tree Menus** from the catalog.

## Usage

1. **Configure script directories**  
   In Blender: **Edit → Preferences → Add-ons** → enable **Blender Tree Menus** → use **Script directories** to add one or more folders you control (e.g. an official tools folder plus a personal folder in Documents).  
   Use paths outside the add-on so your scripts survive add-on updates.

2. **Multiple paths and merge order**  
   - Paths are scanned in **list order** and merged into one menu tree.  
   - **Later entries override** scripts with the same menu label in the same folder (useful when a personal folder listed after an official folder should replace a shared script).  
   - Invalid or missing paths are skipped; menus still build from valid paths.

3. **Add folders and scripts**  
   - **Top-level folders** under each script directory become **header menus** in the 3D Viewport. **Subfolders** become submenus (sorted alphabetically by folder name on disk).  
   - **Menu labels** are formatted for display: camelCase and snake_case names become separate capitalized words (e.g. `rigControls` → **Rig Controls**, `export_fbx` → **Export Fbx**). Sort order still follows the raw on-disk names.  
   - **Python files** (`.py`) that define a `main()` function become menu items; scripts without `main()` are ignored. Script labels use the same formatting (from the filename without `.py`).  
   - **Ignored paths:** dot-prefixed names (e.g. `.hidden`), underscore-prefixed names (e.g. `_internal`), and `__pycache__` directories are skipped during discovery and never appear in menus.  
   - Scripts placed directly under a script directory root (not in a subfolder) appear under a header menu labeled **Scripts** (root-level scripts from all configured paths merge into one **Scripts** menu).

4. **Run a script**  
   Open the 3D Viewport → header → the menu that matches your folder name (or **Scripts** for root-level files). Click a script name to run its `main()` in Blender (with `bpy` available). Errors are reported in the UI; the add-on stays enabled.

5. **Refresh the menus**  
   Menus rebuild when the add-on is enabled and after loading a `.blend` file. After changing script directories, adding/removing paths, or changing scripts on disk, open the add-on preferences and click **Refresh script menus**. The status line shows how many menus were registered, from how many paths, or why none were built (including any skipped invalid paths).

## Troubleshooting

| Status message | What to check |
|----------------|---------------|
| **No menus: no script directories configured** | Add at least one script directory in add-on preferences. |
| **No menus: all paths invalid (...)** | Every configured path does not exist or is not a folder. Fix paths or create the folders. |
| **No menus: no scripts with main() in configured directories** | Paths exist but none contain `.py` files with a `def main():` function. Add qualifying scripts or use subfolders that contain them. |
| **... skipped invalid: ...** | Some paths were invalid but menus were built from the remaining valid paths. Fix or remove the skipped paths. |

Enable **Show menu build log** in preferences (or run Blender with a non-zero debug value) to print rebuild details (all configured paths, skipped paths, and counts) to the system console.
