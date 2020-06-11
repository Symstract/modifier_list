"""
This operator is inspired by Modifier Tools add-on, thanks for the authors
meta-androcto, saidenka and lijenstina.
https://wiki.blender.org/wiki/Extensions:2.6/Py/Scripts/3D_interaction/modifier_tools
"""

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
            self.report({'INFO'}, "Active object has no modifiers")
            return {'CANCELLED'}

        obs = sel_obs.copy()

        if ml_act_ob not in obs:
            obs.append(ml_act_ob)

        ml_act_ob_all_mods_vis = [mod.show_viewport for mod in ml_act_ob.modifiers]
        show_mods = not any(ml_act_ob_all_mods_vis)
        skipped_linked_obs = False

        for ob in obs:
            # Skip linked objects if they don't have a library override
            if ob.library and not ob.override_library:
                skipped_linked_obs = True
                continue

            for mod in ob.modifiers:
                # Dont toggle the visibility of collision modifiers as that
                # can apparently cause problems in some scenes.
                if not mod.type == 'COLLISION':
                    mod.show_viewport = show_mods

        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        if 'TOGGLE_VISIBILITY' in prefs.batch_ops_reports:
            skipped_linked_obs_message = (" (skipped linked objects with no override)"
                                          if skipped_linked_obs else "")
            message = "Displaying all modifiers" if show_mods else "Hiding all modifiers"
            self.report({'INFO'}, message + skipped_linked_obs_message)

        return {'FINISHED'}
