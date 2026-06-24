# Design: Blender Script Menu Add-on

## Context

Blender 5.0 add-on implemented in Python. The add-on will satisfy the existing addon-boilerplate requirements (bl_info, register/unregister, preferences, UI registration hook) and add dynamic menus driven by a user-chosen script directory. Scripts are untrusted in the sense that they are user-authored and can do anything Blender’s Python allows; the add-on must avoid running script code at registration time and must run it in a predictable context when the user clicks a menu item.

## Goals / Non-Goals

**Goals:**

- One configurable script root path (add-on preferences).
- At registration: scan the script root; build a menu per folder and submenu per subfolder; add a menu item for each `.py` file that defines `main()`.
- On menu item click: run that script’s `main()` in Blender’s Python environment (same thread, `bpy` available).
- Predictable menu order (e.g. alphabetical for folders and scripts).
- No manual per-script registration; structure is fully driven by filesystem layout.

**Non-Goals:**

- Script editor or IDE; no editing, debugging, or version control inside the add-on.
- Sandboxing or restricting what scripts can do (they run with full Blender access).
- Auto-refresh of menus when the filesystem changes (refresh by disabling/re-enabling the add-on, or a future “Refresh” operator).
- Supporting scripts that don’t define `main()` (e.g. other entry points); only `main()` is considered.

## Decisions

### 1. Where to register the menus

- **Decision:** Register the top-level script menus in a single, documented Blender space (e.g. 3D Viewport header) so users know where to find them.
- **Rationale:** Keeps the feature simple and discoverable. Alternative would be multiple menu placements or a user option; can be added later if needed.

### 2. How to discover scripts (detect `main()` without running code)

- **Decision:** At registration time, discover scripts by scanning the filesystem for `.py` files and using Python’s `ast` module to parse each file and check for a `main` function definition. Do not import or execute user scripts at registration.
- **Rationale:** Importing would run top-level code when the add-on loads, which is unsafe and would run scripts before the user clicks. AST parsing is read-only and avoids any execution.

### 3. How to execute a script when a menu item is clicked

- **Decision:** When the user clicks a menu item, load the script file, execute it in a dedicated namespace that includes `bpy` and standard builtins, then call `main()` from that namespace. Use `exec(compile(..., path, 'exec'), namespace)` (or equivalent) so the script runs in an isolated namespace but with Blender available; do not import the script into the add-on’s module graph.
- **Rationale:** Ensures top-level code runs only on click, not at menu build time. Keeps user code out of the add-on’s global namespace. Same-thread execution satisfies Blender’s UI requirements. Alternative of importing the module would run top-level code on first click and would require managing module cache and re-loading; exec-with-namespace is simpler and matches “run this file’s main() once per click.”

### 4. Menu build time and refresh

- **Decision:** Build the full menu tree once inside `register()` (after reading the script root from preferences). No automatic refresh when the directory changes; user can disable and re-enable the add-on to rebuild. A “Refresh script menus” operator can be added later as an enhancement.
- **Rationale:** Keeps initial implementation simple and avoids file watchers or polling. Re-enable is a clear, documented way to refresh.

### 5. Ordering of items in menus

- **Decision:** Sort folder names and script names (e.g. lexicographic) when building menus so order is stable and predictable.
- **Rationale:** Avoids arbitrary order that changes with filesystem or OS; alphabetical is familiar and easy to reason about.

### 6. Preferences and path validation

- **Decision:** One add-on preference: script root path (e.g. `bpy.types.StringProperty` with `subtype='DIR_PATH'`). At registration, if the path is set and exists and is a directory, scan it; otherwise register no menus (or a placeholder / message) so the add-on still enables without error.
- **Rationale:** Empty or invalid path must not crash the add-on. Subtype `DIR_PATH` gives a folder picker in Blender’s preferences UI.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| User script crashes or raises an exception | Wrap the call to `main()` in try/except; show an error (e.g. via Blender’s report or a small popup) so the add-on does not break and the user sees the failure. |
| User script runs long or blocks | Scripts run in the main thread; a long-running script will freeze the UI. Document this; consider documenting async or threading only if we add it later. |
| Top-level code in script runs on first click | Accepted: when we exec the file and then call `main()`, top-level runs once. Document that “click = run script (top-level + main()).” |
| Invalid or malicious path in preferences | Validate path at use time (exists, is dir); if invalid, skip building menus and do not raise. |
| Script directory on network or with special chars | Rely on Blender/OS path handling; document that local paths are best supported; no special handling in v1. |

## Migration Plan

- **Deploy:** Ship as a new add-on. User enables it, sets script root in preferences, re-enables if needed to build menus. No migration of existing data.
- **Rollback:** User disables the add-on; no persistent state beyond the preference (script path) which can be cleared or left as-is.

## Open Questions

- Exact menu placement (which editor and menu slot) to be fixed in implementation and documented in the spec or user docs.
- Whether to add a “Refresh script menus” operator in the first release or as a follow-up.
