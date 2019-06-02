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
    PropertyGroup,
    UIList
)

from . import ml_modifier_layouts, modifier_categories
from .. import icons


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
        ob = bpy.context.object
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


# Functions for adding a gizmo object
# ======================================================================

def _get_ml_collection(context):
    """Get the ml gizmo collection or create it if it doesnt exist yet"""
    scene = context.scene

    if "ML_Gizmo Objects" not in scene.collection.children:
        ml_col = bpy.data.collections.new("ML_Gizmo Objects")
        scene.collection.children.link(ml_col)
    else:
        ml_col = bpy.data.collections["ML_Gizmo Objects"]

    return ml_col


def _create_gizmo_object(self, context, modifier, place_at_vertex):
    """Create a gizmo (empty) object"""
    ob = context.object
    ob.update_from_editmode()
    ob_mat = ob.matrix_world
    mesh = ob.data

    sel_verts = [v for v in mesh.vertices if v.select]

    if place_at_vertex :
        if len(sel_verts) != 1:
            self.report(type={'INFO'}, message="Please, select (only) a single vertex")
            return
        else:
            vert_loc = ob_mat @ sel_verts[0].co

    gizmo_ob = bpy.data.objects.new(modifier + "_Gizmo Object", None)

    if place_at_vertex:
        gizmo_ob.location = vert_loc
    else:
        gizmo_ob.location = ob_mat.to_translation()

    ml_col = _get_ml_collection(context)
    ml_col.objects.link(gizmo_ob)

    return gizmo_ob


def assign_gizmo_object_to_modifier(self, context, modifier, place_at_vertex=False):
    """Assign a gizmo object to the correct property of the given modifier"""
    ob = context.object
    mod = ob.modifiers[modifier]

    # If modifier is UV Project, handle it differently here
    if mod.type == 'UV_PROJECT':
        projectors = ob.modifiers[modifier].projectors
        projector_count = ob.modifiers[modifier].projector_count

        for p in projectors[0:projector_count]:
            if not p.object:
                gizmo_ob = _create_gizmo_object(self, context, modifier,
                                                place_at_vertex=place_at_vertex)
                p.object = gizmo_ob
                break

        return

    # If modifier is not UV Project, continue normally
    gizmo_ob = _create_gizmo_object(self, context, modifier, place_at_vertex=place_at_vertex)

    if mod.type == 'ARRAY':
        mod.use_object_offset = True

    gizmo_ob_prop = modifier_categories.have_gizmo_property[mod.type]

    setattr(mod, gizmo_ob_prop, gizmo_ob)


# Modifier list and operator classes etc.
#=======================================================================

class MeshModifiersCollection(PropertyGroup):
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

    ob = context.object

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
        ob = context.object
        mods = ob.modifiers
        mods_len = len(mods) - 1
        active_mod_index = ob.ml_modifier_active_index
        active_mod_index_up = np.clip(active_mod_index - 1, 0, mods_len)
        active_mod_index_down = np.clip(active_mod_index + 1, 0, mods_len)

        if mods:
            active_mod_name = ob.modifiers[active_mod_index].name

            if self.action == 'UP':
                bpy.ops.object.modifier_move_up(modifier=active_mod_name)
                ob.ml_modifier_active_index = active_mod_index_up
            elif self.action == 'DOWN':
                bpy.ops.object.modifier_move_down(modifier=active_mod_name)
                ob.ml_modifier_active_index = active_mod_index_down
            elif self.action == 'REMOVE':
                bpy.ops.object.modifier_remove(modifier=active_mod_name)
                ob.ml_modifier_active_index = active_mod_index_up

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

        ob = context.object

        # Enable auto smooth if modifier is weighted normal
        if self.modifier_type == 'WEIGHTED_NORMAL':
            ob.data.use_auto_smooth = True

        # Set correct active_mod index
        mods = ob.modifiers
        mods_len = len(mods) - 1
        ob.ml_modifier_active_index = mods_len

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
        current_active_mod_index = ob.ml_modifier_active_index
        new_active_mod_index = np.clip(current_active_mod_index - 1, 0, 99)
        ob.ml_modifier_active_index = new_active_mod_index

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
        active_index = ob.ml_modifier_active_index
        ob.ml_modifier_active_index = active_index + 1

        return {'FINISHED'}


