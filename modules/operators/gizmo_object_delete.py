import bpy
from bpy.types import Operator

from ..utils import get_gizmo_object_from_modifier, get_ml_active_object, delete_gizmo_object


class OBJECT_OT_ml_gizmo_object_delete(Operator):
    bl_idname = "object.ml_gizmo_object_delete"
    bl_label = "Delete Gizmo"
    bl_description = ("Delete the gizmo object")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        ob = get_ml_active_object()     
        active_mod_index = ob.ml_modifier_active_index
        active_mod = ob.modifiers[active_mod_index]
        gizmo_ob = get_gizmo_object_from_modifier(active_mod)
        delete_gizmo_object(self, gizmo_ob)

        return {'FINISHED'}
