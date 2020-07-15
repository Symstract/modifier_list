import numpy as np

import bpy
from bpy.props import *
from bpy.types import Operator

from . import lattice_toggle_editmode, lattice_toggle_editmode_prop_editor
from ..modifier_categories import CURVE_DEFORM_NAMES_ICONS_TYPES
from ..multiuser_data_modifier_apply_utils import LinkedObjectDataChanger
from ..utils import (
    delete_gizmo_object,
    delete_ml_vertex_group,
    get_gizmo_object_from_modifier,
    get_ml_active_object,
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
    keep_modifier_when_applying_as_shapekey = False

    @classmethod
    def poll(cls, context):
        ob = get_ml_active_object()
        data = ob.data
        mod = ob.modifiers[ob.ml_modifier_active_index]

        if ob.library:
            return False
        elif ob.override_library and (data.library or data.override_library):
            return False
        elif ob.override_library and not (data.library or data.override_library):
            if not mod.is_property_overridable_library("name"):
                return False

        return True

    def execute(self, context):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences
        ob = context.active_object
        ml_active_ob = get_ml_active_object()
        mod = ml_active_ob.modifiers[self.modifier]

        # Get the gizmo object and the vertex group, so they can be
        # deleted after applying the modifier. Also get the modifier
        # type for that.
        gizmo_ob = get_gizmo_object_from_modifier(mod)
        vert_group = mod.vertex_group if hasattr(mod, "vertex_group") else None
        mod_type = mod.type

        is_editmode = (context.mode in
                       {'EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE', 'EDIT_TEXT', 'EDIT_LATTICE'})

        if is_editmode:
            bpy.ops.object.editmode_toggle()
            # Add an undo step to avoid problems with undo
            bpy.ops.ed.undo_push(message="Toggle Editmode")

        # Make applying modifiers possible when the object's data is
        # used by other objects too.
        if self.multi_user_data_apply_method != 'NONE':
            self.linked_object_data_changer = LinkedObjectDataChanger(ml_active_ob)
            self.linked_object_data_changer.make_active_instance_data_unique()

        success = self.apply_modifier(context, ml_active_ob, is_editmode)
        
        if not success:
            return {'CANCELLED'}

        if is_editmode:
            # Add an undo step to avoid problems with undo
            bpy.ops.ed.undo_push(message="Apply Modifier")
            if ob.type == 'LATTICE':
                self.ensure_correct_mode_after_applying_lattice(context)
            else:
                bpy.ops.object.editmode_toggle()

        # Apply the modifier to all instances
        if self.multi_user_data_apply_method == 'APPLY_TO_ALL':
            self.linked_object_data_changer.assign_new_data_to_other_instances()

        self.ensure_correct_modifier_active_index(ml_active_ob)

        # Delete the gizmo object and the vertex group
        if self.shift or prefs.always_delete_gizmo:
            if not self.keep_modifier_when_applying_as_shapekey:
                self.delete_gizmo_and_vertex_group(context, ml_active_ob, mod_type, gizmo_ob,
                                                   vert_group)

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
            if not self.keep_modifier_when_applying_as_shapekey:
                bpy.ops.object.ml_modifier_apply_multi_user_data_dialog('INVOKE_DEFAULT',
                                                                        modifier=self.modifier,
                                                                        op_name=self.bl_idname)
            return {'CANCELLED'}

        return self.execute(context)

    def apply_modifier(self, context, ml_active_object, is_init_mode_editmode):
        # Make applying modifiers possible when an object is pinned
        override = context.copy()
        override['object'] = ml_active_object
        mod_type = ml_active_object.modifiers[self.modifier].type

        try:
            # Applying a modifier as a shape key is done with a separate operator since 2.90
            if float(bpy.app.version_string[0:4]) < 2.90:
                bpy.ops.object.modifier_apply(override, apply_as=self.apply_as,
                                              modifier=self.modifier)
            else:
                if self.apply_as == 'DATA':
                    bpy.ops.object.modifier_apply(override, modifier=self.modifier)
                elif self.apply_as == 'SHAPE':
                        bpy.ops.object.modifier_apply_as_shapekey(
                            override, modifier=self.modifier,
                            keep_modifier=self.keep_modifier_when_applying_as_shapekey)
            
            if ml_active_object.type in {'CURVE', 'SURFACE'}:
                self.curve_modifier_apply_report(mod_type)
            
            return True
        
        except RuntimeError as rte:
            message = str(rte).replace("Error: ", "")
            message = message[:-1]
            self.report(type={'ERROR'}, message=message)
            
            if self.multi_user_data_apply_method != 'NONE':
                self.linked_object_data_changer.reassign_old_data_to_active_instance()
            
            if is_init_mode_editmode:
                bpy.ops.object.editmode_toggle()
            
            return False

    def curve_modifier_apply_report(self, modifier_type):
        curve_deform_mods = [mod[2] for mod in CURVE_DEFORM_NAMES_ICONS_TYPES]
        if modifier_type in curve_deform_mods:
            self.report({'INFO'}, "Applied modifier only changed CV points, "
                        "not tessellated/bevel vertices")
                        
    def ensure_correct_mode_after_applying_lattice(self, context):
        # When using lattice_toggle_editmode(_prop_editor)
        # operator, the mode the user was in before that is
        # stored inside that module. That can also be utilised
        # here.
        if context.area.type == 'PROPERTIES':
            if lattice_toggle_editmode_prop_editor.init_mode == 'EDIT_MESH':
                bpy.ops.object.editmode_toggle()
        elif lattice_toggle_editmode.init_mode == 'EDIT_MESH':
            bpy.ops.object.editmode_toggle()

    def ensure_correct_modifier_active_index(self, ml_active_object):
        # Set correct modifier_active_index in case the applied modifier
        # is not the first in modifier stack.
        current_active_mod_index = ml_active_object.ml_modifier_active_index
        new_active_mod_index = np.clip(current_active_mod_index - 1, 0, 99)
        ml_active_object.ml_modifier_active_index = new_active_mod_index

        if current_active_mod_index != 0:
            self.report({'INFO'}, "Applied modifier was not first, result may not be as expected")

    def delete_gizmo_and_vertex_group(self, context, ml_active_object, modifier_type, gizmo_object,
                                      vertex_group):
        delete_gizmo_object(self, gizmo_object)
        context.view_layer.objects.active = ml_active_object
        if modifier_type == 'LATTICE':
            delete_ml_vertex_group(ml_active_object, vertex_group)


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
    bl_description = ("Apply modifier as a shape key and remove from the stack.\n"
                      "\n"
                      "Hold shift to also delete its gizmo object (if it has one)")

    apply_as = 'SHAPE'


class OBJECT_OT_ml_modifier_save_as_shapekey(Operator, ApplyModifier):
    bl_idname = "object.ml_modifier_save_as_shapekey"
    bl_label = "Save Modifier As Shape Key"
    bl_description = "Apply modifier as a new shape key and keep it in the stack"

    apply_as = 'SHAPE'
    keep_modifier_when_applying_as_shapekey = True
