import bpy
from bpy.props import *
from bpy.types import Operator


class COLLECTION_OT_ml_objects_display_type_set(Operator):
    bl_idname = "collection.objects_display_type_set"
    bl_label = "Set Display Type For Objects In Collection"
    bl_description = "Set display type for the objects in a collection"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    collection_name: StringProperty(options={'HIDDEN'})
    display_type: StringProperty(options={'HIDDEN'})

    def execute(self, context):
        collection = bpy.data.collections[self.collection_name]

        for ob in collection.all_objects:
            ob.display_type = self.display_type

        return {'FINISHED'}
