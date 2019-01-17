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
    "blender": (2, 79, 0),
    "location": "Spacebar",
    "description": "A handy popup panel for showing modifiers in 3D view",
    "warning": "",
    "wiki_url": "",
    "category": "3d View"
}


import math
import numpy as np

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

    def draw(self, context):
        layout = self.layout

        # === Favourite modifiers selection ===
        layout.label(text="Favourite modifiers:")

        col = layout.column(align=True)

        num_of_mods = len(get_pref_attr_name())
        num_of_rows = math.ceil(num_of_mods / 2)

        attr_iter = iter(get_pref_attr_name())

        wm = bpy.context.window_manager

        # Draw two property searches per row
        for attr in attr_iter:
            row = col.split(percentage=0.5, align=True)
            row.prop_search(self, attr, wm, "all_modifiers", text="", icon='MODIFIER')
            row.prop_search(self, next(attr_iter), wm, "all_modifiers", text="", icon='MODIFIER')

        col.separator()

        # === Hotkey ===
        col.label(text="Hotkey:")

        col = layout.column()
        kc = bpy.context.window_manager.keyconfigs.addon
        for km, kmi in addon_keymaps:
            km = km.active()
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)


#=======================================================================


def get_pref_attr_name():
    """For drawing favourite modifier selection rows in preferences."""

    attr_name_list = [attr for attr in dir(Preferences) if "modifier_" in attr]

    return attr_name_list


def get_pref_attr_value():
    """For buttons in pop-up panel."""

    fav_mods = bpy.context.user_preferences.addons[__name__].preferences
    # get correct class attributes and then their values
    attr_list = [attr for attr in dir(fav_mods) if "modifier_" in attr]
    attr_value_list = [getattr(fav_mods, attr) for attr in attr_list]

    return attr_value_list


def all_name_icon_type():
    """List of all modifier names, icons and types."""

    mods_enum = bpy.types.Modifier.bl_rna.properties['type'].enum_items

    all_mod_names = [modifier.name for modifier in mods_enum]
    all_mod_icons = [modifier.icon for modifier in mods_enum]
    all_mod_types = [modifier.identifier for modifier in mods_enum]

    all_mods_zipped = list(zip(all_mod_names, all_mod_icons, all_mod_types))

    return all_mods_zipped


def fav_name_icon_type():
    """Iterator of favourite modifier names, icons and types."""

    mods_enum = bpy.types.Modifier.bl_rna.properties['type'].enum_items
    all_mod_names = [modifier.name for modifier in mods_enum]
    all_mods_dict = dict(zip(all_mod_names, all_name_icon_type()))
    fav_mods_list = [all_mods_dict[mod] if mod in all_mods_dict else (None, None, None)
                     for mod in get_pref_attr_value()]
    fav_mods_iter = iter(fav_mods_list)

    return fav_mods_iter


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

    # Executing an operator via function doesn't create an undo event,
    # so it needs to be added manually.
    bpy.ops.ed.undo_push(message="Add Modifier")


class OBJECT_MT_custom_add_modifier_menu(Menu):
    bl_label = "Add Modifier"
    bl_idname = "OBJECT_MT_custom_add_modifier_menu"
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
            col.operator("object.custom_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Generate")

        sub = col.column()
        sub.scale_y = 0.3
        sub.separator()

        for name, icon, mod in all_name_icon_type()[9:25]:
            col.operator("object.custom_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Deform")

        sub = col.column()
        sub.scale_y = 0.3
        sub.separator()

        for name, icon, mod in all_name_icon_type()[25:41]:
            col.operator("object.custom_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Simulate")
        sub = col.column()
        sub.scale_y = 0.3
        sub.separator()

        for name, icon, mod in all_name_icon_type()[41:51]:
            col.operator("object.custom_modifier_add", text=name, icon=icon).modifier_type = mod


