# Copyright (C) 2019 Antti Tikka

# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK *****


bl_info = {
    "name": "Modifier Popup Panel + Blend Ops",
    "author": "Antti Tikka, Nick Bosse",
    "version": (1, 0, 1),
    "blender": (2, 79, 0),
    "location": "Spacebar",
    "description": "UI minimising addon that provides expanded, modifier popup and substance integration options",
    "warning": "",
    "wiki_url": "https://github.com/Symstract/Modifier-Popup-Panel/tree/master",
    "category": "3D View"
}


import math
import numpy as np
import os

import addon_utils
from bl_ui.properties_data_modifier import DATA_PT_modifiers
import bpy
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import (
    AddonPreferences,
    Menu,
    Operator,
    PropertyGroup,
    UIList
)
import rna_keymap_ui


class Preferences(AddonPreferences):
    bl_idname = __name__

    modifier_01 = StringProperty()
    modifier_02 = StringProperty()
    modifier_03 = StringProperty()
    modifier_04 = StringProperty()
    modifier_05 = StringProperty()
    modifier_06 = StringProperty()
    modifier_07 = StringProperty()
    modifier_08 = StringProperty()
    modifier_09 = StringProperty()
    modifier_10 = StringProperty()
    modifier_11 = StringProperty()
    modifier_12 = StringProperty()

    mod_list_def_len = IntProperty(name="",
                                   description="Default/min number of rows to display in the modifier list",
                                   default=4)


    def draw(self, context):
        layout = self.layout

        # === Favourite modifiers selection ===
        layout.label(text="Favourite modifiers:")

        col = layout.column(align=True)

        num_of_mods = len(get_pref_mod_attr_name())
        num_of_rows = math.ceil(num_of_mods / 2)

        attr_iter = iter(get_pref_mod_attr_name())

        wm = bpy.context.window_manager

        # Draw two property searches per row
        for attr in attr_iter:
            row = col.split(percentage=0.5, align=True)
            row.prop_search(self, attr, wm, "all_modifiers", text="", icon='MODIFIER')
            row.prop_search(self, next(attr_iter), wm, "all_modifiers", text="", icon='MODIFIER')

        layout.separator()

        # === Number of rows in the modifier list ===
        layout.label(text="Default/min number of rows to display in the modifier list:")

        row = layout.row()
        split = row.split(percentage=0.5)
        split.prop(self, "mod_list_def_len")

        layout.separator()

        # === Hotkey ===
        layout.label(text="Hotkey:")

        col = layout.column()
        kc = bpy.context.window_manager.keyconfigs.addon
        for km, kmi in addon_keymaps:
            km = km.active()
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

        layout.separator()

        # === Info ===
        is_loaded, is_enabled = addon_utils.check("space_view3d_modifier_tools")
        if not is_enabled:
            layout.label(icon='INFO', text="Enable Modifier Tools addon for modifier batch operators.")


#=======================================================================


def get_pref_mod_attr_name():
    """List of the names of favourite modifier attributes in Preferences
    class for making drawing favourite modifier selection rows in
    preferences easy.
    """
    attr_name_list = [attr for attr in dir(Preferences) if "modifier_" in attr]
    return attr_name_list


def get_pref_mod_attr_value():
    """List of the names of favourite modifiers"""
    prefs = bpy.context.user_preferences.addons[__name__].preferences
    # Get correct class attributes and then their values
    attr_list = [attr for attr in dir(prefs) if "modifier_" in attr]
    attr_value_list = [getattr(prefs, attr) for attr in attr_list]
    return attr_value_list


def all_name_icon_type():
    """List of tuples of the names, icons and types of all modifiers."""
    mods_enum = bpy.types.Modifier.bl_rna.properties['type'].enum_items

    all_mod_names = [modifier.name for modifier in mods_enum]
    all_mod_icons = [modifier.icon for modifier in mods_enum]
    all_mod_types = [modifier.identifier for modifier in mods_enum]

    all_mods_zipped = list(zip(all_mod_names, all_mod_icons, all_mod_types))
    return all_mods_zipped


def fav_name_icon_type():
    """Iterator of tuples of the names, icons and types of favourite
    modifiers.
    """
    mods_enum = bpy.types.Modifier.bl_rna.properties['type'].enum_items
    all_mod_names = [modifier.name for modifier in mods_enum]
    all_mods_dict = dict(zip(all_mod_names, all_name_icon_type()))
    fav_mods_list = [all_mods_dict[mod] if mod in all_mods_dict else (None, None, None)
                     for mod in get_pref_mod_attr_value()]
    fav_mods_iter = iter(fav_mods_list)
    return fav_mods_iter


def mod_show_editmode_and_cage(modifier, layout, scale_x=1.0, use_in_llist=False):
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
    # Note: transparent icons look too dark. Bug?

    has_no_show_in_editmode = {
        'MESH_SEQUENCE_CACHE', 'BUILD', 'DECIMATE', 'MULTIRES', 'CLOTH', 'COLLISION',
        'DYNAMIC_PAINT','EXPLODE', 'FLUID_SIMULATION', 'PARTICLE_SYSTEM','SMOKE', 'SOFT_BODY'
    }

    deform_mods = {mod for name, icon, mod in all_name_icon_type()[25:41]}
    other_show_on_cage_mods = {
        'DATA_TRANSFER', 'NORMAL_EDIT', 'WEIGHTED_NORMAL', 'UV_PROJECT', 'VERTEX_WEIGHT_EDIT',
        'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_PROXIMITY', 'ARRAY', 'EDGE_SPLIT', 'MASK', 'MIRROR',
        'SOLIDIFY', 'SUBSURF', 'TRIANGULATE'
    }
    has_show_on_cage = deform_mods.union(other_show_on_cage_mods)

    pcoll = preview_collections["main"]

    # === show_in_editmode ===
    sub = layout.row(align=True)
    sub.scale_x = scale_x

    if modifier.type not in has_no_show_in_editmode:
        show_in_editmode_on = pcoll['SHOW_IN_EDITMODE_ON']
        show_in_editmode_off = pcoll['SHOW_IN_EDITMODE_OFF']
        if not modifier.show_viewport and use_in_llist:
            show_in_editmode_on = pcoll['SHOW_IN_EDITMODE_ON_INACTIVE']
            show_in_editmode_off = pcoll['SHOW_IN_EDITMODE_OFF_INACTIVE']
        elif not modifier.show_viewport:
            sub.active = False

        if use_in_llist:
            icon = show_in_editmode_on.icon_id if modifier.show_in_editmode else show_in_editmode_off.icon_id
            sub.prop(modifier, "show_in_editmode", text="", icon_value=icon,
                     emboss=False)
        else:
            sub.prop(modifier, "show_in_editmode", text="")


    # === show_on_cage ===
    if modifier.type in has_show_on_cage:
        ob = bpy.context.object
        mods = ob.modifiers
        mod_index = mods.find(modifier.name)

        # Check if some modifier before this has show_in_editmode on
        # and doesn't have show_on_cage setting.
        is_before_show_in_editmode_on = False
        end_index = np.clip(mod_index, 1, 99)
        for mod in mods[0:end_index]:
            if mod.show_in_editmode and mod.type not in has_show_on_cage:
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
                if use_in_llist:
                    show_on_cage_on = pcoll['SHOW_ON_CAGE_ON_INACTIVE']
                    show_on_cage_off = pcoll['SHOW_ON_CAGE_OFF_INACTIVE']
                else:
                    sub.active = False

            if use_in_llist:
                icon = show_on_cage_on.icon_id if modifier.show_on_cage else show_on_cage_off.icon_id
                sub.prop(modifier, "show_on_cage", text="", icon_value=icon, emboss=False)
            else:
                sub.prop(modifier, "show_on_cage", text="")


