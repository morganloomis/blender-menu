## Context

The project has no Blender add-on code yet; this is greenfield. Tech stack is Blender 5.0 and Python. The proposal defines a single new capability, **addon-boilerplate**: a standard scaffold with manifest, module layout, register/unregister lifecycle, and optional preferences and UI hooks. This design describes how to implement that scaffold so it can be copied or generated for future add-ons.

## Goals / Non-Goals

**Goals:**
- Provide a minimal, copy-pasteable add-on structure: one entry package with `bl_info`, `register()`, and `unregister()`.
- Define a clear place for preferences (e.g. addon preferences class and draw) and for UI entry points (menu/pie registration stubs) so extensions stay consistent.
- Keep the boilerplate small enough to understand in one read and to evolve into a generator later if desired.

**Non-Goals:**
- Implementing real menu/pie logic or operators (only registration hooks).
- A CLI or script to generate new add-ons from the boilerplate (optional follow-up).
- Supporting Blender versions before 5.0.

## Decisions

1. **Single-package layout**  
   One top-level package (e.g. `blender_menu/` or a generic name) containing `__init__.py` (with `bl_info`, `register`, `unregister`), and optional modules such as `preferences.py` and `ui.py`. Alternative: multiple sibling packages from the start. Chosen: single package to keep the first add-on simple; more packages can be added when we have a second add-on or a generator.

2. **`bl_info` in `__init__.py` only**  
   Blender expects `bl_info` in the root module loaded by the add-on. We keep it in the package’s `__init__.py` and do not duplicate it elsewhere. Alternative: separate `bl_info.py` imported from `__init__.py`. Chosen: one file to edit for version/name to avoid drift.

3. **Registration order**  
   Register preferences first, then operators/panels/menus; unregister in reverse order. This follows Blender’s usual pattern and avoids dependency issues. Document this order in comments in the boilerplate.

4. **Preferences and UI as optional modules**  
   `preferences.py` defines an `ADDON_PREFERENCES`-style class; `ui.py` (or similar) exposes empty or stub menu/pie registration so that “add menu here” is a single, obvious place. The main `__init__.py` imports and registers these only if the modules exist (or always if we keep them in the boilerplate but minimal). Chosen: include both in the boilerplate with minimal implementations so every add-on has the same extension points.

5. **Naming**  
   Package name will match the project/repo (e.g. `blender_menu`) for this first add-on. The boilerplate can use a placeholder or comment (e.g. `addon_id`) so that copying for another add-on only requires a find-replace.

## Risks / Trade-offs

- **Risk:** Boilerplate grows and becomes hard to trim for tiny add-ons.  
  **Mitigation:** Keep only manifest, register/unregister, one preferences class, and one UI hook; no extra operators or panels.

- **Trade-off:** No generator script in this change means new add-ons are created by copying files and renaming. Acceptable for now; a generator can be a later change.

- **Risk:** Blender 5.0 API changes in a point release.  
  **Mitigation:** Pin or document the target 5.0.x in the boilerplate comments; no external deps beyond `bpy`.

## Migration Plan

- **Deploy:** Add the new package and files under the repo root (or an agreed add-ons directory). Enable the add-on in Blender via Preferences → Add-ons. No migration of existing data or add-ons.
- **Rollback:** Disable or remove the add-on; no persistent state beyond Blender preferences if the add-on stores any (boilerplate can stay minimal to avoid that initially).

## Open Questions

- Final package name for this repo: `blender_menu` vs `blenderMenu` (Python favours snake_case, so `blender_menu` preferred unless we have a reason to match the repo name exactly).
- Whether to add a one-line “Hello World” operator in the boilerplate to prove load/register; or keep it to pure structure only. Recommend: one minimal operator so enabling the add-on does something visible with no extra design.
