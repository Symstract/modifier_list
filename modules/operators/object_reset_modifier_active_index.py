from bpy.types import Operator

from ..utils import get_ml_active_object


class OBJECT_OT_ml_reset_modifier_active_index(Operator):
    bl_idname = "object.ml_reset_modifier_active_index"
    bl_label = "Reset Active Modifier Index"
    bl_description = "Reset the active modifier index"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        get_ml_active_object().ml_modifier_active_index = 0

        return {'FINISHED'}