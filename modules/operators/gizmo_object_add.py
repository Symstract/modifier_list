from bpy.props import *
from bpy.types import Operator

from ..utils import assign_gizmo_object_to_modifier


class OBJECT_OT_ml_gizmo_object_add(Operator):
    bl_idname = "object.ml_gizmo_object_add"
    bl_label = "Add Gizmo"
    bl_description = ("Add a gizmo object to the modifier.\n"
                      "\n"
                      "• When a single vertex is selected, the gizmo is placed at the vertex location.\n"
                      "• When holding shift, the gizmo is placed at the 3D Cursor")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier: StringProperty()

    def execute(self, context):
        assign_gizmo_object_to_modifier(self, context, self.modifier, place_at_cursor=self.shift)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.shift = True if event.shift else False

        return self.execute(context)