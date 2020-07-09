import bpy
from bpy.props import *
from bpy.types import Operator


class UI_OT_ml_active_favourite_modifier_slot_set(Operator):
    bl_idname = "ui.ml_active_favourite_modifier_slot_set"
    bl_label = "Set Active Favourite Modifier Slot"
    bl_description = "Set the active favourite modifier slot"
    bl_options = {'INTERNAL'}

    index: IntProperty()

    def execute(self, context):
        context.window_manager.modifier_list.active_favourite_modifier_slot_index = self.index

        return {'FINISHED'}
