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
    "name": "Modifier Popup Panel",
    "author": "Antti Tikka",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Spacebar",
    "description": "A handy popup panel for showing modifiers in 3D view",
    "warning": "",
    "wiki_url": "",
    "category": "3d View"
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

    modifier_01: StringProperty()
    modifier_02: StringProperty()
    modifier_03: StringProperty()
    modifier_04: StringProperty()
    modifier_05: StringProperty()
    modifier_06: StringProperty()
    modifier_07: StringProperty()
    modifier_08: StringProperty()
    modifier_09: StringProperty()
    modifier_10: StringProperty()
    modifier_11: StringProperty()
    modifier_12: StringProperty()

    mod_list_def_len: IntProperty(name="",
                                  description="Default/min number of rows to display in the modifier list",
                                  default=7)

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
            row = col.split(factor=0.5, align=True)
            row.prop_search(self, attr, wm, "all_modifiers", text="", icon='MODIFIER')
            row.prop_search(self, next(attr_iter), wm, "all_modifiers", text="", icon='MODIFIER')

        layout.separator()

        # === Number of rows in the modifier list ===
        layout.label(text="Default/min number of rows to display in the modifier list:")

        row = layout.row()
        split = row.split(factor=0.5)
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


#=======================================================================


def get_pref_mod_attr_name():
    """List of the names of favourite modifier attributes in Preferences
    class for making drawing favourite modifier selection rows in
    preferences easy.
    """
    attr_name_list = [attr for attr in Preferences.__annotations__ if "modifier_" in attr]
    return attr_name_list


def get_pref_mod_attr_value():
    """List of the names of favourite modifiers"""
    prefs = bpy.context.preferences.addons[__name__].preferences
    # get correct class attributes and then their values
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


def mod_show_editmode_and_cage(modifier, layout, scale_x=1.0, emboss=True,
                               enable_inactive_icons=False):
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

    has_no_show_in_editmode = {
        'MESH_SEQUENCE_CACHE', 'BUILD', 'DECIMATE', 'MULTIRES', 'CLOTH', 'COLLISION',
        'DYNAMIC_PAINT','EXPLODE', 'FLUID_SIMULATION', 'PARTICLE_SYSTEM','SMOKE', 'SOFT_BODY'
    }

    deform_mods = {mod for name, icon, mod in all_name_icon_type()[25:41]}
    other_show_on_cage_mods = {
        'DATA_TRANSFER', 'NORMAL_EDIT', 'WEIGHTED_NORMAL', 'UV_PROJECT','VERTEX_WEIGHT_EDIT',
        'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_PROXIMITY', 'ARRAY', 'EDGE_SPLIT', 'MASK', 'MIRROR',
        'SOLIDIFY', 'SUBSURF', 'TRIANGULATE'
    }
    has_show_on_cage = deform_mods.union(other_show_on_cage_mods)

    pcoll = preview_collections["main"]

    # === show_in_editmode ===
    sub = layout.row(align=True)
    sub.scale_x = scale_x
    sub.active = modifier.show_viewport
    if modifier.type not in has_no_show_in_editmode:
        if not modifier.show_viewport and enable_inactive_icons:
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
                 emboss=emboss)

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
                sub.active = False
                if enable_inactive_icons:
                    show_on_cage_on = pcoll['SHOW_ON_CAGE_ON_INACTIVE']
                    show_on_cage_off = pcoll['SHOW_ON_CAGE_OFF_INACTIVE']
                else:
                    show_on_cage_on = pcoll['SHOW_ON_CAGE_ON_INACTIVE_BUTTON']
            icon = show_on_cage_on.icon_id if modifier.show_on_cage else show_on_cage_off.icon_id
            sub.prop(modifier, "show_on_cage", text="", icon_value=icon, emboss=emboss)


#=======================================================================


class AllModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="my modifier")


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
        col.separator(factor=0.3)
        for name, icon, mod in all_name_icon_type()[0:10]:
            col.operator("object.mpp_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Generate")
        col.separator(factor=0.3)
        for name, icon, mod in all_name_icon_type()[10:26]:
            col.operator("object.mpp_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Deform")
        col.separator(factor=0.3)
        for name, icon, mod in all_name_icon_type()[26:42]:
            col.operator("object.mpp_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Simulate")
        col.separator(factor=0.3)
        for name, icon, mod in all_name_icon_type()[42:52]:
            col.operator("object.mpp_modifier_add", text=name, icon=icon).modifier_type = mod


