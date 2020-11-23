import bpy
from bpy.props import *
from bpy.types import Operator


class Collection_OT_ml_smooth_shading_set(Operator):
    bl_idname = "collection.ml_objects_smooth_shading_set"
    bl_label = "Set Smooth Shading For Objects In Collection"
    bl_description = "Set smooth shading for the objects in a collection"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    collection_name: StringProperty(options={'HIDDEN'})
    shade_smooth: BoolProperty(options={'HIDDEN'})

    def execute(self, context):
        collection = bpy.data.collections[self.collection_name]

        for ob in collection.all_objects:
            if ob.type == 'MESH':
                for p in ob.data.polygons:
                    p.use_smooth = self.shade_smooth

        return {'FINISHED'}
