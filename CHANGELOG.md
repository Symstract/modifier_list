# Changelog


## 1.6.1 - 18.8.2020

Updates for Blender 2.9x.

### 2.90:

Modifiers: option to preserve custom normals for subsurf & multires
https://developer.blender.org/rB5c28955d3a018adf9986cc601837cde9fc011496

LibOverride and modifiers: Add copying of linked modifiers
https://developer.blender.org/rBcfbea0e

### 2.91:

Ocean Modifier: Add viewport resolution
https://developer.blender.org/rBa44299c

Cycles: add support for rendering deformation motion blur from Alembic caches.
https://developer.blender.org/rBSb5dcf746369e51c08285292cd78f621999dd09e9

Multires: Base Mesh Sculpting
https://developer.blender.org/rB976f0113e008b4ff2d96760b0e83d5466dda8c54


## 1.6 - 20.7.2020

### New Features and changes

- **There's a new Modifier Extras popover** next to the batch operators. It currently contains only three operators. More on them below.

- **Managing favourite modifiers has been greatly improved.** They can now be
    - reordered manually
    - sorted alphabetically
    - selected from an enum menu which shows all modifiers (so you have a good overview which ones you have in already favourites and which one you don't)  and has a setting to sort them automatically when you add or remove one
    - configured from a popup which can be accessed from the new Modifier Extras menu, so you don't need to open the preferences anymore for that.

- **There's two new operators for synchronizing one or all modifiers on instances** in the new Modifier Extras menu. (Note: custom bevel profiles don't get synchronized currently.)

- **Apply All Modifiers operator works now with instances** as well, based on the active object. It shows a popup like the Apply Modifier operator does.

- **Apply All Modifiers and Remove All Modifiers operators now operate on the active object too**, not only on the selected objects. Previously it was annoying that if the active object was not selected, the operators wouldn't work for it.

- **Gizmo object can now be added for curves (also for selected points), fonts, lattices and surfaces** as well, not just for meshes

- **You can now apply all but the hidden modifiers** if you hold Shift when using the Apply All Modifiers operator. The behaviour is reversed when the Disallow Applying Hidden Modifiers setting is on.

- **Sidebar panels' category can now be customized** in the preferences

- **Moving a modifier up and down now uses two different operators**, previously it was done by a same operator. So if you had added shortcuts, they need to be re-added.

- **Some UI polishing has been done**, mainly greying out buttons when they can't be used and adding "sub-panels" for preferences

#### For Blender 2.90 only

- **Bevel modifier layout has been improved.** The setting are now ordered based on which of them are used the most and which of them fit together.

- **Point Clouds are now supported** (experimental feature)

- **Added support for the new Save As Shape Key operator**

- **Ocean modifier layout has been updated to include the new spray map settings**

- **Simulate category has been renamed to Physics**

- **Inserting a modifier after the active one might be faster now.** Probably no noticable difference in most cases in practice though.

### Fixes

- Fixed applying modifiers broken in Blender 2.90
- Fixed error when the Keep Sidebar Visible setting was on and there was no active object
- Fixed error when deleting a gizmo using the popup
- Fixed error in the console when selecting a lattice gizmo using the popup
- Fixed curve modifiers shown in lattice modifier search
- Fixed the properties context change button missing for Fluid modifier in Blender 2.82 and later
- Fixed Copy button showing for Fluid modifier in Blender 2.82 and later
- Fixed the properties context change button missing for Soft Body modifier for other than meshes 


## 1.5.6 - 26.6.2020

Updates for latest 2.90:
- Fixed Bevel custom profile, the checkbox changed to an enum
- Fixed Bevel Width property name for Absolute method 

I'll make some layout changes to Bevel to improve it in the future.


## 1.5.5 - 7.6.2020

- Added support for Blender 2.90 after the new modifier panels
- A button for resetting the active modifier index is shown now if it gets out of range. That can happen e.g. if the last modifier is a physics modifier, it's active and you remove it from within the physics panel.

**Note**: currently there's one **issue with the new modifier panels**: if the active object has modifiers and you then activate Modifier List, the regular panels don't disappear from the UI. It can also lead to a crash. So if you see the regular panels there, restart Blender. I've reported the bug and it will be fixed as soon as possible.


## 1.5.4 - 2.5.2020