#=======================================================================


class AllModifiersCollection(PropertyGroup):
    # Collection Property for search
    value = StringProperty(name="my modifier")


def add_modifier(self, context):
    # Add modifier
    wm = bpy.context.window_manager
    mod_name = wm.mod_to_add
    mod_type = wm.all_modifiers[mod_name].value
    bpy.ops.object.modifier_add(type=mod_type)

    # Set correct active_mod index
    ob = context.object
    mods = ob.modifiers
    mods_len = len(mods) - 1
    ob.modifier_active_index = mods_len

    # Executing an operator via a function doesn't create an undo event,
    # so it needs to be added manually.
    bpy.ops.ed.undo_push(message="Add Modifier")


class OBJECT_MT_mpp_add_modifier_menu(Menu):
    bl_label = "Add Modifier"
    bl_idname = "OBJECT_MT_mpp_add_modifier_menu"
    bl_description = "Add a procedural operation/effect to the active object"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.alignment = 'LEFT'

        col = row.column()
        col.label(text="Modify")

        sub = col.column()
        sub.scale_y = 0.3
        sub.separator()

        for name, icon, mod in all_name_icon_type()[0:9]:
            col.operator("object.mpp_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Generate")

        sub = col.column()
        sub.scale_y = 0.3
        sub.separator()

        for name, icon, mod in all_name_icon_type()[9:25]:
            col.operator("object.mpp_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Deform")

        sub = col.column()
        sub.scale_y = 0.3
        sub.separator()

        for name, icon, mod in all_name_icon_type()[25:41]:
            col.operator("object.mpp_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Simulate")
        sub = col.column()
        sub.scale_y = 0.3
        sub.separator()

        for name, icon, mod in all_name_icon_type()[41:51]:
            col.operator("object.mpp_modifier_add", text=name, icon=icon).modifier_type = mod


