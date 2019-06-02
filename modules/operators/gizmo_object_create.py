from bpy.props import *
from bpy.types import Operator

from ..utils import assign_gizmo_object_to_modifier


class OBJECT_OT_ml_create_gizmo_object(Operator):
    bl_idname = "object.ml_create_gizmo_object"
    bl_label = "Add Gizmo Object"
    bl_description = ("Add a gizmo object to the modifier.\n"
                      "\n"
                      "\u2022 Click to place it at the origin of the active object.\n"
                      "\u2022 Click + Hold shift to place it at the selected vertex")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier: StringProperty()

    def execute(self, context):
        assign_gizmo_object_to_modifier(self, context, self.modifier, self.place_at_vertex)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.place_at_vertex = True if event.shift else False

        return self.execute(context)