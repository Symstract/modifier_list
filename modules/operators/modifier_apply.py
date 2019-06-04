import numpy as np

import bpy
from bpy.props import *
from bpy.types import Operator

from ..modifier_categories import curve_deform_names_icons_types


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
        ob = context.object
        self.mod_type = ob.modifiers[self.modifier].type

        if context.mode in {'EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE', 'EDIT_TEXT', 'EDIT_LATTICE'}:
            bpy.ops.object.editmode_toggle()
            bpy.ops.ed.undo_push(message="Toggle Editmode")

            try:
                bpy.ops.object.modifier_apply(apply_as=self.apply_as, modifier=self.modifier)
                if ob.type in {'CURVE', 'SURFACE'}:
                    self.curve_modifier_apply_report()
            except RuntimeError as rte:
                message = str(rte).replace("Error: ", "")
                message = message[:-1]
                self.report(type={'ERROR'}, message=message)
                bpy.ops.object.editmode_toggle()
                return {'FINISHED'}

            bpy.ops.ed.undo_push(message="Apply Modifier")
            bpy.ops.object.editmode_toggle()
        else:
            try:
                bpy.ops.object.modifier_apply(apply_as=self.apply_as, modifier=self.modifier)
                if ob.type in {'CURVE', 'SURFACE'}:
                    self.curve_modifier_apply_report()
            except RuntimeError as rte:
                message = str(rte).replace("Error: ", "")
                message = message[:-1]
                self.report(type={'ERROR'}, message=message)
                return {'FINISHED'}

        # Set correct active_mod index in case the applied modifier is
        # not the first in modifier stack.
        current_active_mod_index = ob.ml_modifier_active_index
        new_active_mod_index = np.clip(current_active_mod_index - 1, 0, 99)
        ob.ml_modifier_active_index = new_active_mod_index

        if current_active_mod_index != 0:
            self.report({'INFO'}, "Applied modifier was not first, result may not be as expected")

        return {'FINISHED'}

    def curve_modifier_apply_report(self):
        curve_deform_mods = [mod[2] for mod in curve_deform_names_icons_types]
        if self.mod_type in curve_deform_mods:
            self.report({'INFO'}, "Applied modifier only changed CV points, "
                        "not tessellated/bevel vertices")