class OBJECT_UL_modifier_list(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if mod:
                col = layout.column()
                row = col.split(percentage=0.70)
                sub = row.row(align=True)
                sub.label(text="", translate=False, icon_value=layout.icon(mod))
                sub.prop(mod, "name", text="", emboss=False, icon_value=icon)

                # Hide visibility toggles for collision modifier as they are not used
                # in the regular UI either (apparently can cause problems in some scenes).
                if mod.type != 'COLLISION':
                    sub = row.row(align=True)

                    icon = 'RESTRICT_RENDER_OFF' if mod.show_render else 'RESTRICT_RENDER_ON'
                    sub.prop(mod, "show_render", text="", icon=icon, emboss=False)

                    icon = 'RESTRICT_VIEW_OFF' if mod.show_viewport else 'RESTRICT_VIEW_ON'
                    sub.prop(mod, "show_viewport", text="", icon=icon, emboss=False)

                    mod_show_editmode_and_cage(mod, sub, use_in_llist=True)
            else:
                layout.label(text="", translate=False, icon_value=icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class ModifierListActions(Operator):
    """Base operator for list actions."""

    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    action = None

    def execute(self, context):
        ob = context.object
        mods = ob.modifiers
        mods_len = len(mods) - 1
        active_mod_index = ob.modifier_active_index
        active_mod_index_up = np.clip(active_mod_index - 1, 0, mods_len)
        active_mod_index_down = np.clip(active_mod_index + 1, 0, mods_len)

        if mods:
            active_mod_name = ob.modifiers[active_mod_index].name

            if self.action == 'UP':
                bpy.ops.object.modifier_move_up(modifier=active_mod_name)
                ob.modifier_active_index = active_mod_index_up
            elif self.action == 'DOWN':
                bpy.ops.object.modifier_move_down(modifier=active_mod_name)
                ob.modifier_active_index = active_mod_index_down
            elif self.action == 'REMOVE':
                bpy.ops.object.modifier_remove(modifier=active_mod_name)
                ob.modifier_active_index = active_mod_index_up

        return {'FINISHED'}


class OBJECT_OT_mpp_modifier_move_up(ModifierListActions):
    bl_idname = "object.mpp_modifier_move_up"
    bl_label = "Move modifier up"
    bl_description = "Move modifier up in the stack"

    action = 'UP'


class OBJECT_OT_mpp_modifier_move_down(ModifierListActions):
    bl_idname = "object.mpp_modifier_move_down"
    bl_label = "Move modifier down"
    bl_description = "Move modifier down in the stack"

    action = 'DOWN'


class OBJECT_OT_mpp_modifier_remove(ModifierListActions):
    bl_idname = "object.mpp_modifier_remove"
    bl_label = "Remove Modifier"
    bl_description = "Remove modifier from the active object"

    action = 'REMOVE'


class OBJECT_OT_mpp_modifier_add(Operator):
    bl_idname = "object.mpp_modifier_add"
    bl_label = "Add Modifier"
    bl_description = "Add a procedural operation/effect to the active object"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier_type = StringProperty()

    def execute(self, context):
        bpy.ops.object.modifier_add(type=self.modifier_type)

        # Set correct active_mod index
        ob = context.object
        mods = ob.modifiers
        mods_len = len(mods) - 1
        ob.modifier_active_index = mods_len

        return {'FINISHED'}


class OBJECT_OT_mpp_modifier_apply(Operator):
    bl_idname = "object.mpp_modifier_apply"
    bl_label = "Apply Modifier"
    bl_description = "Apply modifier and remove from the stack"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier = StringProperty()

    apply_as = EnumProperty(
        items=(
            ('DATA', "Data", ""),
            ('SHAPE', "Shape", "")
        ),
        default='DATA'
    )


    def execute(self, context):
        if context.mode == 'EDIT_MESH':
            bpy.ops.object.editmode_toggle()
            bpy.ops.ed.undo_push(message="Toggle Editmode")
            bpy.ops.object.modifier_apply(apply_as=self.apply_as, modifier=self.modifier)
            bpy.ops.ed.undo_push(message="Apply Modifier")
            bpy.ops.object.editmode_toggle()
        else:
            bpy.ops.object.modifier_apply(apply_as=self.apply_as, modifier=self.modifier)

        # Set correct active_mod index in case the applied modifier is
        # not the first in modifier stack.
        ob = context.object
        current_active_mod_index = ob.modifier_active_index
        new_active_mod_index = np.clip(current_active_mod_index - 1, 0, 99)
        ob.modifier_active_index = new_active_mod_index

        if current_active_mod_index != 0:
            self.report({'INFO'}, "Applied modifier was not first, result may not be as expected")

        return {'FINISHED'}


class OBJECT_OT_mpp_modifier_copy(Operator):
    bl_idname = "object.mpp_modifier_copy"
    bl_label = "Copy Modifier"
    bl_description = "Duplicate modifier at the same position in the stack"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier = StringProperty()

    def execute(self, context):
        bpy.ops.object.modifier_copy(modifier=self.modifier)

        # Set correct active_mod index
        ob = context.object
        active_index = ob.modifier_active_index
        ob.modifier_active_index = active_index + 1

        return {'FINISHED'}


#=======================================================================


class VIEW_3D_PT_modifier_popup(Operator):
    bl_idname = "view3d.modifier_popup"
    bl_label = "Modifier Pop-up Panel"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        ob = context.object

        if not ob:
            layout.label(text="No active object")
        elif ob.type not in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE'}:
            layout.label(text="Wrong object type")
        else:
            # === Favourite modifiers ===
            col = layout.column(align=True)

            fav_name_icon_type_iter = fav_name_icon_type()

            # Check if an item or the next item in fav_name_icon_type has a value
            # and add rows and buttons accordingly (two buttons per row).
            for name, icon, mod in fav_name_icon_type_iter:
                next_mod = next(fav_name_icon_type_iter)
                if name or next_mod[0] is not None:
                    row = col.split(percentage=0.5, align=True)

                    if name is not None:
                        add_modifer = row.operator("object.mpp_modifier_add", text=name,
                                                   icon=icon).modifier_type = mod
                    else:
                        row.label(text="")

                    if next_mod[0] is not None:
                        row.operator("object.mpp_modifier_add", text=next_mod[0],
                                     icon=next_mod[1]).modifier_type = next_mod[2]
                    else:
                        row.label(text="")

            # === Modifier search and menu ===
            col = layout.column()
            wm = bpy.context.window_manager
            row = col.split(percentage=0.59)
            row.prop_search(wm, "mod_to_add", wm, "all_modifiers", text="", icon='MODIFIER')
            row.menu("OBJECT_MT_mpp_add_modifier_menu")

            # === Modifier list ===
            ob = context.object

            prefs = bpy.context.user_preferences.addons[__name__].preferences
            num_of_rows = prefs.mod_list_def_len
            layout.template_list("OBJECT_UL_modifier_list", "", ob, "modifiers",
                                 ob, "modifier_active_index", rows=num_of_rows)

            row = layout.row()

            # === Modifier tools (from the addon) ===
            is_loaded, is_enabled = addon_utils.check("space_view3d_modifier_tools")
            if is_loaded and is_enabled:
                sub = row.row(align=True)
                sub.scale_x = 2.0
                sub.operator("object.toggle_apply_modifiers_view", icon='RESTRICT_VIEW_OFF', text="")
                sub.operator("object.apply_all_modifiers", icon='IMPORT', text="")
                sub.operator("object.delete_all_modifiers", icon='X', text="")

            # === List manipulation ===
            sub = row.row(align=True)
            sub.scale_x = 2.0
            sub.alignment = 'RIGHT'
            sub.operator(OBJECT_OT_mpp_modifier_move_up.bl_idname, icon='TRIA_UP', text="")
            sub.operator(OBJECT_OT_mpp_modifier_move_down.bl_idname, icon='TRIA_DOWN', text="")
            sub.operator(OBJECT_OT_mpp_modifier_remove.bl_idname, icon='ZOOMOUT', text="")

            # === Modifier settings ===
            ob = context.object

            if ob:
                if ob.modifiers:
                    active_mod_index = ob.modifier_active_index
                    active_mod = ob.modifiers[active_mod_index]

                    active_mod_icon = [icon for name, icon, mod in all_name_icon_type()
                                       if mod == active_mod.type].pop()

                    col = layout.column(align=True)

                    # === General settings ===
                    box = col.box()
                    row = box.row()

                    sub = row.row()
                    sub.label(text="", icon=active_mod_icon)
                    sub.prop(active_mod, "name", text="")

                    sub = row.row(align=True)
                    sub_sub = sub.row(align=True)
                    sub_sub.scale_x = 1.2
                    # Hide visibility toggles for collision modifier as they are not used
                    # in the regular UI either (apparently can cause problems in some scenes).
                    if active_mod.type != 'COLLISION':
                        sub_sub.prop(active_mod, "show_render", text="")
                        sub_sub.prop(active_mod, "show_viewport", text="")
                    mod_show_editmode_and_cage(active_mod, sub, scale_x=1.2)

                    row = box.row()
                    row.operator("object.mpp_modifier_apply",
                                 text="Apply").modifier = active_mod.name

                    sub = row.row()
                    # Cloth and Soft Body have "Apply As Shape Key" but no "Copy Modifier".
                    # In those cases "Apply As Shape Key" doesn't need to be scaled up.
                    if active_mod.type not in {'CLOTH', 'SOFT_BODY'}:
                        sub.scale_x = 1.3
                    deform_mods = {mod for name, icon, mod in all_name_icon_type()[25:42]}
                    other_shape_key_mods = {'CLOTH', 'SOFT_BODY', 'MESH_CACHE'}
                    has_shape_key = deform_mods.union(other_shape_key_mods)
                    if active_mod.type in has_shape_key:
                        apply_as_shape_key = sub.operator("object.mpp_modifier_apply",
                                                          text="Apply as Shape Key")
                        apply_as_shape_key.modifier=active_mod.name
                        apply_as_shape_key.apply_as='SHAPE'

                    has_no_copy = {
                        'CLOTH', 'COLLISION', 'DYNAMIC_PAINT', 'FLUID_SIMULATION',
                        'PARTICLE_SYSTEM', 'SMOKE', 'SOFT_BODY'
                    }
                    if active_mod.type not in has_no_copy:
                        row.operator("object.mpp_modifier_copy",
                                     text="Copy").modifier = active_mod.name

                    # === Modifier specific settings ===
                    box = col.box()
                    # A column is needed here to keep the layout more compact,
                    # because in a box separators give an unnecessarily big space.
                    col = box.column()
                    mp = DATA_PT_modifiers(context)
                    getattr(mp, active_mod.type)(col, ob, active_mod)


#=======================================================================


class BlackOpsMeshMenu(Menu):
    bl_label = "Add Blend Ops Mesh"
    bl_idname = "view3d.black_ops.sub_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.black_plane", text="Blend Plane", icon="MESH_GRID")
        layout.operator("mesh.black_cube", text="Blend Cube", icon="SNAP_VOLUME")

        layout.separator()

        layout.operator("mesh.def_eight", text="8 Cylinder", icon="MESH_CYLINDER")
        layout.operator("mesh.def_sixteen", text="16 Cylinder", icon="MESH_CYLINDER")
        layout.operator("mesh.def_thirty_two", text="32 Cylinder", icon="MESH_CYLINDER")

        layout.separator()

        layout.operator("mesh.def_sphere_two", text="2 Cube Sphere", icon="WIRE")
        layout.operator("mesh.def_sphere_four", text="4 Cube Sphere", icon="WIRE")
        layout.operator("mesh.def_sphere_eight", text="8 Cube Sphere", icon="WIRE")


#=======================================================================


class BlackOps(Menu):
    bl_label = "Blend Ops Menu"
    bl_idname = "view3d.black_ops"

    # Function that creates the dropdown menu
    def draw(self, context):
        layout = self.layout

        layout.menu(BlackOpsMeshMenu.bl_idname, icon="MESH_GRID")
        # layout.menu(BlackOpsBackgroundMenu.bl_idname, icon="FILE_IMAGE")

        layout.separator()

        layout.operator("object.shade_sharp", text="Sharp Shade", icon="FACESEL")

        layout.separator()

        layout.label(text="Modifiers Pop-Up  [Shift Ctrl Alt B]", icon="MODIFIER")
        layout.operator("object.origin_mirror", text="Origin Mirror", icon="MOD_MIRROR")
        # layout.operator("object.remove_mirror", text="Unmirror Object", icon="GROUP")

        layout.operator("object.bevel_w_weight", text="Bevel", icon="MOD_BEVEL")
        layout.operator("edge.set_bevel_sharp", text="Bevel Sharp", icon="SNAP_EDGE")
        layout.operator("object.black_slice", text="Split Boolean", icon="ROTATECENTER")
        layout.operator("object.clear_not_sharp", text="Clear Not Sharp", icon="SNAP_EDGE")
        layout.operator("object.curve_array", text="Curve Array", icon="MOD_CURVE")
        layout.operator("object.circle_array", text="Circle Array", icon="GROUP_VERTEX")
        # layout.operator("object.remove_bevel", text="Unbevel Object", icon = "SNAP_VOLUME")

        layout.separator()

        layout.operator("object.boolean_mode", text="Boolean Mode", icon="MOD_BOOLEAN")
        layout.operator("object.exit_boolean_mode", text="Exit Boolean Mode", icon="X")

        layout.operator("object.mod_apply", text="Apply Modifiers", icon="MODIFIER")
        layout.operator("object.mod_apply_all", text="Apply Modifiers to All", icon="MODIFIER")

        layout.separator()

        layout.operator("object.pack_unwrap", text="Pack Unwrap", icon="UV_ISLANDSEL")
        layout.operator("object.sharp_unwrap", text="Sharp Unwrap", icon="UV_EDGESEL")
        layout.operator("object.cube_unwrap", text="Cube Unwrap", icon="UV_FACESEL")

        layout.separator()

        layout.operator("object.create_tex_set", text="Create Texture Set", icon="POTATO")
        layout.operator("scene.create_mat_sets", text="Create Material Sets", icon="SMOOTH")
        layout.operator("scene.clear_mat_sets", text="Clear Material Sets", icon="SOLID")
        layout.operator("object.id_create", text="Create Scene ID Map", icon="SEQ_CHROMA_SCOPE")

        layout.separator()

        layout.operator("object.sharpShade", text="Import Substance", icon="IMPORT")
        layout.operator("scene.substance_export", text="Export Scene for Substance", icon="EXPORT")


#=======================================================================


class SharpShading(Operator):
    """Shade smooth with auto smooth enabled"""
    bl_idname = "object.shade_sharp"
    bl_label = "Sharp Shade"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    # Function section for sharp shading
    def execute(self, context):
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.610865
        return {'FINISHED'}


class OriginMirror(Operator):
    """Origin to 3D cursor, mirror on x axis with clipping"""
    bl_idname = "object.origin_mirror"
    bl_label = "Origin Mirror"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        bpy.ops.object.modifier_add(type="MIRROR")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        return {'FINISHED'}


class BevelWeight(Operator):
    bl_idname = "object.bevel_w_weight"
    bl_label = "Bevel with weight"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Bevel"].limit_method = "ANGLE"
        return {'FINISHED'}


class SetBevelEdgeAll(Operator):
    """Adds bevel modifier with weight setting and all edge weights to 1 and all sharp edges marked"""
    bl_idname = "edge.set_bevel_sharp"
    bl_label = "Set All Bevel Edge"
    bl_context = "editmode"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        # Add bevel modifier with weight setting then set all sharp edge weights to 1 furthermore go into edit mode and make
        # all sharp edges marked sharp
        # Add modifier
        obj = bpy.context.object

        if not obj.modifiers:
            bpy.ops.object.modifier_add(type="BEVEL")
            bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
            bpy.context.object.modifiers["Bevel"].segments = 3
            bpy.context.object.modifiers["Bevel"].use_clamp_overlap = False
            bpy.context.object.modifiers["Bevel"].width = 0.05
            ob = bpy.context.object
            me = ob.data
            me.use_customdata_edge_bevel = True
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.mesh.edges_select_sharp()
            bpy.ops.mesh.mark_sharp()
            bpy.ops.object.editmode_toggle()
            for e in me.edges:
                if e.use_edge_sharp:
                    e.bevel_weight = 1
                else:
                    pass
            return {'FINISHED'}
        else:
            bevel = False
            for modifier in obj.modifiers:
                if modifier.type == "BEVEL":
                    bevel = True
                    me = obj.data
                    me.use_customdata_edge_bevel = True
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action="DESELECT")
                    bpy.ops.mesh.edges_select_sharp()
                    bpy.ops.mesh.mark_sharp()
                    bpy.ops.object.editmode_toggle()
                    for e in me.edges:
                        if e.use_edge_sharp:
                            e.bevel_weight = 1
            if bevel is True:
                pass
            else:
                bpy.ops.object.modifier_add(type="BEVEL")
                bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
                bpy.context.object.modifiers["Bevel"].segments = 3
                bpy.context.object.modifiers["Bevel"].use_clamp_overlap = False
                bpy.context.object.modifiers["Bevel"].width = 0.05
                ob = bpy.context.object
                me = ob.data
                me.use_customdata_edge_bevel = True
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.edges_select_sharp()
                bpy.ops.mesh.mark_sharp()
                bpy.ops.object.editmode_toggle()
                for e in me.edges:
                    if e.use_edge_sharp:
                        e.bevel_weight = 1
                    else:
                        pass
            return {"FINISHED"}
        # bpy.ops.object.modifier_add(type="BEVEL")
        # Set limit to weight
        # bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"


