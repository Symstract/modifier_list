from bpy.props import *
from bpy.types import Operator

from ..utils import assign_gizmo_object_to_modifier


class OBJECT_OT_ml_gizmo_object_add(Operator):
    bl_idname = "object.ml_gizmo_object_add"
    bl_label = "Add Gizmo"
    bl_description = ("Add a gizmo object to the modifier.\n"
                      "\n"
                      "Placement:\n"
                      "Shift: 3D Cursor.\n"
                      "Alt: world origin.\n"
                      "If in Edit Mode and there is a selection: the average location of "
                      "the selected elements.\n"
                      "Else: active object's origin")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier: StringProperty()

    def execute(self, context):
        if self.shift:
            placement = 'CURSOR'
        elif self.alt:
            placement = 'WORLD_ORIGIN'
        else:
            placement = 'OBJECT'

        assign_gizmo_object_to_modifier(self, context, self.modifier, placement=placement)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.shift = event.shift
        self.alt = event.alt

        return self.execute(context)
