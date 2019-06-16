import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object

class UI_OT_ml_object_pin(Operator):
    bl_idname = "ui.ml_object_pin"
    bl_label = "Pin Object"
    bl_description = ("Pin the object")
    bl_options = {'INTERNAL'}

    unpin: BoolProperty()

    def execute(self, context):
        ob = get_ml_active_object()
        wm = context.window_manager
        wm.ml_pinned_object = None if self.unpin else ob

        return {'FINISHED'}