class BlackSlice(Operator):
    bl_idname = "object.black_slice"
    bl_label = "Bool Split"

    cutter_object = ""
    cutter_duplicate_object = ""
    difference_object = ""
    intersect_object = ""

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        # cutter_object = bpy.context.object.
        selection_names = [obj.name for obj in bpy.context.selected_objects]
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.modifier_apply(modifier="Auto Boolean")
        bpy.ops.object.modifier_apply(modifier="Auto Boolean")
        bpy.ops.btool.auto_slice(solver='BMESH')
        bpy.data.objects[selection_names[1]].select = True
        bpy.ops.object.join()
        return {"FINISHED"}


class ClearNotSharp(Operator):
    bl_idname = "object.clear_not_sharp"
    bl_label = "Clear Not Sharp"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        # Add bevel modifier with weight setting then set all sharp edge weights to 1 furthermore go into edit mode and make
        # all sharp edges marked sharp
        # Add modifier
        obj = bpy.context.object
        for modifier in obj.modifiers:
            if modifier.type == "BEVEL":
                ob = bpy.context.object
                me = ob.data
                me.use_customdata_edge_bevel = True
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                bpy.ops.mesh.edges_select_sharp()
                bpy.ops.mesh.select_all(action="INVERT")
                bpy.ops.mesh.mark_sharp(clear=True)
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.object.editmode_toggle()
                for e in me.edges:
                    if e.use_edge_sharp:
                        e.bevel_weight = 1
                    else:
                        e.bevel_weight = 0
                return {'FINISHED'}
            else:
                ob = bpy.context.object
                me = ob.data
                me.use_customdata_edge_bevel = True
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                bpy.ops.mesh.edges_select_sharp()
                bpy.ops.mesh.select_all(action="INVERT")
                bpy.ops.mesh.mark_sharp(clear=True)
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.object.editmode_toggle()
                for e in me.edges:
                    if e.use_edge_sharp:
                        e.bevel_weight = 1
                    else:
                        e.bevel_weight = 0
                return {"FINISHED"}


