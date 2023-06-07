import numpy as np

import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object, is_modifier_local


class OBJECT_OT_ml_modifier_move_down(Operator):
    bl_idname = "object.ml_modifier_move_down"
    bl_label = "Move Modifier"
    bl_description = ("Move modifier up/down in the stack.\n"
                      "\n"
                      "Hold Shift to move it to the top/bottom")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    move_to_end: BoolProperty(name="Move to End", options={'HIDDEN', 'SKIP_SAVE'})

    @classmethod
    def poll(cls, ontext):
        ob = get_ml_active_object()

        if not ob:
            return False

        active_mod_index = ob.ml_modifier_active_index
        mods = ob.modifiers

        if not ob.modifiers:
            return False

        if active_mod_index == len(mods) - 1:
            return False

        mod = mods[active_mod_index]

        return is_modifier_local(ob, mod)

    def execute(self, context):
        ml_active_ob = get_ml_active_object()

        # Make using operators possible when an object is pinned
        
        ### Draise - removed for Blender 4.0.0 compatibility

        #override = context.copy()
        #override['object'] = ml_active_ob

        active_mod_index = ml_active_ob.ml_modifier_active_index
        active_mod_name = ml_active_ob.modifiers[active_mod_index].name

        mods_max_index = len(ml_active_ob.modifiers) - 1

        if self.move_to_end:
            bpy.ops.object.modifier_move_to_index(modifier=active_mod_name,
                                                  index=mods_max_index)
            ml_active_ob.ml_modifier_active_index = mods_max_index
        else:
            with context.temp_override(id=ml_active_ob): ### Draise - added "with" for Blender 4.0.0 compatibility
                bpy.ops.object.modifier_move_down(modifier=active_mod_name)
                ml_active_ob.ml_modifier_active_index = np.clip(active_mod_index + 1, 0, mods_max_index)

        return {'FINISHED'}

    def invoke(self, context, event):
        if event.shift:
            self.move_to_end = True

        return self.execute(context)
