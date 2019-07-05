import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object


class OBJECT_OT_ml_remove_all_modifiers(Operator):
    bl_idname = "object.ml_remove_all_modifiers"
    bl_label = "Remove All Modifiers"
    bl_description = "Remove all modifiers from the selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return get_ml_active_object() is not None

    def execute(self, context):
        ml_act_ob = get_ml_active_object()
        sel_obs = context.selected_objects
        obs = sel_obs.copy()

        if ml_act_ob not in obs:
            obs.append(ml_act_ob)

        obs_have_mods = False

        for ob in obs:
            for mod in ob.modifiers:
                ob.modifiers.remove(mod)
                obs_have_mods = True

        if not obs_have_mods:
            self.report({'INFO'}, "No modifiers to remove")
            return {'CANCELLED'}

        self.report({'INFO'}, "Removed all modifiers")

        return {'FINISHED'}