class CircleArray(Operator):
    bl_idname = "object.circle_array"
    bl_label = "Circle Array"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.modifier_add(type="ARRAY")
        circle_array_object = bpy.context.object.name
        bpy.context.object.modifiers["Array"].count = 8
        bpy.context.object.modifiers["Array"].use_relative_offset = False
        bpy.context.object.modifiers["Array"].use_object_offset = True
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        bpy.ops.transform.rotate(value=0.7854, axis=(0, 0, 1), constraint_axis=(False, False, True),
                                 constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                                 proportional_edit_falloff='SMOOTH', proportional_size=1)
        empty_name = bpy.context.object.name
        bpy.data.objects[empty_name].select = False
        # bpy.data.objects[empty_name].select = True
        # bpy.context.scene.objects.active = bpy.data.objects[empty_name]
        bpy.data.objects[circle_array_object].select = True
        bpy.context.scene.objects.active = bpy.data.objects[circle_array_object]
        bpy.context.object.modifiers["Array"].offset_object = bpy.data.objects[empty_name]
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        # bpy.data.objects[empty_name].select = True
        # bpy.context.scene.objects.active = bpy.data.objects[empty_name]
        # bpy.ops.transform.rotate(value=1.5708, axis=(0, 0, 1), constraint_axis=(False, False, True),
        #                          constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
        #                          proportional_edit_falloff='SMOOTH', proportional_size=1)
        # bpy.context.object.modifiers["Array"].offset_object = bpy.data.object[empty_name]

        # empty_rotation = bpy.context.scene.objects.modifiers["Array"].count

        return {"FINISHED"}


