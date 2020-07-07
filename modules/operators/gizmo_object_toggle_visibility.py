from bpy.types import Operator

from ..utils import get_gizmo_object_from_modifier, get_ml_active_object


class OBJECT_OT_ml_gizmo_object_toggle_visibility(Operator):
    """The purpose of this operator is to get the opposite behaviour
    for the UI button to what the behaviour would be using the
    hide_viewport property.
    """
    bl_idname = "object.ml_gizmo_object_toggle_visibility"
    bl_label = "Toggle Gizmo Object Visibility"
    bl_description = "Toggle gizmo object visibility"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        ob = get_ml_active_object()
        active_mod_index = ob.ml_modifier_active_index
        active_mod = ob.modifiers[active_mod_index]
        gizmo_ob = get_gizmo_object_from_modifier(active_mod)
        gizmo_ob.hide_viewport = not gizmo_ob.hide_viewport

        return {'FINISHED'}
