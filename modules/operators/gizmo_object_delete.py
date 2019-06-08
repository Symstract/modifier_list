import bpy
from bpy.types import Operator

from ..utils import get_gizmo_object, delete_gizmo_object


class OBJECT_OT_ml_gizmo_object_delete(Operator):
    bl_idname = "object.ml_gizmo_object_delete"
    bl_label = "Delete Gizmo"
    bl_description = ("Delete the gizmo object")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        delete_gizmo_object(self, context)

        return {'FINISHED'}