class CurveArray(Operator):
    bl_idname = "object.curve_array"
    bl_label = "Curve Array"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.modifier_add(type="ARRAY")
        curve_array_object = bpy.context.object.name
        bpy.context.object.modifiers["Array"].count = 4
        bpy.context.object.modifiers["Array"].use_relative_offset = False
        bpy.context.object.modifiers["Array"].use_object_offset = True
        bpy.ops.curve.primitive_bezier_curve_add(view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
            True, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
            False,
            False, False, False, False))
        curve_name = bpy.context.object.name
        bpy.data.objects[curve_name].select = False
        bpy.data.objects[curve_array_object].select = True
        bpy.context.scene.objects.active = bpy.data.objects[curve_array_object]
        bpy.context.object.modifiers["Array"].offset_object = bpy.data.objects[curve_name]
        bpy.ops.object.modifier_add(type='CURVE')
        bpy.context.object.modifiers["Curve"].object = bpy.data.objects[curve_name]
        return {"FINISHED"}


class BlackPlane(Operator):
    bl_idname = "mesh.black_plane"
    bl_label = "Blend Plane Add"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        verts = [
            (0, 1, 0),
            (1, 1, 0),
            (1, -1, 0),
            (0, -1, 0)
        ]

        edges = []

        faces = [
            (3, 2, 1, 0)
        ]

        mesh_data = bpy.data.meshes.new("cube_mesh_data")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Black Plane", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].width = 0.025
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        return {"FINISHED"}


class BlackCube(Operator):
    bl_label = "Blend Cube Add"
    bl_idname = "mesh.black_cube"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        verts = [
            (0, 1, -1),
            (1, 1, -1),
            (1, -1, -1),
            (0, -1, -1),
            (0, 1, 1),
            (1, 1, 1),
            (1, -1, 1),
            (0, -1, 1)
        ]

        edges = []

        faces = [
            (0, 1, 2, 3),
            (7, 6, 5, 4),
            (2, 6, 7, 3),
            (1, 5, 6, 2),
            (0, 4, 5, 1)
        ]

        mesh_data = bpy.data.meshes.new("cube_mesh_data")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Black Cube", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].width = 0.025
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        return {"FINISHED"}


class OneCylinder(Operator):
    bl_idname = "mesh.def_eight"
    bl_label = "Defined Cylinder Add"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        # bpy.ops.mesh.primitive_cylinder_add(vertices=8)
        verts = [
            (0, 1, -1),
            (0.7071, 0.7071, -1),
            (1, 0, -1),
            (0.7071, -0.7071, -1),
            (0, -1, -1),
            # separator
            (0, 1, 1),
            (0.7071, 0.7071, 1),
            (1, 0, 1),
            (0.7071, -0.7071, 1),
            (0, -1, 1)
        ]

        edges = []

        faces = [
            (0, 1, 2, 3, 4),
            (9, 8, 7, 6, 5),
            (3, 8, 9, 4),
            (2, 7, 8, 3),
            (1, 6, 7, 2),
            (0, 5, 6, 1)
        ]

        mesh_data = bpy.data.meshes.new("cube_mesh_data")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Black 8 Cylinder", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].width = 0.025
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        return {"FINISHED"}


class TwoCylinder(Operator):
    bl_idname = "mesh.def_sixteen"
    bl_label = "Defined Cylinder Add"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        # bpy.ops.mesh.primitive_cylinder_add(vertices=16)
        verts = [
            (0, 1, -1),
            (0.3827, 0.9239, -1),
            (0.7071, 0.7071, -1),
            (0.9239, 0.3827, -1),
            (1, 0, -1),
            (0.9239, -0.3927, -1),
            (0.7071, -0.7071, -1),
            (0.3827, -0.9239, -1),
            (0, -1, -1),
            # separator
            (0, 1, 1),
            (0.3827, 0.9239, 1),
            (0.7071, 0.7071, 1),
            (0.9239, 0.3827, 1),
            (1, 0, 1),
            (0.9239, -0.3927, 1),
            (0.7071, -0.7071, 1),
            (0.3827, -0.9239, 1),
            (0, -1, 1)
        ]

        edges = []

        faces = [
            (0, 1, 2, 3, 4, 5, 6, 7, 8),
            (17, 16, 15, 14, 13, 12, 11, 10, 9),
            (7, 16, 17, 8),
            (6, 15, 16, 7),
            (5, 14, 15, 6),
            (4, 13, 14, 5),
            (3, 12, 13, 4),
            (2, 11, 12, 3),
            (1, 10, 11, 2),
            (0, 9, 10, 1)
        ]

        mesh_data = bpy.data.meshes.new("cube_mesh_data")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Black 16 Cylinder", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].width = 0.025
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        return {"FINISHED"}


class ThreeCylinder(Operator):
    bl_idname = "mesh.def_thirty_two"
    bl_label = "Defined Cylinder Add"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        # bpy.ops.mesh.primitive_cylinder_add(vertices=32)
        verts = [
            (0, 1, -1),
            (0.195, 0.981, -1),
            (0.383, 0.924, -1),
            (0.5555, 0.8315, -1),
            (0.7071, 0.7071, -1),
            (0.8315, 0.5556, -1),
            (0.924, 0.383, -1),
            (0.981, 0.195, -1),
            (1, 0, -1),
            (0.9808, -0.1951, -1),
            (0.9239, -0.3827, -1),
            (0.8315, -0.5556, -1),
            (0.7071, -0.7071, -1),
            (0.5556, -0.8315, -1),
            (0.383, -0.924, -1),
            (0.195, -0.981, -1),
            (0, -1, -1),
            # Separator
            (0, -1, 1),
            (0.195, -0.981, 1),
            (0.383, -0.924, 1),
            (0.5555, -0.8315, 1),
            (0.7071, -0.7071, 1),
            (0.8315, -0.5556, 1),
            (0.924, -0.383, 1),
            (0.981, -0.195, 1),
            (1, 0, 1),
            (0.9808, 0.1951, 1),
            (0.9239, 0.3827, 1),
            (0.8315, 0.5556, 1),
            (0.7071, 0.7071, 1),
            (0.5556, 0.8315, 1),
            (0.383, 0.924, 1),
            (0.195, 0.981, 1),
            (0, 1, 1)
        ]

        edges = []

        faces = [
            (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33),
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16),
            (15, 18, 17, 16),
            (14, 19, 18, 15),
            (13, 20, 19, 14),
            (12, 21, 20, 13),
            (11, 22, 21, 12),
            (10, 23, 22, 11),
            (9, 24, 23, 10),
            (8, 25, 24, 9),
            (7, 26, 25, 8),
            (6, 27, 26, 7),
            (5, 28, 27, 6),
            (4, 29, 28, 5),
            (3, 30, 29, 4),
            (2, 31, 30, 3),
            (1, 32, 31, 2),
            (0, 33, 32, 1)
        ]

        mesh_data = bpy.data.meshes.new("cube_mesh_data")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Black 32 Cylinder", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].width = 0.025
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        return {"FINISHED"}


