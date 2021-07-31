"""
This operator is inspired by Modifier Tools add-on, thanks for the authors
meta-androcto, saidenka and lijenstina.
https://wiki.blender.org/wiki/Extensions:2.6/Py/Scripts/3D_interaction/modifier_tools
"""

from bpy.types import Operator

from ..utils import get_ml_active_object


class OBJECT_OT_ml_toggle_all_modifiers(Operator):
    bl_idname = "object.ml_toggle_all_modifier_panels"
    bl_label = "Toggle All Modifier Panels"
    bl_description = "Open/close all modifier panels"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ml_act_ob = get_ml_active_object()
        return ml_act_ob is not None and ml_act_ob.modifiers

    def execute(self, context):
        mods = get_ml_active_object().modifiers
        expand = not any(mod.show_expanded for mod in mods)

        for mod in mods:
            mod.show_expanded = expand

        return {'FINISHED'}
