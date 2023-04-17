# Changelog

## 1.7.5 - 17.4.2023

- Curves object is now supported
- Geometry Nodes: Move to Nodes operator is now supported (disabled in the popup and sidebar when an object is pinned. It doesn't work in that case.)
- Geometry Nodes: Hide in Modifier toggle is now supported
- Geometry Nodes: fixed string properties not working
- Geometry Nodes: now uses the dedicated icon
- Geometry Nodes: attributes starting with a dot are now filtered out
- Geometry Nodes: moved field toggles to the right
- Geometry Nodes: fixed an error in the console when the modifier has no node group
- Fixed point cloud missing the modifier menu
- Fixed modifier stack staying visible after switching to the list
- Fixed modifier settings being disabled for objects with a library override
- Fixed the modifier stack displaying an extra icon for each modifier
- Error raising when adding modifier to non-editable override object is now handled
- Disabled the Copy to Selected operator in the popup and sidebar when an object is pinned. It doesn't work in that case.
- Fixed (presumably) a minor error arising when there is no objects in the scene at all, and when the cursor is placed in the Outliner context
- Fixed an error with lattice edit mode toggling when there is a pinned object
- Fixed modifier default selector showing some unsuitable settings (enums) for Data Transfer. Those have options that could lead to errors.
- Shift + A now opens the modifier menu in the Property Editor (add manually to other editors)
- Shift + Ctrl + A now opens the modifier search in the Property Editor (add manually to other editors)
- Assigning a hotkey for the Copy Modifier and Modifier Move Up/Down operators is now possible
- Modifier search now supports adding a gizmo object

## 1.7.4 - 1.4.2022

- Fixed Mesh Sequence Cache missing some settings in 3.1

## 1.7.3 - 3.2.2022

- Updated Mesh Sequence Cache for Blender 3.1 (Alembic override layers, layout changes)
- Fixed Geometry Nodes' attribute search not working properly. Previously, vertex groups were not supported with the list layout because the attribute search only shows attributes. Also, only existing ones could be selected, new ones couldn't be created. To support vertex groups and adding new attributes, the layout now uses a text input field for names and next to each one there is a button to search both attributes and vertex groups.
- Fixed error when applying modifier for instances without matching modifier
- Fixed some Geometry Nodes inputs sometimes breaking.

## 1.7.2 - 28.11.2021

Updates for Blender 3.0 (and 2.93 if mentioned).

### Geometry Nodes

- Added support for adding the modifier to curve objects
- Added support for image, material and texture inputs
- Added support for attribute inputs
- Added support for outputs
- Added icons for data-block inputs (also in 2.93)
- Node group selector now uses the proper data-block selector (also in 2.93)
- Fixed some Geometry Nodes inputs not working
- Removed warning when node group has multiple geometry inputs. Other modifier warning are not shown either, so this was an exception.
- The modifier is now shown as disabled when it has no node tree (also in 2.93)

### Other

- Added "Smooth" checkbox for Mask Modifier
- Added vertex group control for the MeshCache modifier

### Fixes

- Fixed wrong modifier being active after copying a modifier
- Preferences are now (again) written to the .json when changing a property, not only when disabling the addon

## 1.7.1 - 18.8.2021

Fixes for the list layout.

- Fixed Boolean missing Edit Mode toggle. This has been available since Blender 2.91. Awful mistake from me to miss this as this is useful.
- Fixed Weld missing On Cage toggle
- Fixed Volume to Mesh, Mesh to Volume and Volume Displace showing Edit Mode toggle

## 1.7 - 5.8.2021

### New features and changes

- **Optional stack layout**
  - It uses the default modifier stack (so layouts are always up to date)
  - There are separate settings for Properties Editor, sidebar and popup in the preferences
  - Setting for the current layout (Properties Editor, sidebar or popup) can also be found in the Modifier Extras popover
  - Currently only the Properties Editor setting is enabled because the stack layout is not working outside of Properties Editor because of a bug in Blender
  - Modifier Extras popover is located in the same row with modifier search and menu
  - Gizmo settings are in the popover
  - Batch operators are located either where they are now or in the popover. The "Show Batch Operators In Main Layout With Stack Style" setting controls that.
  - There's also an operator for expanding/collapsing all modifier panels
  - When switching from stack to list, the panels don't seem to get removed. Disabling and re-enabling the addon fixed that. Seems like a bug I need to report.
- **Customizable modifier default settings**
  - Can be found in the preferences
  - In some cases one setting affects another, which can be confusing. Example: Wertex Weight Proximity's proximity_geometry enum's 'FACE' option is synched with the invert_mask_vertex_groupin setting. Hopefully these kind of situations are rare.
- **When applying a modifier to all instances, the modifier is now removed from the instances** (based on the name and type)
- **Adding shortcuts to modifier applying operators is now possible** because they don't need the modifier name as an argument any more. (Btw, it's recommended to add shortcuts under 3D View > 3D View (Global) in the keymap editor so they work in all modes.)
- **Modifiers are now sorted alphabetically in the search**
- **Some mode enums are now expanded** for convenience in Weld, Mask, Remesh, Solidify and Cast modifiers' UI.
- **Surface Deform: Interpolation Falloff is now deactivate when the mesh is not bound** like it's in the default UI
- **Weighted Normal: autosmooth is now enabled before adding the modifier, not after** to avoid the usual warning in the console
- **Normal Edit: autosmooth is now enabled automatically**

### Updates for Blender 3.0

- Added "Sparse Bind" checkbox for Surface Deform
- Added "Only Loose Edges" checkbox for Weld

