# Modifier List

### Enhanced UI layout for modifiers with handy features. Available also in the sidebar and as a popup.

---

[Download the latest release from here](https://github.com/Symstract/Modifier-List/releases)

[Changelog](/CHANGELOG.md)

[Blender Artists Thread](https://blenderartists.org/t/modifier-popup-panel-list-view-search-favourites/1147752)

---

![](properties_editor_and_sidebar.png)

![](popup.png)

#### _Disclaimer: When using the list layout, since Blender 2.90, every time a modifier gets a new feature I need to manually update the layout and I may not always do that immediately. So there may be a delay._

## Features

- **Modifier list or stack**
  - Modifiers can be displayed either as a list or as a stack
  - There are separate settings for Properties Editor, sidebar and popup in the addon preferences
  - Setting for the current layout (Properties Editor, sidebar or popup) can also be found in the Modifier Extras popover
  - Currently only the Properties Editor setting is enabled because the stack layout is not working outside of Properties Editor because of a bug in Blender
  - When switching from stack to list, the panels don't seem to get removed. Disabling and re-enabling the addon fixed that.
  - **List**
    - The settings of the active modifier are shown under the list, so you will see only one modifier at a time
    - The default list size inside the popup can be set in the addon preferences
    - The order of the list can be reversed persistently by enabling the "Reverse List" setting
  - **Stack**
    - It uses the default modifier stack, so modifier layouts are always up to date
    - Not all features of the addon are supported with the stack but most are
- **Modifier search**
- **Modifier menu**
- **Favourite modifiers** which can be set in the addon preferences or from a popup available from the Modifier Extras menu
- **Ability to apply modifiers in edit mode (kind of).** The apply operator acts as a macro when used in edit mode and automatically switches to object mode, applies the modifier and switches back to edit mode.
- **Ability to apply modifiers even if the object's data is used by multiple objects.** In this case, a popup with two options is shown: "Apply To Active Object Only (Break Link)" and "Apply To All Objects"
- **Operators for synchronizing one or all modifiers on instances.** These can be found in the Modifier Extras menu.
- **Ability to inserted new modifiers after the active one** by enabling the "Insert New Modifier After Active" setting.
  - Hold control to override this. (When off, the behaviour is reversed).
  - Modifier search doesn't support overriding
  - This is really slow on heavy meshes
- **Setting to disallow applying hidden modifiers**, which affects both "Apply Modifier" and "Apply All Modifiers". Hold Alt to override this. (When off, the behaviour is reversed.)
- **Ability to move a modifier to top/bottom** by holding shift when pressing "Move Modifier"
- **Modifier batch operators** Toggle All Modifiers, Apply All Modifiers and Remove All Modifiers. Apply All Modifiers works also in edit mode.
  - There's also an operator for expanding/collapsing all modifier panels when using the stack
  - When using the stack layout, the operators are located either in the top level layout, like with the list, or in the popover. The "Show Batch Operators In Main Layout With Stack Style" setting controls that.
- **Sidebar panels and a popup**, which contain also a vertex group list. The sidebar panels can be disabled in the addon preferences. The Sidebar category can be customized and there's also a setting to keep the panels always visible.
- **Object pinning for the sidebar tab and for the popup** by clicking the pin icon in the header. When an object is pinned, the panels don't follow object selection but keep showing the modifiers (and vertex groups) of the pinned object instead. It works the same way as context pinning in Properties Editor.
- **Easy way to add a control object** - or as I decided to call them, **a gizmo object** - to a modifier
  - There is Add Gizmo button for adding a "gizmo object" to a modifier. It basically just adds an empty and assings it to the appropriate property of the modifier (Mirror Object for Mirror modifier for example).
  - All gizmos go into a gizmo object collection
  - By default, the gizmo is placed at the origin of the active object. But if you are in edit mode and have something selected, the gizmo is placed at the average location of the selected elements (for meshes and curves).
  - If you hold alt while you click the Add Gizmo button, the gizmo is placed at world origin
  - If you hold shift while you click the Add Gizmo button, the gizmo is placed at the location of the 3D Cursor
  - You can also hold shift when adding a modifier to add a gizmo at the same time, so you can save an extra click :)
  - After adding a gizmo, the Add Gizmo button changes to a visibility toggle and a settings popover, in which you can change some gizmo setting, such as its location, rotation and parenting. You can also select or delete the gizmo from the popover.
  - When using the stack layout, gizmo settings are in the Modifier Extras popover
  - There is a setting in the addon preferences for automatically parenting the gizmo to the active object on addition
  - There is also a setting to automatically match the size of the gizmo to the object. Note: this can be a bit slow on heavy meshes.
  - You can hold shift when applying or removing a modifier to also delete its gizmo
- **Improved UI/UX for Lattice modifier**
  - A lattice object can be added to a lattice modifier by using the Add Gizmo operator or by holding shift when adding the modifier
  - It goes into the gizmo object collection
  - It's automatically scaled to fit to the active object or to the selected elements if the object is in edit mode and at least two vertices are selected. A vertex group is also automatically created from the selection.
  - The lattice is aligned to the object. Unfortunately, there's no auto alignment or any way to define the alignment currently.
  - The lattice automatically goes into edit mode when it's added
  - You can go in and out of lattice edit mode by by using the Edit Lattice button. It automatically utilizes object pinning, so the modifier settings keep being shown also when you're editing the lattice. Note: this operator doesn't fully support redo.
  - The settings of the lattice object are shown among the modifier settings, so everything is in the same place
  - When applying or removing the modifier, hold shift to remove the lattice object and the vertex group (unless the group was manually created and its name doesn't start with "ML") at the same time
  - If for some reason the context pinning doesn't automatically turn back off, just click the pin icon in the header to unpin the context
- **Customizable modifier default settings**
  - They can be found in the addon preferences
  - In some cases one setting affects another, which can be confusing. Example: Wertex Weight Proximity's proximity_geometry enum's 'FACE' option is synched with the invert_mask_vertex_groupin setting. Hopefully these kind of situations are rare.
- **Extra settings/operators for boolean objects** inside Boolean layout: visibility toggle, display type, shade smooth / shade flat and select
- **Auto Smooth is enabled automatically when you add a Weighted Normal or a Normal Edit modifier**
- **Black and white icons** to choose between

## Hotkeys

**Default hotkey for the popup is Alt + Space**. Inside the keymap editor, you can find it under 3D View > 3D View (Global) > Modifier Popup.

It's recommended to add shortcuts under the 3D View > 3D View (Global) category so they are availabe in all modes.

## Preferences are auto saved into your Blender config folder

- Example path: "...\AppData\Roaming\Blender Foundation\Blender\ < blender version > \config\modifier_list\preferences.json"
- Preferences from another version can be imported using the "Import Preferences" operator
- This means disabling Modifier List won't make you lose your settings

## Installation

1. Go to Edit menu (File menu in 2.79) and open user preferences
2. Switch to Addons tab and click Install...
3. Navigate to where you downloaded the zip file to, select it and click Install Add-on from File
4. Enable the add-on by ticking the checkbox next to its name
5. Save user preferences

## Known Issues and Limitations

- Inside the popup, lists don't remember their sizes after they are resized. Popups are not really ment for this kind of stuff, so that's a limitation of Blender.
- Using the popup, picking an object from viewport is not possible. A limitation of popups. Hopefully that could be possible at some point because that applies also to the driver editor popup and there's an open bug report about it in the bug tracker.
- Warnings like "Enable 'Auto Smooth' option in mesh settings" are not displayed
- Data Transfer's "Generate Data Layers" doesn't use automatic settings, instead it opens a menu
- Add Modifier's tooltip doesn't fit to Lattice
- Custom bevel profiles don't get synchronized when synchronizing modifiers between instances
