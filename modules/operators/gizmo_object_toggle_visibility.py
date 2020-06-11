from bpy.types import Operator

from ..modifier_categories import have_gizmo_property
from ..utils import get_gizmo_object


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
        gizmo_ob = get_gizmo_object()

        gizmo_ob.hide_viewport = not gizmo_ob.hide_viewport

        return {'FINISHED'}
