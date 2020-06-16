import math
import numpy as np

import bpy
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import (
    Menu,
    Operator,
    Panel,
    PropertyGroup,
    UIList
)

# Check if the modifier layouts can be imported from Blender. If not,
# import the layouts included in this addon. This is needed for 2.90 and
# later because the modifier layouts have been moved from Python into C
# in Blender 2.90 since 5.6.2020.
from bl_ui import properties_data_modifier
if hasattr(properties_data_modifier.DATA_PT_modifiers, "ARRAY"):
    from bl_ui.properties_data_modifier import DATA_PT_modifiers
else:
    from .properties_data_modifier import DATA_PT_modifiers

from . import ml_modifier_layouts
from .. import icons, modifier_categories
from ..operators import lattice_toggle_editmode, lattice_toggle_editmode_prop_editor
from ..utils import (
    delete_gizmo_object,
    delete_ml_vertex_group,
    get_gizmo_object,
    get_ml_active_object,
    get_vertex_group,
    is_modifier_local
)


# Utility functions
# =======================================================================

def is_modifier_disabled(mod):
    """Checks if the name of the modifier should be diplayed with a red
    background.
    """
    if mod.type == 'ARMATURE' and not mod.object:
        return True

    elif mod.type == 'BOOLEAN' and not mod.object:
        return True

    elif mod.type == 'CAST':
        if not any((mod.use_x, mod.use_y, mod.use_z)) or mod.factor == 0:
            return True

    elif mod.type == 'CURVE' and not mod.object:
        return True

    elif mod.type == 'DATA_TRANSFER' and not mod.object:
        return True

    elif mod.type == 'DISPLACE':
        if (mod.direction == 'RGB_TO_XYZ' and not mod.texture) or mod.strength == 0:
            return True

    elif mod.type == 'HOOK' and not mod.object:
        return True

    elif mod.type == 'LAPLACIANDEFORM' and not mod.vertex_group:
        return True

    elif mod.type == 'LAPLACIANSMOOTH':
        if not any((mod.use_x, mod.use_y, mod.use_z)) or mod.lambda_factor == 0:
            return True

    elif mod.type == 'LATTICE' and not mod.object:
        return True

    elif mod.type == 'MESH_CACHE' and (not mod.filepath or mod.factor == 0):
        return True

    elif mod.type == 'MESH_DEFORM' and not mod.object:
        return True

    elif mod.type == 'MESH_SEQUENCE_CACHE' and (not mod.cache_file or not mod.object_path):
        return True

    elif mod.type == 'NORMAL_EDIT' and (mod.mode == 'DIRECTIONAL' and not mod.target):
        return True

    elif mod.type == 'PARTICLE_INSTANCE':
        if not mod.object:
            return True

        if not mod.object.particle_systems:
            return True
        else:
            for m in mod.object.modifiers:
                if m.type == 'PARTICLE_SYSTEM' and m.particle_system == mod.particle_system:
                    if not m.show_viewport:
                        return True

    elif mod.type == 'SHRINKWRAP' and not mod.target:
        return True

    elif mod.type == 'SMOOTH':
        if not any((mod.use_x, mod.use_y, mod.use_z)) or mod.factor == 0:
            return True

    elif mod.type == 'SUBSURF' and mod.levels == 0:
        return True

    elif mod.type == 'SURFACE_DEFORM' and not mod.target:
        return True

    elif mod.type == 'VERTEX_WEIGHT_EDIT' and not mod.vertex_group:
        return True

    elif mod.type == 'VERTEX_WEIGHT_MIX' and not mod.vertex_group_a:
        return True

    elif mod.type == 'VERTEX_WEIGHT_PROXIMITY' and (not mod.vertex_group or not mod.target):
        return True

    return False


# UI elements
# =======================================================================


