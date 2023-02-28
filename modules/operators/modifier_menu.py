import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object, object_type_has_modifiers


class OBJECT_OT_ml_modifier_add_from_menu(Operator):
    bl_idname = "object.ml_modifier_add_from_menu"
    bl_label = "Add Modifier from Menu"
    bl_description = "Open the modifier menu to add a modifier to the active object"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        ob = get_ml_active_object()

        if not ob:
            return False

        if not object_type_has_modifiers(ob):
            return False

        return ob.library is None or ob.override_library is not None

    def execute(self, context):
        bpy.ops.wm.call_menu(name="OBJECT_MT_ml_add_modifier_menu")
        return {'CANCELLED'}
