## ADDED Requirements

### Requirement: Add-on manifest

The add-on SHALL expose a `bl_info` dictionary in the root module loaded by Blender. The manifest MUST include at least `bl_info["version"]`, `bl_info["name"]`, and `bl_info["blender"]` (minimum version tuple) so that Blender can list and version the add-on.

#### Scenario: Blender loads the add-on
- **WHEN** the add-on is enabled in Blender Preferences → Add-ons
- **THEN** Blender loads the root module and reads `bl_info` without error, and the add-on appears in the list with name and version

#### Scenario: Manifest is the single source of version
- **WHEN** the add-on is installed
- **THEN** version and name are defined only in `bl_info` (no duplicate version/name in other modules that Blender uses for display)

### Requirement: Single-package layout

The add-on SHALL be implemented as one top-level Python package. The package MUST contain an `__init__.py` that is the add-on entry point (the module Blender loads). The package MAY contain additional modules (e.g. `preferences.py`, `ui.py`) for preferences and UI registration.

#### Scenario: Add-on is loadable as one package
- **WHEN** the add-on path is added to Blender’s add-on search path and the add-on is enabled
- **THEN** Blender imports the package’s `__init__.py` and no import errors occur for the package or its referenced modules

### Requirement: Register and unregister lifecycle

The add-on SHALL define a `register()` function and an `unregister()` function in the root module. When Blender enables the add-on it MUST call `register()`; when the add-on is disabled or Blender exits it MUST call `unregister()`. Registration order MUST register preferences first, then operators, panels, and menus; unregistration MUST occur in the reverse order.

#### Scenario: Enable add-on runs register
- **WHEN** the user enables the add-on in Preferences → Add-ons
- **THEN** Blender calls `register()` once and no unhandled exception is raised

#### Scenario: Disable add-on runs unregister
- **WHEN** the user disables the add-on in Preferences → Add-ons
- **THEN** Blender calls `unregister()` once and all previously registered classes are unregistered without error

#### Scenario: Unregister reverses register order
- **WHEN** `unregister()` is called after a successful `register()`
- **THEN** menus/panels/operators are unregistered before preferences (reverse of register order)

### Requirement: Optional add-on preferences

The add-on SHALL support an optional add-on preferences class (e.g. `bpy.types.AddonPreferences` subclass). If present, the preferences class MUST be registered in `register()` and unregistered in `unregister()`, and the add-on MUST expose a way to draw preferences in Blender’s Preferences → Add-ons panel (e.g. `draw()` on the preferences class).

#### Scenario: Preferences appear when defined
- **WHEN** the boilerplate includes a preferences class and the add-on is enabled
- **THEN** the user can open Preferences → Add-ons, select this add-on, and see the add-on’s preference UI (or an empty/minimal draw) without error

#### Scenario: Add-on works without preferences module
- **WHEN** the boilerplate is used without a preferences class (or the preferences module is omitted)
- **THEN** `register()` and `unregister()` complete successfully and the add-on enables and disables without requiring preferences

### Requirement: UI registration hook

The add-on SHALL provide a single, documented place (e.g. a module or function) where menu, pie menu, or other UI registration is performed. This hook MUST be called from `register()` and the corresponding unregistration MUST be called from `unregister()` so that extending the add-on with menus or pies follows one consistent pattern.

#### Scenario: UI hook is called on register
- **WHEN** `register()` is called and the UI hook is implemented (e.g. register_ui / unregister_ui)
- **THEN** the UI registration code is invoked during `register()` and UI unregistration is invoked during `unregister()`

#### Scenario: Boilerplate documents UI extension point
- **WHEN** a developer reads the boilerplate to add a menu or pie
- **THEN** one clearly identified module or function (e.g. `ui.py` or `register_ui()`) is the designated place to add menu/pie registration and unregistration