class OneSphere(Operator):
    bl_idname = "mesh.def_sphere_two"
    bl_label = "Defined Sphere Add"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "Black 2 Sphere"
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.subdivide(number_cuts=1, smoothness=1)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.9
        return {"FINISHED"}


class TwoSphere(Operator):
    bl_idname = "mesh.def_sphere_four"
    bl_label = "Defined Cylinder Add"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "Black 4 Sphere"
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.subdivide(number_cuts=3, smoothness=1)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        return {"FINISHED"}


class ThreeSphere(Operator):
    bl_idname = "mesh.def_sphere_eight"
    bl_label = "Defined Cylinder Add"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "Black 8 Sphere"
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.subdivide(number_cuts=7, smoothness=1)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        return {"FINISHED"}


class BooleanMode(Operator):
    bl_idname = "object.boolean_mode"
    bl_label = "Enter Boolean Mode"

    boolean_mode = True
    initial_name = ""
    duplicate_name = ""

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        self.__class__.boolean_mode = True
        self.__class__.initial_name = bpy.context.object.name
        bpy.ops.object.duplicate_move()
        self.__class__.duplicate_name = bpy.context.object.name
        if bpy.context.object.layers[0]:
            bpy.ops.object.move_to_layer(layers=(
                        False, True, False, False, False, False, False, False, False, False, False, False, False, False,
                        False, False, False, False, False, False))
        else:
           bpy.ops.object.move_to_layer(layers=(
                        True, False, False, False, False, False, False, False, False, False, False, False, False, False,
                        False,False, False, False, False, False))
        bpy.data.objects[self.__class__.initial_name].select = True
        bpy.context.scene.objects.active = bpy.data.objects[self.__class__.initial_name]
        bpy.data.objects[self.__class__.initial_name].modifiers.clear()
        return {"FINISHED"}


class ExitBooleanMode(Operator):
    bl_idname = "object.exit_boolean_mode"
    bl_label = "Exit Boolean Mode"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        mode = BooleanMode.boolean_mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            if current_mode == "OBJECT":
                if mode == True:
                    return True
                else:
                    return False
            else:
                return False

    def execute(self, context):
        # global duplicate_name
        # global initial_name
        # global boolean_mode
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        bpy.data.objects[BooleanMode.duplicate_name].select = True
        bpy.context.scene.objects.active = bpy.data.objects[BooleanMode.duplicate_name]
        bpy.data.objects[BooleanMode.initial_name].select = True
        bpy.ops.object.make_links_data(type="MODIFIERS")
        bpy.data.objects[BooleanMode.initial_name].select = False
        bpy.data.objects.remove(bpy.context.scene.objects[BooleanMode.duplicate_name])
        bpy.data.objects[BooleanMode.initial_name].select = True
        bpy.context.scene.objects.active = bpy.data.objects[BooleanMode.initial_name]
        BooleanMode.boolean_mode = False
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.610865
        return {"FINISHED"}


class ApplyMods(Operator):
    bl_idname = "object.mod_apply"
    bl_label = "Apply Modifiers"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.convert(target="MESH")
        return {"FINISHED"}


class ApplyModsAll(Operator):
    bl_idname = "object.mod_apply_all"
    bl_label = "Apply Modifiers to All"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.select_all(action="DESELECT")
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                obj.select = True
        bpy.ops.object.convert(target="MESH")
        #scene = bpy.context.scene
        #scene.objects.active = bpy.data.objects["template"]
        #for obj in scene.objects:
        #    if obj.type == "MESH":
        #        obj.select = True
        #bpy.ops.object.convert(target="MESH")
        #mat = bpy.data.materials.get("Material")
        #for ob in bpy.data.objects:
            #ob.data.object.convert(target="MESH")
            #self.report({"INFO"}, ob.name)
            #mat = bpy.data.materials.new(name=ob.name + " test material")
            #ob.data.materials.append(mat)
            #ob.data.materials.append(mat)
            #ob.data.materials.material_slot_remove()
            #ob.data.materials.new(name=ob.name + " TestMat")
            #self.report({"INFO"}, "Removed material from " + ob.name)
        #Converts object to mesh which has a side effect of applying all modifiers
        #bpy.ops.material.new()
        #for ob in bpy.data.objects:
        #    bpy.ops.ob.convert(target="MESH")
        return {"FINISHED"}


class PackUnwrap(Operator):
    bl_idname = "object.pack_unwrap"
    bl_label = "Pack Unwrap"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.uv.pack_islands(margin=0.001)
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}


class SharpUnwrap(Operator):
    bl_idname = "object.sharp_unwrap"
    bl_label = "Sharp Unwrap"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.uv.pack_islands(margin=0.001)
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}


class CubeUnwrap(Operator):
    bl_idname = "object.cube_unwrap"
    bl_label = "Cube Unwrap"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.select_all(action="TOGGLE")
        bpy.ops.uv.cube_project()
        bpy.ops.uv.pack_islands(margin=0.001)
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}


class CreateId(Operator):
    """Creates unique ID color on each discrete object in scene (which will bake in Susbtance Painter). Use BEFORE joining for texture sets"""
    bl_idname = "object.id_create"
    bl_label = "Create ID"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        def random_color(obj):
            import random
            r = random.random
            mesh = obj.data
            scn = bpy.context.scene
            scn.objects.active = obj
            obj.select = True
            if mesh.vertex_colors:
                vcol_layer = mesh.vertex_colors.active
            else:
                vcol_layer = mesh.vertex_colors.new()
            random_color = [r(), r(), r()]
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    vcol_layer.data[loop_index].color = random_color

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                random_color(obj)
        bpy.ops.paint.vertex_paint_toggle()
        return {"FINISHED"}