- Added support for linked objects and library overrides. Because of this, **the minimum Blender version required is now 2.81**.
- All modifier layouts now update automatically (until they will move from Python to C in Blender, which is happening quite soon probably)
- Fixed applying modifiers in edit mode not being possible in 2.83 and 2.90


## 1.5.3 - 21.4.2020

- Fixed "Surface" modifier appearing in modifier search and menu. It's not meant to be seen by users.


## 1.5.2 - 13.4.2020

**Blender 2.83 and earlier**
- Multires: don't show the sculpt level setting. Sculpting on other levels than the highest has been disabled in vanilla Blender since 2.81... I will release another patch once support for it has been added.

**Blender 2.83**
- Updated layouts for the following modifiers so they are in synch with the latest Blender:
  - Corrective Smooth
  - Explode
  - Hook
  - Laplacian Deform
  - Multires
  - Ocean
  - Surface Deform


## 1.5.1 - 16.12.2019

- Fix wrong modifier menu columns in 2.82 due to new Weld modifier


## 1.5 - 11.12.2019

- **Ability to apply modifiers even if the object's data is used by multiple objects.** In this case, a popup with two options is shown: "Apply To Active Object Only (Break Link)" and "Apply To All Objects"
- **Extra settings/operators for boolean objects** inside Boolean layout: visibility toggle, display type, shade smooth / shade flat and select
- **Ability to move a modifier to top/bottom** by holding shift when pressing "Move Modifier"
- **"Reset Transform" operator inside the gizmo settings menu**
- **Ability to directly add a gizmo at world center** by holding Shift + Alt when adding a modifier or just Alt if adding the gizmo separately
- **Setting to keep Sidebar tab always visible**
- **Setting to disallow applying hidden modifiers**, which affects both "Apply Modifier" and "Apply All Modifiers"
- **"Apply on Spline" option for curve modifiers, which was missing, is now there**
- **Deleting objects that are not actual gizmo objects (empties with "_Gizmo" in their name) is now prevented**
- **"Move up" and "Move Down" operators have been combined**, so if someone had added shortcuts for them, they need to be added again
- **Operators don't show unnecessary "Adjust Last Operation" panel any more**
- **"Show In Edit Mode" is not shown for Boolean any more** (it doesn't work for it)
- **Fix for ResourceWarning related to loading icons on register in console**


## 1.4.2 - 5.9.2019

- Removed the offset from lattices. It was there so the lattice wouldn't overlap the mesh, but it didn't allow precise snapping. Now it does.


## 1.4.1 - 26.8.2019

- Fixed converting particles to mesh not working if render type is "Path"
- Fixed only Remesh modifier working in the sculpting branch
- Fixed Hook Gizmo having parent transformation applied
- Fixed error when removing a modifier and its gizmo from a pinned object if there's no active object
- Some tooltip fixes


## 1.4 - 14.8.2019

### New Features and Changes

- **Preferences are now auto saved into your Blender config folder**, eg: "...\AppData\Roaming\Blender Foundation\Blender\ < blender version > \config\modifier_list\preferences.json"
  - Preferences from another version can be imported using the "Import Preferences" operator
  - This means disabling this addon will no longer make you lose your settings
- **Gizmos are now placed at the average location of the selected elements in edit mode.**
- **New modifiers can now be inserted after the active one** by enabling the "Insert New Modifier After Active" setting.
  - Hold control to override this. (When off, the behaviour is reversed).
  - Modifier search doesn't support overriding
  - This is really slow on heavy meshes.
- **The order of the list can now be reversed persistently** by enabling the "Reverse List" setting.
- **Disabled modifiers (eg. Boolean with no object assigned) now have their icon shown in red inside the list as well as their name field inside the settings region.**
- **Remesh Modifier in Pablo Dobarro's sculpting branch is now fully supported**
-  **You can now choose which batch operator's show info messages**


## 1.3.1 - 13.7.2019

- Fixed Multiresolution modifier missing its layout
- Fixed Particle System modifier missing "Convert" button
- Fixed the following modifiers still having operators that don't work:
  - Corrective Smooth
  - Data Transfer ("Generate Data Layers" doesn't work perfectly though: it's not automatic, it opens a menu instead),
  - Explode,
  - Hook,
  - Ocean,
  - Skin
- Added the missing button that changes Properties Editor's tab for simulation modifiers that use it (for Properties Editor)
- Fixed the regular UI not being restored when disabling the addon


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