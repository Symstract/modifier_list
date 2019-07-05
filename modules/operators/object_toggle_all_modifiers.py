import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object


class OBJECT_OT_ml_toggle_all_modifiers(Operator):
    bl_idname = "object.ml_toggle_all_modifiers"
    bl_label = "Toggle Visibility Of All Modifiers"
    bl_description = "Toggle the visibility of all modifiers of the selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return get_ml_active_object() is not None

    def execute(self, context):
        ml_act_ob = get_ml_active_object()
        sel_obs = context.selected_objects

        if not ml_act_ob.modifiers:
            return {'CANCELLED'}

        obs = sel_obs.copy()

        if ml_act_ob not in obs:
            obs.append(ml_act_ob)

        ml_act_ob_all_mods_vis = [mod.show_viewport for mod in ml_act_ob.modifiers]
        show_mods = not any(ml_act_ob_all_mods_vis)

        for ob in obs:
            for mod in ob.modifiers:
                mod.show_viewport = show_mods

        return {'FINISHED'}