import bpy
from bpy.props import *
from bpy.types import Operator

from ..modifier_categories import all_modifier_names_icons_types

class OBJECT_OT_ml_modifier_add(Operator):
    bl_idname = "object.ml_modifier_add"
    bl_label = "Add Modifier"
    bl_description = "Add a procedural operation/effect to the active object"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier_type: StringProperty()

    def execute(self, context):
        try:
            bpy.ops.object.modifier_add(type=self.modifier_type)
        except TypeError:
            for mod in all_modifier_names_icons_types():
                if mod[2] == self.modifier_type:
                    modifier_name = mod[0]
                    break
            self.report({'ERROR'}, f"Cannot add {modifier_name} modifier for this object type")

        ob = context.object

        # Enable auto smooth if modifier is weighted normal
        if ob.type == 'MESH':
            if self.modifier_type == 'WEIGHTED_NORMAL':
                ob.data.use_auto_smooth = True

        # Set correct active_mod index
        mods = ob.modifiers
        mods_len = len(mods) - 1
        ob.ml_modifier_active_index = mods_len

        return {'FINISHED'}