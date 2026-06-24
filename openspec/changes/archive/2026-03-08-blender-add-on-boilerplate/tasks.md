## 1. Package layout

- [x] 1.1 Create package directory `blenderMenu` at repo root (or agreed add-on path)
- [x] 1.2 Add `blenderMenu/__init__.py` as the add-on entry module
- [x] 1.3 Add `blenderMenu/preferences.py` for add-on preferences
- [x] 1.4 Add `blenderMenu/ui.py` for UI (menu/pie) registration hook

## 2. Add-on manifest and entry point

- [x] 2.1 Define `bl_info` in `blenderMenu/__init__.py` with `name`, `version`, and `blender` (min 5.0); no duplicate version/name elsewhere
- [x] 2.2 Implement `register()` and `unregister()` in `blenderMenu/__init__.py`; add comments documenting order: preferences first, then UI; unregister in reverse

## 3. Preferences

- [x] 3.1 In `preferences.py`, define an `AddonPreferences` subclass (e.g. for `blenderMenu`) with a minimal or empty `draw(self, context)`
- [x] 3.2 In `register()`, register the preferences class; in `unregister()`, unregister it (preferences before UI in register, after UI in unregister)

## 4. UI registration hook

- [x] 4.1 In `ui.py`, add `register_ui()` and `unregister_ui()` (stubs or empty) and a short comment that this is the place to add menu/pie registration
- [x] 4.2 From `__init__.py` `register()` call `register_ui()` after registering preferences; from `unregister()` call `unregister_ui()` before unregistering preferences

## 5. Verification

- [ ] 5.1 Enable the add-on in Blender 5.0 Preferences → Add-ons; confirm it loads and appears with correct name/version
- [ ] 5.2 Disable the add-on and confirm unregister runs without errors
