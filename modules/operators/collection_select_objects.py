import bpy
from bpy.props import *
from bpy.types import Operator


class COLLECTION_OT_ml_select_objects(Operator):
    bl_idname = "collection.ml_select_objects"
    bl_label = "Select Objects In Collection"
    bl_description = ("Select the objects in a collection.\n"
                      "\n"
                      "Hold shift to extend selection")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    collection_name: StringProperty(options={'HIDDEN'})

    def execute(self, context):
        if not self.extend_selection:
            bpy.ops.object.select_all(action='DESELECT')

        collection = bpy.data.collections[self.collection_name]

        for ob in collection.all_objects:
            ob.select_set(True)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.extend_selection = True if event.shift else False

        return self.execute(context)
