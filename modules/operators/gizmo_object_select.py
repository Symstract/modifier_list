import bpy
from bpy.types import Operator

from ..utils import get_gizmo_object


class OBJECT_OT_ml_gizmo_object_select(Operator):
    bl_idname = "object.ml_gizmo_object_select"
    bl_label = "Select Gizmo"
    bl_description = ("Select the gizmo object.\n"
                      "\n"
                      "Hold shift to extend selection")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        gizmo_ob = get_gizmo_object()

        if not self.extend_selection:
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = gizmo_ob

        gizmo_ob.select_set(True)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.extend_selection = True if event.shift else False

        return self.execute(context)