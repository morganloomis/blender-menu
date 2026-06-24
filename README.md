# blenderMenu

Blender add-on that turns a folder on disk into menus in the 3D Viewport. Put Python scripts in that folder (and subfolders); any script that defines `main()` becomes a menu item. Click to run it.

**Workflow (using the add-on):**

1. **Set the script root**  
   In Blender: **Edit → Preferences → Add-ons** → enable **blenderMenu** → set **Script root** to a folder you control (e.g. a folder in your Documents or project).  
   Use a path outside the add-on so your scripts survive add-on updates.

2. **Add folders and scripts**  
   - **Folders** under the script root become top-level menus; **subfolders** become submenus (sorted alphabetically).  
   - **Python files** (`.py`) that define a `main()` function become menu items; scripts without `main()` are ignored.

3. **Run a script**  
   Open the 3D Viewport → header → **Scripts** (or the menu name that matches your folder). Click a script name to run its `main()` in Blender (with `bpy` available). Errors are reported in the UI; the add-on stays enabled.

4. **Refresh the menus**  
   Menus are built when the add-on is enabled. After adding or removing scripts or folders, disable and re-enable the add-on to refresh.

---

## Development workflow (OpenSpec)

This project uses [OpenSpec](https://openspec.dev) for change management: each feature or fix is a **change** with a set of **artifacts** that define why, what, how, and what to implement.

**Schema:** `spec-driven`  
**Artifact order:** `proposal` → `design` → `specs` → `tasks` → implement.

| Artifact   | Purpose |
|-----------|---------|
| **proposal** | Why the change; what changes; which capabilities (new/updated); impact. |
| **design**   | How to implement: decisions, risks, migration. No line-by-line code. |
| **specs**    | One spec per capability: requirements (SHALL/MUST) and scenarios (WHEN/THEN). |
| **tasks**    | Checkboxed implementation list; apply phase works through these. |

**Commands (from repo root):**

- **Start a new change:**  
  `openspec new change "my-change-name"`  
  Creates `openspec/changes/my-change-name/` with the default schema.

- **See status and next steps:**  
  `openspec status --change "my-change-name"`

- **Get instructions for an artifact:**  
  `openspec instructions <artifact-id> --change "my-change-name"`  
  e.g. `openspec instructions proposal --change "my-change-name"`

- **Implement (work through tasks):**  
  `openspec instructions apply --change "my-change-name"`  
  Then implement each task and mark it done in `tasks.md` (`- [ ]` → `- [x]`).

- **When done:**  
  Sync specs to main and/or archive the change (see OpenSpec docs).

**Where things live:**

- **Change artifacts:** `openspec/changes/<change-name>/`  
  - `proposal.md`, `design.md`, `tasks.md`  
  - `specs/<capability>/spec.md` for each capability
- **Main specs:** `openspec/specs/`  
  - Canonical requirements; updated when changes are synced or archived.
- **Config:** `openspec/config.yaml`  
  - Schema and context (e.g. Blender 5.0, Python, 3D tools).

Use **proposal** to agree scope and capabilities, **design** to lock approach, **specs** to define testable behavior, and **tasks** to drive implementation.
