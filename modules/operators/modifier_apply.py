import numpy as np

import bpy
from bpy.props import *
from bpy.types import Operator

from . import lattice_toggle_editmode, lattice_toggle_editmode_prop_editor
from ..modifier_categories import curve_deform_names_icons_types
from ..utils import (
    delete_gizmo_object,
    delete_ml_vertex_group,
    get_gizmo_object,
    get_ml_active_object,
    get_vertex_group
)


class OBJECT_OT_ml_modifier_apply_multi_user_data_dialog(Operator):
    bl_idname = "object.ml_modifier_apply_multi_user_data_dialog"
    bl_label = "Apply Modifier Dialog"
    bl_options = {'INTERNAL'}

    modifier: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    op_name: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=360)

    def draw(self, context):
        ml_active_ob = get_ml_active_object()

        layout = self.layout

        # Popups can't be closed manually, so just show a label after
        # the modifier has been applied.
        try:
            ml_active_ob.modifiers[self.modifier]
        except KeyError:
            layout.label(text="Done")
            return

        layout.label(text="Object's data is used by multiple objects. What would you like to do?")

        layout.separator()

        op = layout.operator(self.op_name, text="Apply To Active Object Only (Break Link)")
        op.modifier = self.modifier
        op.multi_user_data_apply_method = 'APPLY_TO_SINGLE'

        op = layout.operator(self.op_name, text="Apply To All Objects")
        op.modifier = self.modifier
        op.multi_user_data_apply_method = 'APPLY_TO_ALL'


