from bpy.types import Operator
from mathutils import Matrix

from ..utils import get_gizmo_object_from_modifier, get_ml_active_object


class OBJECT_OT_ml_gizmo_object_reset_transform(Operator):
    bl_idname = "object.ml_gizmo_object_reset_transform"
    bl_label = "Reset Transform For Gizmo"
    bl_description = "Reset transform for the gizmo object"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        ob = get_ml_active_object()
        active_mod_index = ob.ml_modifier_active_index
        active_mod = ob.modifiers[active_mod_index]
        gizmo_ob = get_gizmo_object_from_modifier(active_mod)
        gizmo_ob.matrix_world = Matrix.Identity(4)

        return {'FINISHED'}
