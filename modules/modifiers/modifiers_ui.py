import math
import numpy as np

import addon_utils
from bl_ui.properties_data_modifier import DATA_PT_modifiers
import bpy
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import (
    Menu,
    Operator,
    PropertyGroup,
    UIList
)

from .. import icons


# Favourite modifiers and name + icon + type iteratables
#=======================================================================

def get_pref_mod_attr_value():
    """List of the names of favourite modifiers"""
    prefs = bpy.context.preferences.addons["modifier_list"].preferences
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


# show_in_editmode and show_on_cage buttons
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

    pcoll = icons.preview_collections["main"]

    # === show_in_editmode ===
    sub = layout.row(align=True)
    sub.scale_x = scale_x
    if not use_in_list:
        sub.active = modifier.show_viewport
    if modifier.type not in has_no_show_in_editmode:
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

# Modifier list and operator classes etc.
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


class OBJECT_MT_ml_add_modifier_menu(Menu):
    bl_label = "Add Modifier"
    bl_idname = "OBJECT_MT_ml_add_modifier_menu"
    bl_description = "Add a procedural operation/effect to the active object"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.alignment = 'LEFT'

        col = row.column()
        col.label(text="Modify")
        col.separator(factor=0.3)
        for name, icon, mod in all_name_icon_type()[0:10]:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Generate")
        col.separator(factor=0.3)
        for name, icon, mod in all_name_icon_type()[10:26]:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Deform")
        col.separator(factor=0.3)
        for name, icon, mod in all_name_icon_type()[26:42]:
            col.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod

        col = row.column()
        col.label(text="Simulate")
        col.separator(factor=0.3)
        for name, icon, mod in all_name_icon_type()[42:52]:
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
    bl_description = "Remove modifier from the active object"

    action = 'REMOVE'


class OBJECT_OT_ml_modifier_add(Operator):
    bl_idname = "object.ml_modifier_add"
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



class OBJECT_OT_ml_modifier_apply(Operator):
    bl_idname = "object.ml_modifier_apply"
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

        # Set correct active_mod index in case the applied modifier is
        # not the first in modifier stack.
        ob = context.object
        current_active_mod_index = ob.modifier_active_index
        new_active_mod_index = np.clip(current_active_mod_index - 1, 0, 99)
        ob.modifier_active_index = new_active_mod_index

        if current_active_mod_index != 0:
            self.report({'INFO'}, "Applied modifier was not first, result may not be as expected")

        return {'FINISHED'}


class OBJECT_OT_ml_modifier_copy(Operator):
    bl_idname = "object.ml_modifier_copy"
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


# UI
#=======================================================================


def modifiers_ui(context, layout, num_of_rows=False):
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
                row.operator("object.ml_modifier_add", text=name,
                                            icon=icon).modifier_type = mod
            else:
                row.label(text="")

            if next_mod[0] is not None:
                row.operator("object.ml_modifier_add", text=next_mod[0],
                                icon=next_mod[1]).modifier_type = next_mod[2]
            else:
                row.label(text="")

    # === Modifier search and menu ===
    col = layout.column()
    row = col.split(factor=0.59)
    wm = bpy.context.window_manager
    row.prop_search(wm, "mod_to_add", wm, "all_modifiers", text="", icon='MODIFIER')
    row.menu("OBJECT_MT_ml_add_modifier_menu")

    # === Modifier list ===
    ob = context.object

    layout.template_list("OBJECT_UL_modifier_list", "", ob, "modifiers",
                            ob, "modifier_active_index", rows=num_of_rows)

    row = layout.row()

    # === Modifier tools (from the addon) ===
    is_loaded, is_enabled = addon_utils.check("space_view3d_modifier_tools")
    if is_loaded and is_enabled:
        sub = row.row(align=True)
        # Note: In 2.79, this is what scale 2.0 looks like. Here 2.0 causes list ordering
        # buttons to get tiny. 2.8 Bug?
        sub.scale_x = 1.5

        pcoll = icons.preview_collections["main"]

        icon = pcoll['TOGGLE_ALL_MODIFIERS_VISIBILITY']
        sub.operator("object.toggle_apply_modifiers_view", icon_value=icon.icon_id, text="")

        icon = pcoll['APPLY_ALL_MODIFIERS']
        sub.operator("object.apply_all_modifiers", icon_value=icon.icon_id, text="")

        icon = pcoll['DELETE_ALL_MODIFIERS']
        sub.operator("object.delete_all_modifiers", icon_value=icon.icon_id, text="")

    # === List manipulation ===
    sub = row.row(align=True)
    #  Note: In 2.79, this is what scale 2.0 looks like. Here 2.0 causes list ordering
    # buttons to get tiny. 2.8 Bug?
    sub.scale_x = 1.5
    sub.alignment = 'RIGHT'
    sub.operator(OBJECT_OT_ml_modifier_move_up.bl_idname, icon='TRIA_UP', text="")
    sub.operator(OBJECT_OT_ml_modifier_move_down.bl_idname, icon='TRIA_DOWN', text="")
    sub.operator(OBJECT_OT_ml_modifier_remove.bl_idname, icon='REMOVE', text="")

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
                sub_sub.prop(active_mod, "show_render", text="")
                sub_sub.prop(active_mod, "show_viewport", text="")
            mod_show_editmode_and_cage(active_mod, sub, scale_x=1.1)

            row = box.row()
            row.operator("object.ml_modifier_apply",
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
                apply_as_shape_key = sub.operator("object.ml_modifier_apply",
                                                    text="Apply as Shape Key")
                apply_as_shape_key.modifier=active_mod.name
                apply_as_shape_key.apply_as='SHAPE'

            has_no_copy = {
                'CLOTH', 'COLLISION', 'DYNAMIC_PAINT', 'FLUID_SIMULATION',
                'PARTICLE_SYSTEM', 'SMOKE', 'SOFT_BODY'
            }
            if active_mod.type not in has_no_copy:
                row.operator("object.ml_modifier_copy",
                                text="Copy").modifier = active_mod.name

            # === Modifier specific settings ===
            box = col.box()
            # A column is needed here to keep the layout more compact,
            # because in a box separators give an unnecessarily big space.
            col = box.column()
            mp = DATA_PT_modifiers(context)
            getattr(mp, active_mod.type)(col, ob, active_mod)


# Registering
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


def register():
    # === Properties ===
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


def unregister():
    bpy.app.handlers.load_post.remove(on_file_load)

    del bpy.types.Object.modifier_active_index