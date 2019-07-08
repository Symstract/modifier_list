# Changelog

## 1.3 - 8.7.2019

### New Features and Changes

- **Objects can now be pinned to the sidebar tab and to the popup** by clicking the pin icon in the header. When an object is pinned, the panels don't follow object selection but keep showing the modifiers (and vertex groups) of the pinned object instead. It works the same way as context pinning in Properties Editor.
- **Lattice modifier's UI/UX has been improved**
  - A lattice object can now be added to a lattice modifier by using the Add Gizmo operator or by holding shift when adding the modifier.
  - It goes into the gizmo object collection
  - It's automatically scaled to fit to the active object or to the selected elements if the object is in edit mode and at least two vertices are selected. A vertex group is also automatically created from the selection.
  - The lattice is aligned to the object. Unfortunately, there's no auto alignment or any way to define the alignment currently.
  - The lattice automatically goes into edit mode when it's added.
  - You can go in and out of lattice edit mode by by using the Edit Lattice button. It automatically utilizes object pinning, so the modifier settings keep being shown also when you're editing the lattice. Note: this operator doesn't fully support redo.
  - The settings of the lattice object are shown among the modifier settings, so everything is in the same place.
  - When applying or removing the modifier, hold shift to remove the lattice object and the vertex group (unless the group was manually created and its name doesn't start with "ML") at the same time.
  - If for some reason the context pinning doesn't automatically turn back off, just click the pin icon in the header to unpin the context.
- **Modifier Tools addon is no longer needed with this addon.** Similar batch operators are now included in this addon. Also, Apply All Modifiers now works in edit mode too.
- **Gizmo object can now be added to the location of the 3D Cursor** when holding shift while clicking the Add Gizmo button.
- **UI layout has been improved to use less space**
  - Apply, Apply As Shape Key, Copy and Add Gizmo buttons now use icons only.
  - The Add Gizmo button is moved into the same row with Apply, Apply As Shape Key and Copy buttons.
  - The row which shows modifier icon, name and visibility toggles can now be hidden from the addon preferences.
- **There is now a setting to use black icons**
- **Setting to adjust the width of the popup**
- **Setting for showing three favourites in a row**
- **Setting to not use icons in favourites** (to save space)
- **Setting to automatically match the size of the gizmo to the object.** Note: this can be a bit slow on heavy meshes.
- **Setting for always deleting the gizmo even when shift is not held**

### Fixes

- List ordering buttons behave better when the panel is narrow.

## 1.2.2 - 17.6.2019

- Fixed Multiresolution modifier operators not working.

## 1.2.1 - 13.6.2019

- Fixed the effect of a gizmo object not being taken into account when applying a modifier if the gizmo is deleted at the same time (by holding shift).

## 1.2 - 11.6.2019

### New Features and Changes

- Modifier List is now also inside the properties editor, replacing the regular modifier UI! Grease Pencil still uses the regular UI for now. If you'd rather use the regular UI for all modifiers, there is a setting for it in the preferences.
- Adding a control object - or as I decided to call them, a gizmo object - is now fast and effortless!
   - There is now Add Gizmo button for adding a "gizmo object" to a modifier. It basically just adds an empty and assings it to the appropriate property of the modifier.
   - All gizmos go to a gizmo objects collection.
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