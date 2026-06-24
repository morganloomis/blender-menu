## ADDED Requirements

### Requirement: Script root path preference

The add-on SHALL provide an add-on preference for the script root directory. The preference MUST use a path property (e.g. Blender `StringProperty` with `subtype='DIR_PATH'`) so the user can choose a folder. The script menu feature SHALL use only this path; there SHALL be no built-in or default path inside the add-on package.

#### Scenario: User can set script root in preferences
- **WHEN** the user opens Blender Preferences → Add-ons and selects this add-on
- **THEN** a script root path control (e.g. directory picker) is visible and the user can set or clear the path

#### Scenario: Add-on enables with empty path
- **WHEN** the script root path is empty or unset and the user enables the add-on
- **THEN** the add-on enables without error and no script menus are registered

### Requirement: Menu hierarchy from directory structure

The add-on SHALL build a menu hierarchy from the script root directory at registration time. For each direct subfolder of the script root, the add-on MUST create one top-level menu. For each subfolder of those folders, the add-on MUST create one submenu under the corresponding parent menu. Folder and script names in menus MUST be sorted lexicographically so order is stable and predictable.

#### Scenario: One menu per top-level folder
- **WHEN** the script root contains directories `A` and `B` and the add-on is enabled
- **THEN** the user sees two top-level menus (e.g. "A" and "B") in the documented menu location, in alphabetical order

#### Scenario: Submenus for nested folders
- **WHEN** the script root contains `A` and `A/Sub` and the add-on is enabled
- **THEN** the user sees a top-level menu for "A" and a submenu under it for "Sub"

#### Scenario: Menus are sorted
- **WHEN** the script root contains folders `Z`, `A`, `M` and the add-on is enabled
- **THEN** the top-level menus appear in alphabetical order (A, M, Z)

### Requirement: Script discovery without execution

The add-on SHALL discover Python scripts by scanning the script root and its subdirectories for `.py` files. A script SHALL be included as a menu item only if the file parses as Python and defines a function named `main`. Discovery MUST be performed by parsing file contents (e.g. with Python’s `ast` module) and MUST NOT import or execute user script code at registration time.

#### Scenario: Script with main() appears as menu item
- **WHEN** the script root (or a subfolder) contains a `.py` file that defines `def main():` and the add-on is enabled
- **THEN** that script appears as a menu item under the menu (or submenu) for its folder, with a stable label (e.g. script name without extension)

#### Scenario: Script without main() is ignored
- **WHEN** the script root contains a `.py` file that does not define `main`
- **THEN** that file does not appear as a menu item and does not cause registration to fail

#### Scenario: No user code runs at registration
- **WHEN** the script root contains `.py` files and the add-on is enabled
- **THEN** only parsing (e.g. AST) is used to detect `main()`; no user script code is executed during registration

### Requirement: Run script on menu item click

When the user activates a script menu item, the add-on SHALL execute that script’s `main()` function. Execution MUST run in the same thread as Blender’s UI and MUST provide access to Blender’s Python API (e.g. `bpy`) in the script’s namespace. The add-on MUST NOT import the user script into the add-on’s module graph; execution SHALL use an isolated namespace (e.g. via `exec` with a dedicated namespace) and then call `main()` from that namespace. If execution or `main()` raises an exception, the add-on MUST report the error to the user (e.g. via Blender’s report or a popup) and MUST NOT crash or leave the add-on in an invalid state.

#### Scenario: Click runs main()
- **WHEN** the user clicks a script menu item for a valid script that defines `main()`
- **THEN** the script is loaded, its top-level code runs once, `main()` is called, and the script has access to `bpy`

#### Scenario: Script error is reported
- **WHEN** the user clicks a script menu item and the script raises an exception (e.g. in `main()` or at top-level)
- **THEN** the add-on catches the exception, reports it to the user (e.g. in the UI or report box), and the add-on remains enabled and usable

### Requirement: Invalid script root does not crash add-on

If the script root path is set but does not exist or is not a directory, the add-on SHALL NOT raise an error at registration. The add-on MUST enable successfully and MUST register no script menus (or only a harmless placeholder) when the path is invalid.

#### Scenario: Invalid path on enable
- **WHEN** the script root path is set to a non-existent or non-directory path and the user enables the add-on
- **THEN** the add-on enables without exception and no script menus are built from that path

### Requirement: Documented menu placement

The add-on SHALL register the script menus in a single, documented Blender editor/space (e.g. 3D Viewport header). The placement MUST be documented so users know where to find the script menus (e.g. in add-on documentation or in the add-on’s preference description).

#### Scenario: Menus appear in documented location
- **WHEN** the script root is valid and contains at least one folder or script with `main()`, and the add-on is enabled
- **THEN** the script menus appear in the documented editor and menu slot (e.g. 3D Viewport → header menu)
