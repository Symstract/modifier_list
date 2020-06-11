import bpy
from bpy.props import *
from bpy.types import Operator


class OBJECT_OT_ml_toggle_visibility_on_view_layer(Operator):
    bl_idname = "object.ml_toggle_visibility_on_view_layer"
    bl_label = "Toggle Visibility"
    bl_description = "Show/hide the object on the active view layer"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    object_name: StringProperty(options={'HIDDEN'})

    def execute(self, context):
        ob = bpy.data.objects[self.object_name]
        hide = not ob.hide_get()
        ob.hide_set(hide)

        return {'FINISHED'}