def show_in_editmode_button(modifier, layout, pcoll, use_in_list):
    row = layout.row(align=True)

    if modifier.type in modifier_categories.DONT_SUPPORT_SHOW_IN_EDITMODE:
        empy_icon = pcoll['EMPTY_SPACE']
        row.label(text="", translate=False, icon_value=empy_icon.icon_id)
        return

    if not use_in_list:
        row.active = modifier.show_viewport

    if not modifier.show_viewport and use_in_list:
        show_in_editmode_on = pcoll['SHOW_IN_EDITMODE_ON_INACTIVE']
        show_in_editmode_off = pcoll['SHOW_IN_EDITMODE_OFF_INACTIVE']
    else:
        show_in_editmode_on = pcoll['SHOW_IN_EDITMODE_ON']
        show_in_editmode_off = pcoll['SHOW_IN_EDITMODE_OFF']

    show = modifier.show_in_editmode
    icon = show_in_editmode_on.icon_id if show else show_in_editmode_off.icon_id
    row.prop(modifier, "show_in_editmode", text="", icon_value=icon, emboss=not use_in_list)


def use_apply_on_spline_button(modifier, layout, pcoll, use_in_list):
    row = layout.row(align=True)

    if modifier.type not in modifier_categories.SUPPORT_USE_APPLY_ON_SPLINE:
        empy_icon = pcoll['EMPTY_SPACE']
        row.label(text="", translate=False, icon_value=empy_icon.icon_id)
        return

    use_apply_on_spline_on = pcoll['USE_APPLY_ON_SPLINE_ON']
    use_apply_on_spline_off = pcoll['USE_APPLY_ON_SPLINE_OFF']
    apply_on = modifier.use_apply_on_spline
    icon = use_apply_on_spline_on.icon_id if apply_on else use_apply_on_spline_off.icon_id
    row.prop(modifier, "use_apply_on_spline", text="", icon_value=icon, emboss=not use_in_list)


def show_on_cage_button(object, modifier, layout, pcoll, use_in_list):
    support_show_on_cage = modifier_categories.SUPPORT_SHOW_ON_CAGE

    if modifier.type not in support_show_on_cage:
        return False

    mods = object.modifiers
    mod_index = mods.find(modifier.name)

    # Check if some modifier before this has show_in_editmode on
    # and doesn't have show_on_cage setting.
    is_before_show_in_editmode_on = False
    end_index = np.clip(mod_index, 1, 99)

    for mod in mods[0:end_index]:
        if mod.show_in_editmode and mod.type not in support_show_on_cage:
            is_before_show_in_editmode_on = True
            break

    if is_before_show_in_editmode_on:
        return False

    # Check if some modifier after this has show_in_editmode and
    # show_on_cage both on and also is visible in the viewport.
    is_after_show_on_cage_on = False

    for mod in mods[(mod_index + 1):(len(mods))]:
        if (mod.show_viewport and mod.show_in_editmode and mod.show_on_cage):
            is_after_show_on_cage_on = True
            break

    # Button
    row = layout.row(align=True)
    show_on_cage_on = pcoll['SHOW_ON_CAGE_ON']
    show_on_cage_off = pcoll['SHOW_ON_CAGE_OFF']

    if (not modifier.show_viewport or not modifier.show_in_editmode
            or is_after_show_on_cage_on):
        if use_in_list:
            show_on_cage_on = pcoll['SHOW_ON_CAGE_ON_INACTIVE']
            show_on_cage_off = pcoll['SHOW_ON_CAGE_OFF_INACTIVE']
        else:
            row.active = False

    icon = show_on_cage_on.icon_id if modifier.show_on_cage else show_on_cage_off.icon_id
    row.prop(modifier, "show_on_cage", text="", icon_value=icon, emboss=not use_in_list)

    return True


def properties_context_change_button(modifier, layout, use_in_list):
    if bpy.context.area.type != 'PROPERTIES' or use_in_list:
        return False

    have_phys_context_button = {
        'CLOTH',
        'COLLISION',
        'FLUID_SIMULATION',
        'DYNAMIC_PAINT',
        'SMOKE',
        'SOFT_BODY'
    }

    if modifier.type in have_phys_context_button:
        row = layout.row(align=True)
        row.operator("wm.properties_context_change", icon='PROPERTIES',
                        emboss=False).context = "PHYSICS"
        return True

    if modifier.type == 'PARTICLE_SYSTEM':
        row = layout.row(align=True)
        row.operator("wm.properties_context_change", icon='PROPERTIES',
                        emboss=False).context = "PARTICLES"
        return True

    return False