### Fixes

- Fixed Geometry Nodes object and collection inputs appearing disabled
- Fixed a possible error when reloading the addon. Now it should always work.

**The minimum required Blender version is now 2.92.**

## 1.6.4 - 22.5.2021

Updates for Blender 2.93 and 3.0 mainly.

### 2.93

- Added missing bisect distance parameter to Mirror
- Added missing Hole Tolerant parameter to Boolean

### 3.0

- Fixed a broken Blender version check which caused the addon not to even register
- Fixed the documentation link missing due to a changed dictionary key in bl_info ("wiki_url" -> "doc_url"). Because of this change, **the minimum Blender version required is now 2.83**.

### Other

- UV Project: aspect/scale settings are only activated when using a camera projector as done in the default UI now.

- Prevented an error if the preference file happens to have become corrupted and can't be read

- Batch operator idname changes:
  - object.ml_toggle_all_modifiers -> view3d.ml_toggle_all_modifiers
  - object.ml_apply_all_modifiers -> view3d.ml_apply_all_modifiers
  - object.ml_remove_all_modifiers -> view3d.ml_remove_all_modifiers
    This is to make shortcuts work by default in all modes when added via the context menu. (It was already possible to make them work by adding them under 3D View in the hotkey editor manually.) Note that adding them via the context menu doesn't seem to be possible in the properties editor.

## 1.6.3 - 25.2.2021

Updates for Blender 2.92 and 2.93

- **Modifier: Add "Connected" mode to the weld modifier**
  https://developer.blender.org/rB9b11a77

- **Add Custom Falloff Curve to the Vertex Weight Proximity Modifier.**
  https://developer.blender.org/rBe4204a3

- **Add operator to copy a modifier to all selected objects**
  https://developer.blender.org/rB6fbeb6e2e05408af448e9409f8e7e11470f82db6

  - This can be found in the Modifier Extras popover

- **Added Geometry Nodes support**

  - Node editor context is set correctly
  - The currently experimental Point Cloud object in 2.93 is also supported

- **Added tooltip for Configure Favourite Modifiers**

## 1.6.2 - 25.11.2020

Updates for Blender 2.9x mainly.

### 2.91:

- **Fixed volume modifiers showing for meshes**

- **Weighted Normal: fixed "Face Influence" setting missing in Blender 2.91**

- **Weld modifier: removed "Duplicate Limit" which no longer exists**

- **Merge newboolean branch into master.**
  https://developer.blender.org/rB9e09b5c418c0a436e3c84ccf38c065527988b0a0

  - the extra settings (hiding, setting display type etc.) also have collection equivalents now

- **Subdivision Surfaces: add boundary smooth option to modifiers**
  https://developer.blender.org/rB6070f92ab94be7bd1d6729f178d71c71c4245fbb

- **Subdivision Surfaces: add option disable using the limit surface**
  https://developer.blender.org/rB53f20b940a1e520e131b8bb31cf0529ed4d30f9e
  (only Subdivision Surface)

- Fix T71981: Alembic override frame causes fluid sim mesh to have artifacts
  **(Add an option to disable Alembic vertex interpolation.)**
  https://developer.blender.org/D9041

- **Volumes: new Mesh to Volume modifier**
  https://developer.blender.org/D9032

- **Volumes: new Volume Displace modifier**
  https://developer.blender.org/rB1f50beb9f28edd2fe54d97647222ad6ee5808c1c

- **Volumes: new Volume to Mesh modifier**
  https://developer.blender.org/D9141

### 2.92:

- **Multires: Remove simple subdivision type**
  https://developer.blender.org/rB17381c7b90eb3acde53eca013ae5a5a55699f17d

### Other:

- **Removed Simulation modifier as it's now longer in master.** It was available for the point cloud object which is not there anymore either. (Point cloud object will come back later, currently it's only in the geometry-nodes branch.)

- **Removed modifiers from point cloud object.** It currently has only one modifier in the branch: Empty/Nodes modifier. Support for that will come later.

- **Multires:**

  - layout was improved by moving all options to the left column in order to make the columns more even
  - "Rebuild Subdivisions" operator is now hidden when there's already subdivisions
  - settings are now set inactive the same way as in the regular UI
  - "Optimal Display" setting is now above the "UV Smooth" option

- **Subdivision Surface:**
  - "Quality" setting is now visible also when Cycles experimental features are enabled
  - settings are now set inactive the same way as in the regular UI when using Cycles adaptive subdivision

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
  - selected from an enum menu which shows all modifiers (so you have a good overview which ones you have in already favourites and which one you don't) and has a setting to sort them automatically when you add or remove one
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
- **Deleting objects that are not actual gizmo objects (empties with "\_Gizmo" in their name) is now prevented**
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
- **You can now choose which batch operator's show info messages**

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

Only Blender 2.8 is supported from now on. Also, the name is changed from Modifier Popup Panel to Modifier List since this addon now also has a tab in the sidebar. Because of that, when you install this new version, you need to remove the old version and add your favourite modifiers again.

By the way, the popup is now vertically a bit more compact. A bit too compact, I think, but that's unavoidable with the tabs.

### New Features and Changes

- This addon now has a tab in the sidebar (which can be disabled from addon preferences)
- Popup now has tabs
- Added a tab for vertex groups to the popup and a panel for them to the sidebar

## 1.0.1 - 28-2-2019

The following changes only apply to the Blender 2.8 version.

- Changed hotkey to alt + space because that's not in use by default in 2.8.
- Disabled editing it from preferences for now because of a bug in 2.8 which causes problems with that.
