import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object, get_gizmo_object_from_modifier


class OBJECT_OT_ml_gizmo_object_parent_set(Operator):
    bl_idname = "object.ml_gizmo_object_parent_set"
    bl_label = "Parent Gizmo To Active Object"
    bl_description = ("Parent the gizmo object to the active object")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    unset: BoolProperty(name="Unset")

    def execute(self, context):
        ob = get_ml_active_object()
        active_mod_index = ob.ml_modifier_active_index
        active_mod = ob.modifiers[active_mod_index]
        gizmo_ob = get_gizmo_object_from_modifier(active_mod)

        if self.unset:
            parent_inverse = gizmo_ob.matrix_parent_inverse
            gizmo_ob.parent = None
            gizmo_ob.matrix_world @= parent_inverse
        else:
            gizmo_ob.parent = ob
            gizmo_ob.matrix_parent_inverse = ob.matrix_world.inverted()

        return {'FINISHED'}