def modifier_visibility_buttons(modifier, layout, use_in_list=False):
    """This handles the modifier visibility buttons (and also the
    properties_context_change button) to match the behaviour of the
    regular UI .

    When called, adds those buttons, for the given modifier, in their
    correct state, to the specified (sub-)layout.

    Note: some modifiers show show_on_cage in the regular UI only if,
    for example, an object to use for deforming is specified. Eg.
    Armatature modifier requires an armature object to be specified in
    order to show the button. This function doesn't take that into
    account but instead shows the button always in those cases. It's
    easier to achieve and hardly makes a difference.
    """
    pcoll = icons.preview_collections["main"]
    empy_icon = pcoll['EMPTY_SPACE']

    # Main layout
    row = layout.row(align=True)
    row.scale_x = 1.0 if use_in_list else 1.2

    # show_render and show_viewport
    sub = row.row(align=True)

    # Hide visibility toggles for collision modifier as they are not
    # used in the regular UI either (apparently can cause problems
    # in some scenes).
    if modifier.type == 'COLLISION':
        sub.label(text="", translate=False, icon_value=empy_icon.icon_id)
        sub.label(text="", translate=False, icon_value=empy_icon.icon_id)
    else:
        sub.prop(modifier, "show_render", text="", emboss=not use_in_list)
        sub.prop(modifier, "show_viewport", text="", emboss=not use_in_list)

    # show_in_editmode
    show_in_editmode_button(modifier, row, pcoll, use_in_list)

    ob = get_ml_active_object()

    # No use_apply_on_spline or show_on_cage for lattices
    if ob.type == 'LATTICE':
        return

    # use_apply_on_spline
    if ob.type != 'MESH':
        use_apply_on_spline_button(modifier, row, pcoll, use_in_list)
        return

    # show_on_cage or properties_context_change
    show_on_cage_added = show_on_cage_button(ob, modifier, row, pcoll, use_in_list)
    context_change_added = False
    if not show_on_cage_added:
        context_change_added = properties_context_change_button(modifier, row, use_in_list)

    # Make icons align nicely if neither show_on_cage nor properties_context_change was added
    if not show_on_cage_added and not context_change_added:
        sub = row.row(align=True)
        sub.label(text="", translate=False, icon_value=empy_icon.icon_id)


class MeshModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class CurveModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class LatticeModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


def add_modifier(self, context):
    # Add modifier
    wm = bpy.context.window_manager
    mod_name = wm.ml_mod_to_add

    if mod_name == "":
        return None

    mod_type = wm.ml_mesh_modifiers[mod_name].value
    bpy.ops.object.ml_modifier_add(modifier_type=mod_type)

    # Executing an operator via a function doesn't create an undo event,
    # so it needs to be added manually.
    bpy.ops.ed.undo_push(message="Add Modifier")


class MESH_MT_ml_add_modifier_menu(Menu):
    bl_label = "Add Modifier"
    bl_description = "Add a procedural operation/effect to the active object"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.alignment = 'LEFT'

        col = row.column()
        col.label(text="Modify")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.MESH_MODIFY_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Generate")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.MESH_GENERATE_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Deform")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.MESH_DEFORM_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Simulate")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.MESH_SIMULATE_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod


class CURVE_MT_ml_add_modifier_menu(Menu):
    bl_label = "Add Modifier"
    bl_description = "Add a procedural operation/effect to the active object"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.alignment = 'LEFT'

        col = row.column()
        col.label(text="Modify")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.CURVE_MODIFY_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Generate")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.CURVE_GENERATE_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Deform")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.CURVE_DEFORM_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Simulate")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.CURVE_SIMULATE_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod


class LATTICE_MT_ml_add_modifier_menu(Menu):
    bl_label = "Add Modifier"
    bl_description = "Add a procedural operation/effect to the active object"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.alignment = 'LEFT'

        col = row.column()
        col.label(text="Modify")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.LATTICE_MODIFY_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Deform")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.LATTICE_DEFORM_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Simulate")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.LATTICE_SIMULATE_NAMES_ICONS_TYPES:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod


