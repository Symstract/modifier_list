import numpy as np

import bpy
from bpy.props import *
from bpy.types import Operator

from ..modifier_categories import curve_deform_names_icons_types
from ..utils import (
    delete_gizmo_object,
    delete_ml_vertex_group,
    get_gizmo_object,
    get_vertex_group
)


class OBJECT_OT_ml_modifier_apply(Operator):
    bl_idname = "object.ml_modifier_apply"
    bl_label = "Apply Modifier"
    bl_description = ("Apply modifier and remove from the stack.\n"
                      "\n"
                      "Hold shift to also delete its gizmo object (if it has one)")
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

        # Get the gizmo object and the vertex group, so they can be
        # deleted after applying the modifier
        gizmo_ob = get_gizmo_object(context)
        vert_group = get_vertex_group(context)

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

        # Delete the gizmo object and the vertex group
        if self.shift:
            delete_gizmo_object(self, context, gizmo_ob)
            if self.mod_type == 'LATTICE':
                delete_ml_vertex_group(context, vert_group)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.shift = True if event.shift else False

        return self.execute(context)

    def curve_modifier_apply_report(self):
        curve_deform_mods = [mod[2] for mod in curve_deform_names_icons_types]
        if self.mod_type in curve_deform_mods:
            self.report({'INFO'}, "Applied modifier only changed CV points, "
                        "not tessellated/bevel vertices")