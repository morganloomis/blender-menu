## Why

We need a standard, repeatable starting point for Blender add-ons in this project. Without a boilerplate, each new add-on would reinvent structure, manifest, and registration, leading to inconsistency and duplicated setup. Defining it once lets us ship new add-ons faster and keep the codebase aligned with Blender 5.0 and project conventions.

## What Changes

- Introduce a documented add-on boilerplate: folder layout, `bl_info`, and a single entry module.
- Define standard register/unregister flow (operators, panels, preferences) and a minimal preferences schema.
- Add a clear place for menu/pie or other UI entry points so future add-ons can extend from the same pattern.
- Optionally provide a small script or template to generate a new add-on from the boilerplate (if in scope).

## Capabilities

### New Capabilities
- `addon-boilerplate`: Standard Blender add-on scaffold—manifest (`bl_info`), module layout, register/unregister lifecycle, and optional preferences and UI hooks.

### Modified Capabilities
- *(None; no existing specs in `openspec/specs/`.)*

## Impact

- **New**: Add-on root package(s), `__init__.py` with `bl_info` and register/unregister, optional `preferences.py` and UI modules. No existing code removed.
- **APIs**: Follows Blender 5.0 add-on API; no external service or custom API surface.
- **Dependencies**: Python standard library and Blender’s `bpy`; no new third-party deps.
- **Systems**: Affects only this repo’s add-on layout and future add-ons created from this boilerplate.