class CreateTexSet(Operator):
    bl_idname = "object.create_tex_set"
    bl_label = "Create Texture Set"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        for ob in bpy.context.selected_editable_objects:
            bpy.ops.object.convert(target="MESH")
            bpy.ops.object.join()
            mat = bpy.data.materials.new(name=ob.name + " Texture Set")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            for node in nodes:
                nodes.remove(node)
            group = nodes.new("ShaderNodeGroup")
            group.node_tree = bpy.data.node_groups["NodeGroup"]
            node_output = nodes.new(type="ShaderNodeOutputMaterial")
            node_output.location = 400, 0
            links = mat.node_tree.links
            link = links.new(group.outputs[0], node_output.inputs[0])
            ob.data.materials.append(mat)
        return {"FINISHED"}


class CreateMaterialSets(Operator):
    bl_idname = "scene.create_mat_sets"
    bl_label = "Create Material Sets"

    @classmethod
    def poll(cls, context):
        if bpy.context.object is None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.select_all(action="SELECT")
        for ob in bpy.context.selected_editable_objects:
            mat = bpy.data.materials.new(name=ob.name + " Texture Set")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            for node in nodes:
                nodes.remove(node)
            group = nodes.new("ShaderNodeGroup")
            group.node_tree = bpy.data.node_groups["NodeGroup"]
            node_output = nodes.new(type="ShaderNodeOutputMaterial")
            node_output.location = 400,0
            links = mat.node_tree.links
            link = links.new(group.outputs[0], node_output.inputs[0])
            ob.data.materials.append(mat)
        bpy.ops.object.select_all(action="DESELECT")
        return {"FINISHED"}


class ClearMaterials(Operator):
    bl_idname = "scene.clear_mat_sets"
    bl_label = "Clear Material Sets"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    def execute(self, context):
        bpy.ops.object.select_all(action="SELECT")
        for ob in bpy.context.selected_editable_objects:
            ob.active_material_index = 0
            for i in range(len(ob.material_slots)):
                bpy.ops.object.material_slot_remove({"object": ob})
        bpy.ops.object.select_all(action="DESELECT")
        return {"FINISHED"}


class SubstanceExport(Operator):
    bl_idname = "scene.substance_export"
    bl_label = "Substance Export"

    @classmethod
    def poll(self, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        if bpy.data.is_saved:
            i = 0
            bpy.ops.object.select_all(action="DESELECT")
            for ob in bpy.data.objects:
                if ob.type == "MESH":
                    if len(ob.data.uv_layers) == 0:
                        def warning(self, context):
                            self.layout.label("Object in scene missing UV!")
                        bpy.context.window_manager.popup_menu(warning, title="Error", icon='ERROR')
                        i = 1
                    elif len(ob.material_slots) == 0:
                        def warning(self, context):
                            self.layout.label("Missing texture set! (Object without material)")
                        bpy.context.window_manager.popup_menu(warning, title="Error", icon='ERROR')
                        i = 1
            if i == 0:
                bpy.ops.object.select_all(action="SELECT")
                filename = bpy.path.basename(bpy.context.blend_data.filepath)
                blendpath = bpy.path.abspath("//")
                filename = os.path.splitext(filename)[0]
                bpy.ops.export_scene.fbx(filepath=blendpath + filename + ".fbx", use_selection=True, axis_forward='-Z',
                                                  axis_up='Y')
                def warning(self, context):
                    self.layout.label("Scene Exported.")
                bpy.context.window_manager.popup_menu(warning, title="Info", icon='INFO')
            bpy.ops.object.select_all(action="DESELECT")
        else:
            def warning(self, context):
                 self.layout.label("Blend file is not saved!")
            bpy.context.window_manager.popup_menu(warning, title="Error", icon='ERROR')
        return {"FINISHED"}


#=======================================================================


def set_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    all_modifiers = bpy.context.window_manager.all_modifiers

    if not all_modifiers:
        for name, icon, mod in all_name_icon_type():
            item = all_modifiers.add()
            item.name = name
            item.value = mod


@persistent
def on_file_load(dummy):
    set_modifier_collection_items()


# classes = (
#     Preferences,
#     AllModifiersCollection,
#     OBJECT_MT_mpp_add_modifier_menu,
#     OBJECT_UL_modifier_list,
#     OBJECT_OT_mpp_modifier_move_up,
#     OBJECT_OT_mpp_modifier_move_down,
#     OBJECT_OT_mpp_modifier_remove,
#     OBJECT_OT_mpp_modifier_add,
#     OBJECT_OT_mpp_modifier_apply,
#     OBJECT_OT_mpp_modifier_copy,
#     VIEW_3D_PT_modifier_popup,
# )

addon_keymaps = []

preview_collections = {}


def register():
    #for cls in classes:
    #    bpy.utils.register_class(cls)
    bpy.utils.register_module(__name__)
    bpy.types.Object.modifier_active_index = IntProperty()

    # Use Window Manager for storing modifier search property
    # and modifier collection because it can be accessed on
    # registering and it's not scene specific.
    wm = bpy.types.WindowManager
    wm.mod_to_add = StringProperty(name="Modifier to add", update=add_modifier,
                                   description="Search for a modifier and add it to the stack")
    wm.all_modifiers = CollectionProperty(type=AllModifiersCollection)

    bpy.app.handlers.load_post.append(on_file_load)

    set_modifier_collection_items()

    # Keymap
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(VIEW_3D_PT_modifier_popup.bl_idname, 'B', 'PRESS', shift=True, ctrl=True, alt=True)
        kmi.active = True
        kmim = km.keymap_items.new("wm.call_menu", "Q", "PRESS")
        kmim.properties.name = BlackOps.bl_idname
        addon_keymaps.append((km, kmi))
        addon_keymaps.append((km, kmim))

    # Icons
    from bpy.utils import previews
    pcoll = previews.new()

    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    icons_dir_files = os.listdir(icons_dir)

    all_icon_files = [icon for icon in icons_dir_files if icon.endswith(".png")]
    all_icon_names = [icon[0:-4] for icon in all_icon_files]
    all_icon_files_and_names = zip(all_icon_names, all_icon_files)

    for icon_name, icon_file in all_icon_files_and_names:
        pcoll.load(icon_name, os.path.join(icons_dir, icon_file), 'IMAGE')

    preview_collections["main"] = pcoll


def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_module(__name__)
    #for cls in classes:
    #    bpy.utils.unregister_class(cls)

    bpy.app.handlers.load_post.remove(on_file_load)

    del bpy.types.Object.modifier_active_index

if __name__ == "__main__":
    register()

