import bpy
from bpy.props import *
from bpy.types import Operator

class UI_OT_ml_object_pin(Operator):
    bl_idname = "ui.ml_object_pin"
    bl_label = "Pin Object"
    bl_description = "Pin/unpin the object"
    bl_options = {'INTERNAL'}

    unpin: BoolProperty()

    def execute(self, context):
        ob = context.object
        scene = context.scene
        scene.ml_pinned_object = None if self.unpin else ob

        # Update the sidebar if called from the popup
        context.area.tag_redraw()

        return {'FINISHED'}