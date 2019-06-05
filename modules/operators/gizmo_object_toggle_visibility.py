from bpy.props import *
from bpy.types import Operator

from ..modifier_categories import have_gizmo_property


class OBJECT_OT_ml_gizmo_object_toggle_visibility(Operator):
    """The purpose of this operator is to get the opposite behaviour
    for the UI button to what the behaviour would be using the
    hide_viewport property.
    """
    bl_idname = "object.ml_gizmo_object_toggle_visibility"
    bl_label = "Toggle Gizmo Object Visibility"
    bl_description = "Toggle Gizmo Object Visibility"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier: StringProperty()

    def execute(self, context):
        ob = context.object
        active_mod_index = ob.ml_modifier_active_index
        active_mod = ob.modifiers[active_mod_index]

        gizmo_ob_prop = have_gizmo_property[active_mod.type]
        gizmo_ob = getattr(active_mod, gizmo_ob_prop)

        gizmo_ob.hide_viewport = not gizmo_ob.hide_viewport

        return {'FINISHED'}