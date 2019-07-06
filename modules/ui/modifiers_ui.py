import math
import numpy as np

import bpy
import addon_utils
from bl_ui.properties_data_modifier import DATA_PT_modifiers
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import (
    Menu,
    Operator,
    Panel,
    PropertyGroup,
    UIList
)

from . import ml_modifier_layouts
from .. import icons, modifier_categories
from ..operators import lattice_toggle_editmode, lattice_toggle_editmode_prop_editor
from ..utils import (
    delete_gizmo_object,
    delete_ml_vertex_group,
    get_gizmo_object,
    get_ml_active_object,
    get_vertex_group,
)


# UI elements
#=======================================================================

def mod_show_editmode_and_cage(modifier, layout, scale_x=1.0, use_in_list=False):
    """This handles showing, hiding and activating/deactivating
    show_in_editmode and show_on_cage buttons to match the behaviour of
    the regular UI. When called, adds those buttons, for the specified
    modifier, in their correct state, to the specified (sub-)layout.
    Note: some modifiers show show_on_cage in the regular UI only if,
    for example, an object to use for deforming is specified. Eg.
    Armatature modifier requires an armature object to be specified in
    order to show the button. This function doesn't take that into
    account but instead shows the button always in those cases. It's
    easier to achieve and hardly makes a difference.
    """
    # Note: When using custom icons, the icons don't seem to get dimmer
    # in inactive state, so custom dimmer icons are needed.
    # SHOW_IN_EDITMODE_ON_INACTIVE_BUTTON and
    # SHOW_ON_CAGE_ON_INACTIVE_BUTTON are used here for that reason.
    # Is it a bug or just how icon_value works?

    dont_support_show_in_editmode  = modifier_categories.dont_support_show_in_editmode
    support_show_on_cage  = modifier_categories.support_show_on_cage

    pcoll = icons.preview_collections["main"]

    # === show_in_editmode ===
    sub = layout.row(align=True)
    sub.scale_x = scale_x
    if not use_in_list:
        sub.active = modifier.show_viewport
    if modifier.type not in dont_support_show_in_editmode :
        if not modifier.show_viewport and use_in_list:
            show_in_editmode_on = pcoll['SHOW_IN_EDITMODE_ON_INACTIVE']
            show_in_editmode_off = pcoll['SHOW_IN_EDITMODE_OFF_INACTIVE']
        elif not modifier.show_viewport:
            show_in_editmode_off = pcoll['SHOW_IN_EDITMODE_OFF']
            show_in_editmode_on = pcoll['SHOW_IN_EDITMODE_ON_INACTIVE_BUTTON']
        else:
            show_in_editmode_on = pcoll['SHOW_IN_EDITMODE_ON']
            show_in_editmode_off = pcoll['SHOW_IN_EDITMODE_OFF']
        icon = show_in_editmode_on.icon_id if modifier.show_in_editmode else show_in_editmode_off.icon_id
        sub.prop(modifier, "show_in_editmode", text="", icon_value=icon,
                 emboss=not use_in_list)
    else:
        # Make icons align nicely
        empy_icon = pcoll['EMPTY_SPACE']
        sub.label(text="", translate=False, icon_value=empy_icon.icon_id)

    # === show_on_cage ===
    if modifier.type in support_show_on_cage :
        ob = get_ml_active_object()
        mods = ob.modifiers
        mod_index = mods.find(modifier.name)

        # Check if some modifier before this has show_in_editmode on
        # and doesn't have show_on_cage setting.
        is_before_show_in_editmode_on = False
        end_index = np.clip(mod_index, 1, 99)
        for mod in mods[0:end_index]:
            if mod.show_in_editmode and mod.type not in support_show_on_cage :
                is_before_show_in_editmode_on = True
                break

        # Check if some modifier after this has show_in_editmode and
        # show_on_cage both on and also is visible in the viewport.
        is_after_show_on_cage_on = False
        for mod in mods[(mod_index + 1):(len(mods))]:
            if (mod.show_viewport and mod.show_in_editmode
                    and mod.show_on_cage):
                is_after_show_on_cage_on = True
                break

        # show_on_cage drawing
        if not is_before_show_in_editmode_on:
            sub = layout.row(align=True)
            sub.scale_x = scale_x
            show_on_cage_on = pcoll['SHOW_ON_CAGE_ON']
            show_on_cage_off = pcoll['SHOW_ON_CAGE_OFF']
            if (not modifier.show_viewport or not modifier.show_in_editmode
                    or is_after_show_on_cage_on):
                if use_in_list:
                    show_on_cage_on = pcoll['SHOW_ON_CAGE_ON_INACTIVE']
                    show_on_cage_off = pcoll['SHOW_ON_CAGE_OFF_INACTIVE']
                else:
                    sub.active = False
                    show_on_cage_on = pcoll['SHOW_ON_CAGE_ON_INACTIVE_BUTTON']
            icon = show_on_cage_on.icon_id if modifier.show_on_cage else show_on_cage_off.icon_id
            sub.prop(modifier, "show_on_cage", text="", icon_value=icon, emboss=not use_in_list)
        else:
            # Make icons align nicely
            empy_icon = pcoll['EMPTY_SPACE']
            sub.label(text="", translate=False, icon_value=empy_icon.icon_id)
    else:
        # Make icons align nicely
        empy_icon = pcoll['EMPTY_SPACE']
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
    bpy.ops.object.modifier_add(type=mod_type)

    ob = get_ml_active_object()

    # Enable auto smooth if modifier is weighted normal
    if mod_type == 'WEIGHTED_NORMAL':
        ob.data.use_auto_smooth = True

    # Set correct active_mod index
    mods = ob.modifiers
    mods_len = len(mods) - 1
    ob.ml_modifier_active_index = mods_len

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
        for name, icon, mod in modifier_categories.mesh_modify_names_icons_types:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Generate")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.mesh_generate_names_icons_types:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Deform")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.mesh_deform_names_icons_types:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Simulate")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.mesh_simulate_names_icons_types:
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
        for name, icon, mod in modifier_categories.curve_modify_names_icons_types:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Generate")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.curve_generate_names_icons_types:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Deform")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.curve_deform_names_icons_types:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Simulate")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.curve_simulate_names_icons_types:
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
        for name, icon, mod in modifier_categories.lattice_modify_names_icons_types:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Deform")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.lattice_deform_names_icons_types:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Simulate")
        col.separator(factor=0.3)
        for name, icon, mod in modifier_categories.lattice_simulate_names_icons_types:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod


class OBJECT_UL_modifier_list(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if mod:
                layout.label(text="", translate=False, icon_value=layout.icon(mod))
                layout.prop(mod, "name", text="", emboss=False, icon_value=icon)

                # Hide visibility toggles for collision modifier as they are not used
                # in the regular UI either (apparently can cause problems in some scenes).
                if mod.type != 'COLLISION':
                    row = layout.row(align=True)
                    row.alignment = 'RIGHT'
                    row.prop(mod, "show_render", text="", emboss=False)
                    row.prop(mod, "show_viewport", text="", emboss=False)
                    mod_show_editmode_and_cage(mod, row, use_in_list=True)
            else:
                layout.label(text="", translate=False, icon_value=icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class ModifierListActions:
    """Base operator for list actions."""

    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    action = None

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

        if mods:
            active_mod = ml_active_ob.modifiers[active_mod_index]
            active_mod_name = active_mod.name

            if self.action == 'UP':
                bpy.ops.object.modifier_move_up(override, modifier=active_mod_name)
                ml_active_ob.ml_modifier_active_index = active_mod_index_up
            elif self.action == 'DOWN':
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
                    if ob.type == 'LATTICE':
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
        self.shift = True if event.shift else False

        return self.execute(context)


class OBJECT_OT_ml_modifier_move_up(Operator, ModifierListActions):
    bl_idname = "object.ml_modifier_move_up"
    bl_label = "Move modifier up"
    bl_description = "Move modifier up in the stack"

    action = 'UP'


class OBJECT_OT_ml_modifier_move_down(Operator, ModifierListActions):
    bl_idname = "object.ml_modifier_move_down"
    bl_label = "Move modifier down"
    bl_description = "Move modifier down in the stack"

    action = 'DOWN'


class OBJECT_OT_ml_modifier_remove(Operator, ModifierListActions):
    bl_idname = "object.ml_modifier_remove"
    bl_label = "Remove Modifier"
    bl_description = ("Remove modifier from the active object.\n"
                     "\n"
                     "Hold shift to also delete its gizmo object (if it has one)")

    action = 'REMOVE'


class OBJECT_PT_Gizmo_object_settings(Panel):
    bl_label = "Gizmo Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        layout = self.layout

        ob = get_ml_active_object()
        gizmo_ob = get_gizmo_object()

        layout.prop(gizmo_ob, "name", text="")

        if gizmo_ob.type == 'EMPTY':
            layout.prop(gizmo_ob ,"empty_display_type", text="")
            layout.prop(gizmo_ob ,"empty_display_size", text="Display Size")

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

        layout.operator("object.ml_gizmo_object_select")
        layout.operator("object.ml_gizmo_object_delete")


# UI
#=======================================================================

def modifiers_ui(context, layout, num_of_rows=False, use_in_popup=False):

    ob = context.object if context.area.type == 'PROPERTIES' else get_ml_active_object()
    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    pcoll = icons.preview_collections["main"]

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
    wm = bpy.context.window_manager
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
    layout.template_list("OBJECT_UL_modifier_list", "", ob, "modifiers",
                         ob, "ml_modifier_active_index", rows=num_of_rows)

    # When sub.scale_x is 1.5 and the area/region is narrow, the buttons
    # don't align properly, so some manual work is needed.
    if use_in_popup:
        align_button_groups = prefs.popup_width <= 278
    elif context.area.type == 'VIEW_3D':
        align_button_groups = context.region.width <= 308
    else:
        align_button_groups = context.area.width <= 308

    sub_scale = 3 if align_button_groups else 1.5

    row = layout.row(align=align_button_groups)

    # === Modifier batch operators ===
    sub = row.row(align=True)
    # Note: In 2.79, this is what scale 2.0 looks like. Here 2.0 causes list ordering
    # buttons to get tiny. 2.8 Bug?
    sub.scale_x = sub_scale

    icon = pcoll['TOGGLE_ALL_MODIFIERS_VISIBILITY']
    sub.operator("object.ml_toggle_all_modifiers", icon_value=icon.icon_id, text="")

    icon = pcoll['APPLY_ALL_MODIFIERS']
    sub.operator("object.ml_apply_all_modifiers", icon_value=icon.icon_id, text="")

    icon = pcoll['DELETE_ALL_MODIFIERS']
    sub.operator("object.ml_remove_all_modifiers", icon_value=icon.icon_id, text="")

    # === List manipulation ===
    sub = row.row(align=True)
    #  Note: In 2.79, this is what scale 2.0 looks like. Here 2.0 causes list ordering
    # buttons to get tiny. 2.8 Bug?
    sub.scale_x = sub_scale
    if not align_button_groups:
        sub.alignment = 'RIGHT'
    sub.operator(OBJECT_OT_ml_modifier_move_up.bl_idname, icon='TRIA_UP', text="")
    sub.operator(OBJECT_OT_ml_modifier_move_down.bl_idname, icon='TRIA_DOWN', text="")
    sub.operator(OBJECT_OT_ml_modifier_remove.bl_idname, icon='REMOVE', text="")

    # === Modifier settings ===
    if not ob.modifiers:
        return

    active_mod_index = ob.ml_modifier_active_index
    active_mod = ob.modifiers[active_mod_index]

    all_modifier_names_icons_types = modifier_categories.all_modifier_names_icons_types

    active_mod_icon = [icon for name, icon, mod in all_modifier_names_icons_types()
                        if mod == active_mod.type].pop()

    col = layout.column(align=True)

    # === General settings ===
    box = col.box()

    if not prefs.hide_general_settings_region:
        row = box.row()
        sub = row.row()
        sub.label(text="", icon=active_mod_icon)
        sub.prop(active_mod, "name", text="")

        sub = row.row(align=True)
        sub_sub = sub.row(align=True)
        sub_sub.scale_x = 1.1
        # Hide visibility toggles for collision modifier as they are not used
        # in the regular UI either (apparently can cause problems in some scenes).
        if active_mod.type != 'COLLISION':
            sub_sub.prop(active_mod, "show_render", text="")
            sub_sub.prop(active_mod, "show_viewport", text="")
        mod_show_editmode_and_cage(active_mod, sub, scale_x=1.1)

    row = box.row()

    sub = row.row(align=True)
    sub.scale_x = 5
    icon = pcoll['APPLY_MODIFIER']
    sub.operator("object.ml_modifier_apply", text="",
                 icon_value=icon.icon_id).modifier = active_mod.name

    if active_mod.type in modifier_categories.support_apply_as_shape_key:
        icon = pcoll['APPLY_MODIFIER_AS_SHAPEKEY']
        sub.operator("object.ml_modifier_apply_as_shapekey", text="",
                     icon_value=icon.icon_id).modifier=active_mod.name

    if active_mod.type not in modifier_categories.dont_support_copy:
        sub.operator("object.ml_modifier_copy",
                     text="", icon='DUPLICATE').modifier = active_mod.name

    # === Gizmo object settings ===
    if ob.type == 'MESH':
        if (active_mod.type in modifier_categories.have_gizmo_property
                or active_mod.type == 'UV_PROJECT'):
            gizmo_ob = get_gizmo_object()

            sub = row.row(align=True)
            sub.alignment = 'RIGHT'

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
                sub.popover("OBJECT_PT_Gizmo_object_settings", text="")


    # === Modifier specific settings ===
    box = col.box()
    # A column is needed here to keep the layout more compact,
    # because in a box separators give an unnecessarily big space.
    col = box.column()
    # Custom layouts for multiresolution, laplacian deform, mesh deform
    # and surface deform because otherwise their operators don't work.
    if active_mod.type == 'MULTIRES':
        ml_modifier_layouts.MULTIRES(col, ob, active_mod)
    elif active_mod.type == 'LAPLACIANDEFORM':
        ml_modifier_layouts.LAPLACIANDEFORM(col, ob, active_mod)
    elif active_mod.type == 'MESH_DEFORM':
        ml_modifier_layouts.MESH_DEFORM(col, ob, active_mod)
    elif active_mod.type =='SURFACE_DEFORM':
        ml_modifier_layouts.SURFACE_DEFORM(col, ob, active_mod)
    elif active_mod.type == 'LATTICE':
        ml_modifier_layouts.LATTICE(col, ob, active_mod)
    else:
        mp = DATA_PT_modifiers(context)
        getattr(mp, active_mod.type)(col, ob, active_mod)


# Registering
#=======================================================================

def set_mesh_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    mesh_modifiers = bpy.context.window_manager.ml_mesh_modifiers

    if not mesh_modifiers:
        for name, _, mod in modifier_categories.all_modifier_names_icons_types():
            item = mesh_modifiers.add()
            item.name = name
            item.value = mod


def set_curve_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    curve_modifiers = bpy.context.window_manager.ml_curve_modifiers

    if not curve_modifiers:
        for name, _, mod in modifier_categories.curve_all_names_icons_types:
            item = curve_modifiers.add()
            item.name = name
            item.value = mod


def set_lattice_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    lattice_modifiers = bpy.context.window_manager.ml_lattice_modifiers

    if not lattice_modifiers:
        for name, _, mod in modifier_categories.lattice_all_names_icons_types:
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
    bpy.types.Object.ml_modifier_active_index = IntProperty()

    # Use Window Manager for storing modifier search property
    # and modifier collection because it can be accessed on
    # registering and it's not scene specific.
    wm = bpy.types.WindowManager
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