class OBJECT_UL_modifier_list(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if mod:
                row = layout.row()
                row.alert = is_modifier_disabled(mod)
                row.label(text="", translate=False, icon_value=layout.icon(mod))

                layout.prop(mod, "name", text="", emboss=False, icon_value=icon)

                modifier_visibility_buttons(mod, layout, use_in_list=True)
            else:
                layout.label(text="", translate=False, icon_value=icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class ModifierListActions:
    """Base operator for list actions."""

    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    action = None

    @classmethod
    def poll(cls, ontext):
        ob = get_ml_active_object()

        if not ob.modifiers:
            return False

        mod = ob.modifiers[ob.ml_modifier_active_index]
        return is_modifier_local(ob, mod)

    def execute(self, context):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences
        ml_active_ob = get_ml_active_object()

        # Make using operators possible when an object is pinned
        override = context.copy()
        override['object'] = ml_active_ob

        # Get the active object in 3d View so Properties Editor's
        # context pinning won't mess things up.
        if context.area.type == 'PROPERTIES':
            context.area.type = 'VIEW_3D'
            ob = context.object
            context.area.type = 'PROPERTIES'
        else:
            ob = context.object

        mods = ml_active_ob.modifiers
        mods_len = len(mods) - 1
        active_mod_index = ml_active_ob.ml_modifier_active_index
        active_mod_index_up = np.clip(active_mod_index - 1, 0, mods_len)
        active_mod_index_down = np.clip(active_mod_index + 1, 0, mods_len)

        if not mods:
            return {'CANCELLED'}

        active_mod = ml_active_ob.modifiers[active_mod_index]
        active_mod_name = active_mod.name

        if self.action == 'UP':
            if self.shift:
                for _ in range(active_mod_index):
                    bpy.ops.object.modifier_move_up(override, modifier=active_mod_name)
                ml_active_ob.ml_modifier_active_index = 0
            else:
                bpy.ops.object.modifier_move_up(override, modifier=active_mod_name)
                ml_active_ob.ml_modifier_active_index = active_mod_index_up

        elif self.action == 'DOWN':
            if self.shift:
                for _ in range(mods_len - active_mod_index):
                    bpy.ops.object.modifier_move_down(override, modifier=active_mod_name)
                ml_active_ob.ml_modifier_active_index = mods_len
            else:
                bpy.ops.object.modifier_move_down(override, modifier=active_mod_name)
                ml_active_ob.ml_modifier_active_index = active_mod_index_down

        elif self.action == 'REMOVE':
            if self.shift or prefs.always_delete_gizmo:
                # When using lattice_toggle_editmode(_prop_editor)
                # operator, the mode the user was in before that is
                # stored inside that module. That can also be
                # utilised here, so we can return into the correct
                # mode after deleting a lattice in lattice edit
                # mode.
                if ob and ob.type == 'LATTICE':
                    if context.area.type == 'PROPERTIES':
                        if lattice_toggle_editmode_prop_editor.init_mode == 'EDIT_MESH':
                            switch_into_editmode = True
                        else:
                            switch_into_editmode = False
                    elif lattice_toggle_editmode.init_mode == 'EDIT_MESH':
                        switch_into_editmode = True
                    else:
                        switch_into_editmode = False
                else:
                    switch_into_editmode = False

                gizmo_ob = get_gizmo_object()
                delete_gizmo_object(self, gizmo_ob)

                if active_mod.type == 'LATTICE':
                    context.view_layer.objects.active = ml_active_ob
                    vert_group = get_vertex_group()
                    delete_ml_vertex_group(ml_active_ob, vert_group)
                    if switch_into_editmode:
                        bpy.ops.object.editmode_toggle()

            bpy.ops.object.modifier_remove(override, modifier=active_mod_name)
            ml_active_ob.ml_modifier_active_index = active_mod_index_up

        return {'FINISHED'}

    def invoke(self, context, event):
        self.shift = event.shift

        return self.execute(context)


class OBJECT_OT_ml_modifier_move(Operator, ModifierListActions):
    bl_idname = "object.ml_modifier_move"
    bl_label = "Move Modifier"
    bl_description = ("Move modifier up/down in the stack.\n"
                      "\n"
                      "Hold Shift to move it to the top/bottom")

    action_items = [
        ("UP", "Up", ""),
        ("DOWN", "Down", "")
    ]
    action: EnumProperty(items=action_items, default='UP', options={'HIDDEN', 'SKIP_SAVE'})


class OBJECT_OT_ml_modifier_remove(Operator, ModifierListActions):
    bl_idname = "object.ml_modifier_remove"
    bl_label = "Remove Modifier"
    bl_description = ("Remove modifier from the active object.\n"
                     "\n"
                     "Hold shift to also delete its gizmo object (if it has one)")

    action = 'REMOVE'


class OBJECT_PT_ml_modifier_extras(Panel):
    bl_label = "Modifier Extras"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.ml_favourite_modifiers_selection_popup")


class OBJECT_PT_ml_gizmo_object_settings(Panel):
    bl_label = "Gizmo Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        layout = self.layout

        ob = get_ml_active_object()
        gizmo_ob = get_gizmo_object()

        layout.prop(gizmo_ob, "name", text="")

        if gizmo_ob.type == 'EMPTY':
            layout.prop(gizmo_ob, "empty_display_type", text="")
            layout.prop(gizmo_ob, "empty_display_size", text="Display Size")

        layout.separator()

        layout.operator("object.ml_gizmo_object_reset_transform", text="Reset Transform")

        layout.label(text="Location:")
        col = layout.column()
        col.prop(gizmo_ob, "location", text="")

        layout.label(text="Rotation:")
        col = layout.column()
        col.prop(gizmo_ob, "rotation_euler", text="")

        layout.label(text="Parent")

        is_ob_parented_to_gizmo = True if ob.parent == gizmo_ob else False
        is_gizmo_parented_to_ob = True if gizmo_ob.parent == ob else False

        col = layout.column(align=True)

        sub = col.row()
        if is_ob_parented_to_gizmo:
            sub.enabled = False
        depress = is_gizmo_parented_to_ob
        unset = is_gizmo_parented_to_ob
        sub.operator("object.ml_gizmo_object_parent_set", text="Gizmo To Active Object",
                        depress=depress).unset = unset

        sub = col.row()
        if is_gizmo_parented_to_ob:
            sub.enabled = False
        depress = is_ob_parented_to_gizmo
        unset = is_ob_parented_to_gizmo
        sub.operator("object.ml_gizmo_object_child_set", text="Active Object To Gizmo",
                        depress=depress).unset = unset

        layout.separator()

        layout.operator("object.ml_select", text="Select Gizmo").object_name = gizmo_ob.name

        if gizmo_ob.type in {'EMPTY', 'LATTICE'} and "_Gizmo" in gizmo_ob.name:
            layout.operator("object.ml_gizmo_object_delete")


# UI
# =======================================================================

def modifiers_ui(context, layout, num_of_rows=False, use_in_popup=False):
    wm = bpy.context.window_manager
    ob = get_ml_active_object()
    active_mod_index = ob.ml_modifier_active_index
    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    pcoll = icons.preview_collections["main"]

    # Ensure the active index is never out of range. That can happen if
    # a modifier gets deleted without using Modifier List, e.g. when
    # removing a Cloth modifier from within the physics panel.
    if ob.modifiers and active_mod_index > len(ob.modifiers) - 1:
        layout.label(text="The active modifier index has gotten out of range...")
        layout.operator("object.ml_reset_modifier_active_index")
        return

    if ob.modifiers:
        # This makes operators work without passing the active modifier
        # to them manually as an argument.
        layout.context_pointer_set("modifier", ob.modifiers[ob.ml_modifier_active_index])

    # === Favourite modifiers ===
    col = layout.column(align=True)

    # Check if an item or the next item in
    # favourite_modifiers_names_icons_types has a value and add rows
    # and buttons accordingly (2 or 3 buttons per row).
    fav_names_icons_types_iter = modifier_categories.favourite_modifiers_names_icons_types()

    place_three_per_row = prefs.favourites_per_row == '3'

    for name, icon, mod in fav_names_icons_types_iter:
        next_mod_1 = next(fav_names_icons_types_iter)
        if place_three_per_row:
            next_mod_2 = next(fav_names_icons_types_iter)

        if name or next_mod_1[0] or (place_three_per_row and next_mod_2[0]):
            row = col.row(align=True)

            if name:
                icon = icon if prefs.use_icons_in_favourites else 'NONE'
                row.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod
            else:
                row.label(text="")

            if next_mod_1[0]:
                icon = next_mod_1[1] if prefs.use_icons_in_favourites else 'NONE'
                row.operator("object.ml_modifier_add", text=next_mod_1[0],
                                icon=icon).modifier_type = next_mod_1[2]
            else:
                row.label(text="")

            if place_three_per_row:
                if next_mod_2[0]:
                    icon = next_mod_2[1] if prefs.use_icons_in_favourites else 'NONE'
                    row.operator("object.ml_modifier_add", text=next_mod_2[0],
                                icon=icon).modifier_type = next_mod_2[2]
                else:
                    row.label(text="")

    # === Modifier search and menu ===
    col = layout.column()
    row = col.split(factor=0.59)
    row.enabled = ob.library is None or ob.override_library is not None
    if ob.type == 'MESH':
        row.prop_search(wm, "ml_mod_to_add", wm, "ml_mesh_modifiers", text="", icon='MODIFIER')
        row.menu("MESH_MT_ml_add_modifier_menu")
    elif ob.type in {'CURVE', 'SURFACE', 'FONT'}:
        row.prop_search(wm, "ml_mod_to_add", wm, "ml_curve_modifiers", text="", icon='MODIFIER')
        row.menu("CURVE_MT_ml_add_modifier_menu")
    elif ob.type == 'LATTICE':
        row.prop_search(wm, "ml_mod_to_add", wm, "ml_lattice_modifiers", text="", icon='MODIFIER')
        row.menu("LATTICE_MT_ml_add_modifier_menu")

    # === Modifier list ===
    # Get the list index from wm.ml_active_object_modifier_active_index
    # instead of ob.ml_modifier_active_index because library overrides
    # prevent editing that value directly.
    # wm.ml_active_object_modifier_active_index has get and set methods
    # for accessing ob.ml_modifier_active_index indirectly.
    layout.template_list("OBJECT_UL_modifier_list", "", ob, "modifiers",
                         wm, "ml_active_object_modifier_active_index", rows=num_of_rows,
                         sort_reverse=prefs.reverse_list)

    # When sub.scale_x is 1.5 and the area/region is narrow, the buttons
    # don't align properly, so some manual work is needed.
    if use_in_popup:
        align_button_groups = prefs.popup_width <= 250
    elif context.area.type == 'VIEW_3D':
        align_button_groups = context.region.width <= 283
    else:
        align_button_groups = context.area.width <= 291

    row = layout.row(align=align_button_groups)

    # === Modifier batch operators ===
    sub = row.row(align=True)
    sub.scale_x = 3 if align_button_groups else 1.34

    icon = pcoll['TOGGLE_ALL_MODIFIERS_VISIBILITY']
    sub.operator("object.ml_toggle_all_modifiers", icon_value=icon.icon_id, text="")

    icon = pcoll['APPLY_ALL_MODIFIERS']
    sub.operator("object.ml_apply_all_modifiers", icon_value=icon.icon_id, text="")

    icon = pcoll['DELETE_ALL_MODIFIERS']
    sub.operator("object.ml_remove_all_modifiers", icon_value=icon.icon_id, text="")

    sub_sub = sub.row(align=True)
    sub_sub.scale_x = 0.65 if align_button_groups else 0.85
    sub_sub.popover("OBJECT_PT_ml_modifier_extras", icon='DOWNARROW_HLT', text="")

    # === List manipulation ===
    sub = row.row(align=True)
    sub.scale_x = 3 if align_button_groups else 1.5
    if not align_button_groups:
        sub.alignment = 'RIGHT'

    move_up_icon = 'TRIA_DOWN' if prefs.reverse_list else 'TRIA_UP'
    move_down_icon = 'TRIA_UP' if prefs.reverse_list else 'TRIA_DOWN'

    if not prefs.reverse_list:
        sub.operator("object.ml_modifier_move", icon=move_up_icon, text="").action = 'UP'
        sub.operator("object.ml_modifier_move", icon=move_down_icon, text="").action = 'DOWN'
    else:
        sub.operator("object.ml_modifier_move", icon=move_down_icon, text="").action = 'DOWN'
        sub.operator("object.ml_modifier_move", icon=move_up_icon, text="").action = 'UP'

    sub.operator("object.ml_modifier_remove", icon='REMOVE', text="")

    # === Modifier settings ===
    if not ob.modifiers:
        return

    active_mod = ob.modifiers[active_mod_index]
    all_mods = modifier_categories.ALL_MODIFIERS
    active_mod_icon = next(icon for _, icon, mod in all_mods if mod == active_mod.type)
    is_active_mod_local = is_modifier_local(ob, active_mod)

    col = layout.column(align=True)

    # === General settings ===
    box = col.box()

    if not prefs.hide_general_settings_region:
        row = box.row()

        sub = row.row()
        sub.alert = is_modifier_disabled(active_mod)
        sub.label(text="", icon=active_mod_icon)
        sub.prop(active_mod, "name", text="")

        modifier_visibility_buttons(active_mod, row)

    row = box.row()

    sub = row.row(align=True)

    if active_mod.type == 'PARTICLE_SYSTEM':
        ps = active_mod.particle_system
        if ps.settings.render_type in {'COLLECTION', 'OBJECT'}:
            sub.operator("object.duplicates_make_real", text="Convert")
        elif ps.settings.render_type == 'PATH':
            sub.operator("object.modifier_convert", text="Convert").modifier = active_mod.name
    else:
        sub.scale_x = 5
        icon = pcoll['APPLY_MODIFIER']
        sub.operator("object.ml_modifier_apply", text="",
                    icon_value=icon.icon_id).modifier = active_mod.name

        if active_mod.type in modifier_categories.SUPPORT_APPLY_AS_SHAPE_KEY:
            icon = pcoll['APPLY_MODIFIER_AS_SHAPEKEY']
            sub.operator("object.ml_modifier_apply_as_shapekey", text="",
                        icon_value=icon.icon_id).modifier = active_mod.name

        if active_mod.type not in modifier_categories.DONT_SUPPORT_COPY:
            sub.operator("object.ml_modifier_copy",
                        text="", icon='DUPLICATE').modifier = active_mod.name

    # === Gizmo object settings ===
    if ob.type == 'MESH':
        if (active_mod.type in modifier_categories.HAVE_GIZMO_PROPERTY
                or active_mod.type == 'UV_PROJECT'):
            gizmo_ob = get_gizmo_object()

            sub = row.row(align=True)
            sub.alignment = 'RIGHT'
            sub.enabled = is_active_mod_local

            if not gizmo_ob:
                sub_sub = sub.row()
                sub_sub.scale_x = 4
                icon = pcoll['ADD_GIZMO']
                sub_sub.operator("object.ml_gizmo_object_add", text="", icon_value=icon.icon_id
                            ).modifier = active_mod.name
            else:
                sub_sub = sub.row(align=True)
                sub_sub.scale_x = 1.2
                depress = not gizmo_ob.hide_viewport
                sub_sub.operator("object.ml_gizmo_object_toggle_visibility", text="",
                                icon='EMPTY_ARROWS', depress=depress)
                sub.popover("OBJECT_PT_ml_gizmo_object_settings", text="")

    # === Modifier specific settings ===
    box = col.box()
    # Disable layout for linked modifiers here manually so in custom
    # layouts all operators/settings are greyed out.
    box.enabled = is_active_mod_local

    # A column is needed here to keep the layout more compact,
    # because in a box separators give an unnecessarily big space.
    col = box.column()

    # Some modifiers have an improved layout with additional settings.
    have_custom_layout = (
        'BOOLEAN',
        'LATTICE'
    )

    if active_mod.type in have_custom_layout:
        getattr(ml_modifier_layouts, active_mod.type)(col, ob, active_mod)
    else:
        mp = DATA_PT_modifiers(context)
        getattr(mp, active_mod.type)(col, ob, active_mod)


# Registering
# =======================================================================

def active_object_modifier_active_index_get(self):
    """Function for reading ob.ml_modifier_active_index indirectly
    to avoid problems when using library overrides.
    """
    ob = get_ml_active_object()

    if not ob:
        return 0

    return ob.ml_modifier_active_index


def active_object_modifier_active_index_set(self, value):
    """Function for writing ob.ml_modifier_active_index indirectly
    to avoid problems when using library overrides.
    """
    ob = get_ml_active_object()

    if ob:
        ob.ml_modifier_active_index = value


def set_mesh_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    mesh_modifiers = bpy.context.window_manager.ml_mesh_modifiers

    if not mesh_modifiers:
        for name, _, mod in modifier_categories.ALL_MODIFIERS:
            item = mesh_modifiers.add()
            item.name = name
            item.value = mod


def set_curve_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    curve_modifiers = bpy.context.window_manager.ml_curve_modifiers

    if not curve_modifiers:
        for name, _, mod in modifier_categories.CURVE_ALL_NAMES_ICONS_TYPES:
            item = curve_modifiers.add()
            item.name = name
            item.value = mod


def set_lattice_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    lattice_modifiers = bpy.context.window_manager.ml_lattice_modifiers

    if not lattice_modifiers:
        for name, _, mod in modifier_categories.LATTICE_ALL_NAMES_ICONS_TYPES:
            item = lattice_modifiers.add()
            item.name = name
            item.value = mod


@persistent
def on_file_load(dummy):
    set_mesh_modifier_collection_items()
    set_curve_modifier_collection_items()
    set_lattice_modifier_collection_items()


def pinned_object_ensure_users(scene):
    """Handler for making sure a pinned object which is only used by
    ml_pinned_object, i.e. an object which was deleted while it was
    pinned, really gets deleted + the property gets reset.
    """
    if scene.ml_pinned_object:
        if scene.ml_pinned_object.users == 1 and not scene.ml_pinned_object.use_fake_user:
            bpy.data.objects.remove(scene.ml_pinned_object)
            scene.ml_pinned_object = None


def on_pinned_object_change(self, context):
    """Callback function for ml_pinned_object"""
    scene = context.scene
    depsgraph_handlers = bpy.app.handlers.depsgraph_update_pre

    if scene.ml_pinned_object:
        depsgraph_handlers.append(pinned_object_ensure_users)
    else:
        try:
            depsgraph_handlers.remove(pinned_object_ensure_users)
        except ValueError:
            pass


def register():
    # === Properties ===
    bpy.types.Object.ml_modifier_active_index = IntProperty(options={'LIBRARY_EDITABLE'})
    wm = bpy.types.WindowManager
    # Property to access ob.ml_modifier_active_index through, to avoid
    # the problem of modifier_active_index not being possible to be
    # changed directly by the modifier list when using library
    # overrides.
    wm.ml_active_object_modifier_active_index = IntProperty(
        get=active_object_modifier_active_index_get,
        set=active_object_modifier_active_index_set
    )
    wm.ml_mod_to_add = StringProperty(name="Modifier to add", update=add_modifier,
                                      description="Search for a modifier and add it to the stack")
    wm.ml_mesh_modifiers = CollectionProperty(type=MeshModifiersCollection)
    wm.ml_curve_modifiers = CollectionProperty(type=CurveModifiersCollection)
    wm.ml_lattice_modifiers = CollectionProperty(type=LatticeModifiersCollection)

    scene = bpy.types.Scene
    scene.ml_pinned_object = PointerProperty(type=bpy.types.Object, update=on_pinned_object_change)

    bpy.app.handlers.load_post.append(on_file_load)

    set_mesh_modifier_collection_items()
    set_curve_modifier_collection_items()
    set_lattice_modifier_collection_items()


def unregister():
    bpy.app.handlers.load_post.remove(on_file_load)

    del bpy.types.Object.ml_modifier_active_index
