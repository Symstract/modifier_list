import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object ,get_gizmo_object


class OBJECT_OT_ml_gizmo_object_child_set(Operator):
    bl_idname = "object.ml_gizmo_object_child_set"
    bl_label = "Parent Active Object To Gizmo"
    bl_description = ("Parent the active object to the gizmo object")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    unset: BoolProperty(name="Unset")

    def execute(self, context):
        ob = get_ml_active_object()
        gizmo_ob = get_gizmo_object()

        if self.unset:
            parent_inverse = ob.matrix_parent_inverse
            ob.parent = None
            ob.matrix_world @= parent_inverse
        else:
            ob.parent = gizmo_ob
            ob.matrix_parent_inverse = gizmo_ob.matrix_world.inverted()

        return {'FINISHED'}