class MODIFIERS_UL_modifier_list(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if mod:
                layout.label(text="", translate=False, icon_value=layout.icon(mod))
                layout.prop(mod, "name", text="", emboss=False, icon_value=icon)

                # Hide visibility toggles for collision modifier as they are not used
                # in the regular UI either (apparently can cause problems in some scenes)
                if mod.type != 'COLLISION':
                    icon = 'RESTRICT_VIEW_OFF' if mod.show_viewport else 'RESTRICT_VIEW_ON'
                    layout.prop(mod, "show_viewport", text="", icon=icon, emboss=False)

                    icon = 'RESTRICT_RENDER_OFF' if mod.show_render else 'RESTRICT_RENDER_ON'
                    layout.prop(mod, "show_render", text="", icon=icon, emboss=False)

                icon = 'EDITMODE_HLT' if mod.show_in_editmode else 'OBJECT_DATAMODE'
                layout.prop(mod, "show_in_editmode", text="", icon=icon, emboss=False)

                icon = 'OUTLINER_OB_MESH' if mod.show_on_cage else 'MESH_DATA'
                layout.prop(mod, "show_on_cage", text="", icon=icon, emboss=False)
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

            if self.action == 'DOWN':
                bpy.ops.object.modifier_move_down(modifier=active_mod_name)
                ob.modifier_active_index = active_mod_index_down

            if self.action == 'REMOVE':
                bpy.ops.object.modifier_remove(modifier=active_mod_name)
                ob.modifier_active_index = active_mod_index_up

        return {'FINISHED'}


class OBJECT_OT_custom_modifier_move_up(ModifierListActions):
    bl_idname = "object.custom_modifier_move_up"
    bl_label = "Move modifier up"
    bl_description = "Move modifier up in the stack"

    action = 'UP'


class OBJECT_OT_custom_modifier_move_down(ModifierListActions):
    bl_idname = "object.custom_modifier_move_down"
    bl_label = "Move modifier down"
    bl_description = "Move modifier down in the stack"

    action = 'DOWN'


class OBJECT_OT_custom_modifier_remove(ModifierListActions):
    bl_idname = "object.custom_modifier_remove"
    bl_label = "Remove Modifier"
    bl_description = "Remove modifier from the active object"

    action = 'REMOVE'


class OBJECT_OT_custom_modifier_add(Operator):
    bl_idname = "object.custom_modifier_add"
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



class OBJECT_OT_custom_modifier_apply(Operator):
    bl_idname = "object.custom_modifier_apply"
    bl_label = "Apply Modifier"
    bl_description = "Apply modifier and remove from the stack"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier = StringProperty()

    apply_as = EnumProperty(
        items=(
            ('DATA', "Data", ""),
            ('SHAPE', "Shape", "")),
        default='DATA')


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


class OBJECT_OT_custom_modifier_copy(Operator):
    bl_idname = "object.custom_modifier_copy"
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
            # and add rows and buttons accordingly (two buttons per row)
            for name, icon, mod in fav_name_icon_type_iter:
                next_mod = next(fav_name_icon_type_iter)
                if name or next_mod[0] is not None:
                    row = col.split(percentage=0.5, align=True)

                    if name is not None:
                        add_modifer = row.operator("object.custom_modifier_add",
                                                   text=name,
                                                   icon=icon).modifier_type = mod
                    else:
                        row.label(text="")

                    if next_mod[0] is not None:
                        row.operator("object.custom_modifier_add",
                                     text=next_mod[0],
                                     icon=next_mod[1]).modifier_type = next_mod[2]
                    else:
                        row.label(text="")

            # === Modifier search and menu ===
            col = layout.column()
            wm = bpy.context.window_manager
            row = col.split(percentage=0.65)
            row.prop_search(wm, "mod_to_add", wm, "all_modifiers", text="", icon='MODIFIER')
            row.menu("OBJECT_MT_custom_add_modifier_menu")

            # === Modifier list ===
            ob = context.object

            layout.template_list("MODIFIERS_UL_modifier_list", "", ob, "modifiers",
                                 ob, "modifier_active_index")

            # === Modifier tools (from the addon) ===
            row = layout.row()

            sub = row.row(align=True)
            sub.scale_x = 2.0
            sub.operator("object.toggle_apply_modifiers_view", icon='RESTRICT_VIEW_OFF', text="")
            sub.operator("object.apply_all_modifiers", icon='IMPORT', text="")
            sub.operator("object.delete_all_modifiers", icon='X', text="")

            # === List manipulation ===
            sub = row.row(align=True)
            sub.scale_x = 2.0
            sub.alignment = 'RIGHT'
            sub.operator(OBJECT_OT_custom_modifier_move_up.bl_idname, icon='TRIA_UP', text="")
            sub.operator(OBJECT_OT_custom_modifier_move_down.bl_idname, icon='TRIA_DOWN', text="")
            sub.operator(OBJECT_OT_custom_modifier_remove.bl_idname, icon='ZOOMOUT', text="")

            # === Modifier settings ===
            ob = context.object

            row = layout.row()
            if ob:
                if ob.modifiers:
                    active_mod_index = ob.modifier_active_index
                    active_mod = ob.modifiers[active_mod_index]

                    active_mod_icon = [icon for name, icon, mod in all_name_icon_type()
                                       if mod == active_mod.type].pop()

                    column = layout.column(align=True)

                    # === General settings ===
                    box = column.box()
                    row = box.row()
                    sub = row.row()
                    sub.label(text="", icon=active_mod_icon)
                    sub.prop(active_mod, "name", text="")

                    sub = row.row(align=True)
                    sub.scale_x = 1.2
                    sub.alignment = 'RIGHT'
                    # Hide visibility toggles for collision modifier as they are not used
                    # in the regular UI either (apparently can cause problems in some scenes)
                    if active_mod.type != 'COLLISION':
                        sub.prop(active_mod, "show_viewport", text="")
                        sub.prop(active_mod, "show_render", text="")
                    sub.prop(active_mod, "show_in_editmode", text="")
                    sub.prop(active_mod, "show_on_cage", text="")

                    row = box.row()
                    row.operator("object.custom_modifier_apply",
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
                        apply_as_shape_key = sub.operator("object.custom_modifier_apply",
                                                          text="Apply as Shape Key")
                        apply_as_shape_key.modifier=active_mod.name
                        apply_as_shape_key.apply_as='SHAPE'

                    has_no_copy = {'CLOTH', 'COLLISION', 'DYNAMIC_PAINT', 'FLUID_SIMULATION',
                                   'PARTICLE_SYSTEM', 'SMOKE', 'SOFT_BODY'}
                    if active_mod.type not in has_no_copy:
                        row.operator("object.custom_modifier_copy",
                                     text="Copy").modifier = active_mod.name

                    # === Modifier specific settings ===
                    box = column.box()
                    mp = DATA_PT_modifiers(context)
                    getattr(mp, active_mod.type)(box, ob, active_mod)


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
    OBJECT_MT_custom_add_modifier_menu,
    MODIFIERS_UL_modifier_list,
    OBJECT_OT_custom_modifier_move_up,
    OBJECT_OT_custom_modifier_move_down,
    OBJECT_OT_custom_modifier_remove,
    OBJECT_OT_custom_modifier_add,
    OBJECT_OT_custom_modifier_apply,
    OBJECT_OT_custom_modifier_copy,
    VIEW_3D_PT_modifier_popup,
)

addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.modifier_active_index = IntProperty()

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


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.load_post.remove(on_file_load)

    del bpy.types.Object.modifier_active_index

if __name__ == "__main__":
    register()