class OBJECT_OT_ml_create_gizmo_object(Operator):
    bl_idname = "object.ml_create_gizmo_object"
    bl_label = "Add Gizmo Object"
    bl_description = ("Add a gizmo object to the modifier.\n"
                      "\n"
                      "\u2022 Click to place it at the origin of the active object.\n"
                      "\u2022 Click + Hold shift to place it at the selected vertex")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier: StringProperty()

    def execute(self, context):
        assign_gizmo_object_to_modifier(self, context, self.modifier, self.place_at_vertex)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.place_at_vertex = True if event.shift else False

        return self.execute(context)


# UI
#=======================================================================

def modifiers_ui(context, layout, num_of_rows=False):
    ob = context.object

    # === Favourite modifiers ===
    col = layout.column(align=True)

    # Check if an item or the next item in
    # favourite_modifiers_names_icons_types has a value and add rows
    # and buttons accordingly (two buttons per row).
    fav_names_icons_types_iter = modifier_categories.favourite_modifiers_names_icons_types()

    for name, icon, mod in fav_names_icons_types_iter:
        next_mod = next(fav_names_icons_types_iter)
        if name or next_mod[0] is not None:
            row = col.split(factor=0.5, align=True)

            if name is not None:
                row.operator("object.ml_modifier_add", text=name, icon=icon).modifier_type = mod
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
    if ob.type == 'MESH':
        row.prop_search(wm, "ml_mod_to_add", wm, "ml_mesh_modifiers", text="", icon='MODIFIER')
        row.menu("MESH_MT_ml_add_modifier_menu")
    elif ob.type in {'CURVE', 'SURFACE', 'FONT'}:
        row.prop_search(wm, "ml_mod_to_add", wm, "ml_mesh_modifiers", text="", icon='MODIFIER')
        row.menu("CURVE_MT_ml_add_modifier_menu")
    elif ob.type == 'LATTICE':
        row.prop_search(wm, "ml_mod_to_add", wm, "ml_mesh_modifiers", text="", icon='MODIFIER')
        row.menu("LATTICE_MT_ml_add_modifier_menu")


    # === Modifier list ===
    layout.template_list("OBJECT_UL_modifier_list", "", ob, "modifiers",
                         ob, "ml_modifier_active_index", rows=num_of_rows)

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
    if ob:
        if ob.modifiers:
            active_mod_index = ob.ml_modifier_active_index
            active_mod = ob.modifiers[active_mod_index]

            all_modifier_names_icons_types = modifier_categories.all_modifier_names_icons_types

            active_mod_icon = [icon for name, icon, mod in all_modifier_names_icons_types()
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

            if active_mod.type in modifier_categories.support_apply_as_shape_key:
                apply_as_shape_key = sub.operator("object.ml_modifier_apply",
                                                    text="Apply as Shape Key")
                apply_as_shape_key.modifier=active_mod.name
                apply_as_shape_key.apply_as='SHAPE'

            if active_mod.type not in modifier_categories.dont_support_copy:
                row.operator("object.ml_modifier_copy",
                             text="Copy").modifier = active_mod.name

            # === Gizmo object settings ===
            if (active_mod.type in modifier_categories.have_gizmo_property
                    or active_mod.type == 'UV_PROJECT'):
                box = col.box()
                box.operator("object.ml_create_gizmo_object", text="", icon='EMPTY_DATA'
                            ).modifier = active_mod.name

            # === Modifier specific settings ===
            box = col.box()
            # A column is needed here to keep the layout more compact,
            # because in a box separators give an unnecessarily big space.
            col = box.column()
            # Custom layouts for laplacian deform, mesh deform and
            # surface deform because bind button doesn't work otherwise.
            if active_mod.type == 'LAPLACIANDEFORM':
                ml_modifier_layouts.LAPLACIANDEFORM(col, ob, active_mod)
            elif active_mod.type == 'MESH_DEFORM':
                ml_modifier_layouts.MESH_DEFORM(col, ob, active_mod)
            elif active_mod.type =='SURFACE_DEFORM':
                ml_modifier_layouts.SURFACE_DEFORM(col, ob, active_mod)
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


@persistent
def on_file_load(dummy):
    set_mesh_modifier_collection_items()


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

    bpy.app.handlers.load_post.append(on_file_load)

    set_mesh_modifier_collection_items()


def unregister():
    bpy.app.handlers.load_post.remove(on_file_load)

    del bpy.types.Object.ml_modifier_active_index