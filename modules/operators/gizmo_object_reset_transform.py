from bpy.types import Operator
from mathutils import Matrix

from ..utils import get_gizmo_object


class OBJECT_OT_ml_gizmo_object_reset_transform(Operator):
    bl_idname = "object.ml_gizmo_object_reset_transform"
    bl_label = "Reset Transform For Gizmo"
    bl_description = "Reset transform for the gizmo object"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        gizmo_ob = get_gizmo_object()
        gizmo_ob.matrix_world = Matrix.Identity(4)

        return {'FINISHED'}