class OBJECT_UL_modifier_list(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if mod:
                col = layout.column()
                row = col.split(factor=0.70)
                sub = row.row(align=True)
                sub.label(text="", translate=False, icon_value=layout.icon(mod))
                sub.prop(mod, "name", text="", emboss=False, icon_value=icon)

                # Hide visibility toggles for collision modifier as they are not used
                # in the regular UI either (apparently can cause problems in some scenes).
                if mod.type != 'COLLISION':
                    sub = row.row(align=True)
                    sub.prop(mod, "show_viewport", text="", emboss=False)
                    sub.prop(mod, "show_render", text="", emboss=False)
                    mod_show_editmode_and_cage(mod, sub, emboss=False, enable_inactive_icons=True)
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

    modifier_type: StringProperty()

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

    modifier: StringProperty()

    apply_as: EnumProperty(
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

        return {'FINISHED'}


class OBJECT_OT_mpp_modifier_copy(Operator):
    bl_idname = "object.mpp_modifier_copy"
    bl_label = "Copy Modifier"
    bl_description = "Duplicate modifier at the same position in the stack"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier: StringProperty()

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

            # Check if an item or the next item in fav_name_icon_type has a value
            # and add rows and buttons accordingly (two buttons per row).
            fav_name_icon_type_iter = fav_name_icon_type()

            for name, icon, mod in fav_name_icon_type_iter:
                next_mod = next(fav_name_icon_type_iter)
                if name or next_mod[0] is not None:
                    row = col.split(factor=0.5, align=True)

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
            row = col.split(factor=0.59)
            wm = bpy.context.window_manager
            row.prop_search(wm, "mod_to_add", wm, "all_modifiers", text="", icon='MODIFIER')
            row.menu("OBJECT_MT_mpp_add_modifier_menu")

            # === Modifier list ===
            ob = context.object

            prefs = bpy.context.preferences.addons[__name__].preferences
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
            sub.operator(OBJECT_OT_mpp_modifier_remove.bl_idname, icon='REMOVE', text="")

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
                    sub_sub.scale_x = 1.1
                    # Hide visibility toggles for collision modifier as they are not used
                    # in the regular UI either (apparently can cause problems in some scenes).
                    if active_mod.type != 'COLLISION':
                        sub_sub.prop(active_mod, "show_viewport", text="")
                        sub_sub.prop(active_mod, "show_render", text="")
                    mod_show_editmode_and_cage(active_mod, sub, scale_x=1.1)

                    row = box.row()
                    row.operator("object.mpp_modifier_apply",
                                 text="Apply").modifier = active_mod.name

                    sub = row.row()
                    # Cloth and Soft Body have "Apply As Shape Key" but no "Copy Modifier" .
                    # In those cases "Apply As Shape Key" doesn't need to be scaled up.
                    if active_mod.type not in {'CLOTH', 'SOFT_BODY'}:
                        sub.scale_x = 1.3
                    deform_mods = {mod for name, icon, mod in all_name_icon_type()[26:42]}
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


classes = (
    Preferences,
    AllModifiersCollection,
    OBJECT_MT_mpp_add_modifier_menu,
    OBJECT_UL_modifier_list,
    OBJECT_OT_mpp_modifier_move_up,
    OBJECT_OT_mpp_modifier_move_down,
    OBJECT_OT_mpp_modifier_remove,
    OBJECT_OT_mpp_modifier_add,
    OBJECT_OT_mpp_modifier_apply,
    OBJECT_OT_mpp_modifier_copy,
    VIEW_3D_PT_modifier_popup,
)

addon_keymaps = []

preview_collections = {}


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

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
        kmi = km.keymap_items.new(VIEW_3D_PT_modifier_popup.bl_idname, 'SPACE', 'PRESS')
        kmi.active = True
        addon_keymaps.append((km, kmi))

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

    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

    bpy.app.handlers.load_post.remove(on_file_load)

    del bpy.types.Object.modifier_active_index

if __name__ == "__main__":
    register()

