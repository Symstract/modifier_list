import bpy
from bpy.props import *
from bpy.types import Operator


class OBJECT_OT_ml_smooth_shading_set(Operator):
    bl_idname = "object.ml_smooth_shading_set"
    bl_label = "Set Smooth Shading"
    bl_description = "Set smooth shading"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    object_name: StringProperty(options={'HIDDEN'})
    shade_smooth: BoolProperty(options={'HIDDEN'})

    def execute(self, context):
        ob = bpy.data.objects[self.object_name]

        for p in ob.data.polygons:
            p.use_smooth = self.shade_smooth

        return {'FINISHED'}
