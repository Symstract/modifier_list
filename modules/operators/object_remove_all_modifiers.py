"""
This operator is inspired by Modifier Tools add-on, thanks for the authors
meta-androcto, saidenka and lijenstina.
https://wiki.blender.org/wiki/Extensions:2.6/Py/Scripts/3D_interaction/modifier_tools
"""

import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object, is_modifier_local


class OBJECT_OT_ml_remove_all_modifiers(Operator):
    bl_idname = "object.ml_remove_all_modifiers"
    bl_label = "Remove All Modifiers"
    bl_description = "Remove all modifiers from the selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obs = context.selected_objects

        if not obs:
            self.report({'INFO'}, "No selection")
            return {'CANCELLED'}

        obs_have_local_mods = False
        skipped_non_local_modifiers = False
        all_obs_linked_without_override = True

        for ob in obs:
            # Skip linked objects with no library override
            if ob.library:
                continue

            all_obs_linked_without_override = False

            # Store the name of the active modifier. In case it's
            # non-local, it can be then kept active.
            if ob.modifiers:
                init_active_mod = ob.modifiers[ob.ml_modifier_active_index]
                is_local = is_modifier_local(ob, init_active_mod)
                init_active_non_local_mod_name = None if is_local else init_active_mod.name

            for mod in ob.modifiers:
                if is_modifier_local(ob, mod):
                    ob.modifiers.remove(mod)
                    obs_have_local_mods = True
                else:
                    skipped_non_local_modifiers = True

            # Set active modifier index
            ob.ml_modifier_active_index = (ob.modifiers.find(init_active_non_local_mod_name)
                                           if init_active_non_local_mod_name else 0)

        if not obs_have_local_mods:
            if all_obs_linked_without_override or skipped_non_local_modifiers:
                self.report({'INFO'}, "No local modifiers to remove")
            else:
                self.report({'INFO'}, "No modifiers to remove")
            return {'CANCELLED'}

        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        if 'REMOVE' in prefs.batch_ops_reports:
            message = ("Removed all local modifiers" if skipped_non_local_modifiers
                       else "Removed all modifiers")
            self.report({'INFO'}, message)

        return {'FINISHED'}

    def invoke(self, context, event):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        if prefs.show_confirmation_popups:
            return context.window_manager.invoke_confirm(self, event)
        else:
            return self.execute(context)