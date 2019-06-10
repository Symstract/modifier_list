# Changelog

## 1.2 - (Unreleased)

### New Features and Changes

- Modifier List is now also inside the properties editor, replacing the regular modifier UI! Grease Pencil still uses the regular UI for now. If you'd rather use the regular UI for all modifiers, there is a setting for it in the preferences.
- Adding a control object - or as I decided to call them, a gizmo object - is now fast and effortless!
   - There is now Add Gizmo button for adding a "gizmo object" to a modifier. It basically just adds an empty and assings it to the appropriate property of the modifier.
   - By default, the gizmo is placed at the origin of the active object. But if you are in edit mode and have a single vertex selected, the gizmo is placed at the vertex location.
   - You can also hold shift when adding a modifier to add a gizmo at the same time, so you can save an extra click :)
   - After adding a gizmo, the Add Gizmo button changes to a visibility toggle and a settings popover, in which you can change some gizmo setting, such as its location, rotation and parenting. You can also select or delete the gizmo from the popover. Note: selecting and deleting give some (harmless) errors/glitches when used from the modifier popup.
   - There is a setting in the preferences for automatically parenting the gizmo to the active object on addition.
   - You can hold shift when applying or removing a modifier to also delete its gizmo.
- The popup now has header which you can use to move the popup.
- You can now use a dialog type popup which doesn't close when you don't hover over it. The setting is in the preferences.
- Auto Smooth is now enabled automatically when you add a Weighted Normal modifier.
- Applying a modifier in edit mode now works for all objet types.
- Modifier menu and the search don't show modifiers that don't work with the active object anymore.
- Updated the icon for Modifier Tools visibility toggle.

### Fixes
- Bind buttons of Mesh Deform, Laplacian Deform and Surface Deform now work.
- Various small fixes.

## 1.1.1 - 22.3.2019

- Fixed ModuleNotFoundError on Linux and Mac

## 1.1 - 21.3.2019

Only Blender 2.8 is supported from now on. Also, the name is changed from Modifier Popup Panel to Modifier List since this addon now also has a tab in  the sidebar. Because of that, when you install this new version, you need to remove the old version and add your favourite modifiers again.

By the way, the popup is now vertically a bit more compact. A bit too compact, I think, but that's unavoidable with the tabs.

### New Features and Changes

- This addon now has a tab in the sidebar (which can be disabled from addon preferences)
- Popup now has tabs
- Added a tab for vertex groups to the popup and a panel for them to the sidebar

## 1.0.1 - 28-2-2019

The following changes only apply to the Blender 2.8 version.

- Changed hotkey to alt + space because that's not in use by default in 2.8.
- Disabled editing it from preferences for now because of a bug in 2.8 which causes problems with that.