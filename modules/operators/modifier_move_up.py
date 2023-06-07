import numpy as np

import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object, is_modifier_local


class OBJECT_OT_ml_modifier_move_up(Operator):
    bl_idname = "object.ml_modifier_move_up"
    bl_label = "Move Modifier"
    bl_description = ("Move modifier up/down in the stack.\n"
                      "\n"
                      "Hold Shift to move it to the top/bottom")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    move_to_start: BoolProperty(name="Move to Start", options={'HIDDEN', 'SKIP_SAVE'})

    @classmethod
    def poll(cls, ontext):
        ob = get_ml_active_object()

        if not ob:
            return False

        active_mod_index = ob.ml_modifier_active_index
        mods = ob.modifiers

        if not ob.modifiers:
            return False

        if active_mod_index == 0:
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

        if self.move_to_start:
            bpy.ops.object.modifier_move_to_index(modifier=active_mod_name, index=0)
            ml_active_ob.ml_modifier_active_index = 0
        else:
            with context.temp_override(id=ml_active_ob): ### Draise - added "with" for Blender 4.0.0 compatibility 
                bpy.ops.object.modifier_move_up(modifier=active_mod_name)
                ml_active_ob.ml_modifier_active_index = np.clip(active_mod_index - 1, 0, 999)

        return {'FINISHED'}

    def invoke(self, context, event):
        if event.shift:
            self.move_to_start = True

        return self.execute(context)