class ApplyModifier:
    """Base operator for applying a modifier"""
    bl_idname = "object.ml_modifier_apply"
    bl_label = "Apply Modifier"
    bl_description = ("Apply modifier and remove from the stack.\n"
                      "\n"
                      "Hold shift to also delete its gizmo object (if it has one)")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    multi_user_data_apply_method_items = [
        ('NONE', "None", ""),
        ("APPLY_TO_SINGLE", "Apply To Single", ""),
        ("APPLY_TO_ALL", "Apply To All", "")
    ]
    multi_user_data_apply_method: EnumProperty(
        items=multi_user_data_apply_method_items,
        default='NONE',
        options={'HIDDEN', 'SKIP_SAVE'})

    apply_as: None

    @classmethod
    def poll(cls, context):
        ob = get_ml_active_object()
        data = ob.data
        mod = ob.modifiers[ob.ml_modifier_active_index]

        if not mod.is_property_overridable_library("name"):
            return False

        if ob.library:
            return False
        elif ob.override_library and (data.library or data.override_library):
            return False

        return True

    def execute(self, context):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences
        ml_active_ob = get_ml_active_object()

        # Get the active object in 3d View so Properties Editor's
        # context pinning won't mess things up.
        if context.area.type == 'PROPERTIES':
            context.area.type = 'VIEW_3D'
            ob = context.object
            context.area.type = 'PROPERTIES'
        else:
            ob = context.object

        self.mod_type = ml_active_ob.modifiers[self.modifier].type

        # Get the gizmo object and the vertex group, so they can be
        # deleted after applying the modifier
        gizmo_ob = get_gizmo_object()
        vert_group = get_vertex_group()

        if context.mode in {'EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE', 'EDIT_TEXT', 'EDIT_LATTICE'}:
            bpy.ops.object.editmode_toggle()
            bpy.ops.ed.undo_push(message="Toggle Editmode")

            # Make applying modifiers possible when the object's data is
            # used by other objects too.
            if self.multi_user_data_apply_method != 'NONE':
                self.assign_new_data_to_active_instance()

            # Make applying modifiers possible when an object is pinned
            override = context.copy()
            override['object'] = get_ml_active_object()

            try:
                bpy.ops.object.modifier_apply(override, apply_as=self.apply_as, modifier=self.modifier)
                if ml_active_ob.type in {'CURVE', 'SURFACE'}:
                    self.curve_modifier_apply_report()
            except RuntimeError as rte:
                message = str(rte).replace("Error: ", "")
                message = message[:-1]
                self.report(type={'ERROR'}, message=message)
                if self.multi_user_data_apply_method != 'NONE':
                    self.reassign_old_data_to_active_instance()
                bpy.ops.object.editmode_toggle()
                return {'FINISHED'}

            bpy.ops.ed.undo_push(message="Apply Modifier")

            if ob.type == 'LATTICE':
                # When using lattice_toggle_editmode(_prop_editor) operator, the mode
                # the user was in before that is stored inside that
                # module. That can also be utilised here.
                if context.area.type == 'PROPERTIES':
                    if lattice_toggle_editmode_prop_editor.init_mode == 'EDIT_MESH':
                        bpy.ops.object.editmode_toggle()
                elif lattice_toggle_editmode.init_mode == 'EDIT_MESH':
                    bpy.ops.object.editmode_toggle()
            else:
                bpy.ops.object.editmode_toggle()

        else:
            # Make applying modifiers possible when the object's data is
            # used by other objects too.
            if self.multi_user_data_apply_method != 'NONE':
                self.assign_new_data_to_active_instance()

            # Make applying modifiers possible when an object is pinned
            override = context.copy()
            override['object'] = get_ml_active_object()

            try:
                bpy.ops.object.modifier_apply(override, apply_as=self.apply_as, modifier=self.modifier)
                if ml_active_ob.type in {'CURVE', 'SURFACE'}:
                    self.curve_modifier_apply_report()
            except RuntimeError as rte:
                message = str(rte).replace("Error: ", "")
                message = message[:-1]
                self.report(type={'ERROR'}, message=message)
                if self.multi_user_data_apply_method != 'NONE':
                    self.reassign_old_data_to_active_instance()
                return {'FINISHED'}

        # Apply the modifier to all instances
        if self.multi_user_data_apply_method == 'APPLY_TO_ALL':
            self.assign_new_data_to_other_instances()

        # Set correct active_mod index in case the applied modifier is
        # not the first in modifier stack.
        current_active_mod_index = ml_active_ob.ml_modifier_active_index
        new_active_mod_index = np.clip(current_active_mod_index - 1, 0, 99)
        ml_active_ob.ml_modifier_active_index = new_active_mod_index

        if current_active_mod_index != 0:
            self.report({'INFO'}, "Applied modifier was not first, result may not be as expected")

        # Delete the gizmo object and the vertex group
        if self.shift or prefs.always_delete_gizmo:
            delete_gizmo_object(self, gizmo_ob)
            context.view_layer.objects.active = ml_active_ob
            if self.mod_type == 'LATTICE':
                delete_ml_vertex_group(ml_active_ob, vert_group)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.shift = event.shift
        prefs = bpy.context.preferences.addons["modifier_list"].preferences
        ml_active_ob = get_ml_active_object()

        if prefs.disallow_applying_hidden_modifiers:
            mod = ml_active_ob.modifiers[self.modifier]
            if not mod.show_viewport:
                self.report({'INFO'}, "Modifier is hidden in viewport, skipped apply")
                return {'CANCELLED'}

        if self.multi_user_data_apply_method == 'NONE' and ml_active_ob.data.users > 1:
            bpy.ops.object.ml_modifier_apply_multi_user_data_dialog('INVOKE_DEFAULT',
                                                                    modifier=self.modifier,
                                                                    op_name = self.bl_idname)
            return {'CANCELLED'}

        return self.execute(context)

    def get_correct_data_collection(self):
        ml_active_ob = get_ml_active_object()

        if ml_active_ob.type == 'MESH':
            return bpy.data.meshes
        elif ml_active_ob.type in {'CURVE', 'SURFACE', 'FONT'}:
            return bpy.data.curves
        elif ml_active_ob.type == 'LATTICE':
            return bpy.data.lattices

    def assign_new_data_to_active_instance(self):
        ml_active_ob = get_ml_active_object()
        old_data = ml_active_ob.data
        new_data = ml_active_ob.data.copy()
        self.old_data_name = old_data.name
        self.new_data_name = new_data.name
        ml_active_ob.data = new_data

    def assign_new_data_to_other_instances(self):
        obs = bpy.data.objects
        obs_with_same_data = [ob for ob in obs if ob.data and ob.data.name == self.old_data_name]
        data_collection = self.get_correct_data_collection()

        for ob in obs_with_same_data:
            ob.data = data_collection[self.new_data_name]

        data_collection.remove(data_collection[self.old_data_name])

    def reassign_old_data_to_active_instance(self):
        ml_active_ob = get_ml_active_object()
        data_collection = self.get_correct_data_collection()

        ml_active_ob.data = data_collection[self.old_data_name]

        data_collection.remove(data_collection[self.new_data_name])

    def curve_modifier_apply_report(self):
        curve_deform_mods = [mod[2] for mod in curve_deform_names_icons_types]
        if self.mod_type in curve_deform_mods:
            self.report({'INFO'}, "Applied modifier only changed CV points, "
                        "not tessellated/bevel vertices")


class OBJECT_OT_ml_modifier_apply(Operator, ApplyModifier):
    bl_idname = "object.ml_modifier_apply"
    bl_label = "Apply Modifier"
    bl_description = ("Apply modifier and remove from the stack.\n"
                      "\n"
                      "Hold shift to also delete its gizmo object (if it has one)")

    apply_as = 'DATA'


class OBJECT_OT_ml_modifier_apply_as_shapekey(Operator, ApplyModifier):
    bl_idname = "object.ml_modifier_apply_as_shapekey"
    bl_label = "Apply Modifier As Shape Key"
    bl_description =  ("Apply modifier as a shape key and remove from the stack.\n"
                      "\n"
                      "Hold shift to also delete its gizmo object (if it has one)")

    apply_as = 'SHAPE'