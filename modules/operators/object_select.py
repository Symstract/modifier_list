import bpy
from bpy.props import *
from bpy.types import Operator


class OBJECT_OT_ml_select(Operator):
    bl_idname = "object.ml_select"
    bl_label = "Select Object"
    bl_description = ("Select object.\n"
                      "\n"
                      "Hold shift to extend selection")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    object_name: StringProperty(options={'HIDDEN'})

    def execute(self, context):
        ob = bpy.data.objects[self.object_name]

        if not self.extend_selection:
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = ob

        ob.select_set(True)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.extend_selection = True if event.shift else False

        return self.execute(context)
