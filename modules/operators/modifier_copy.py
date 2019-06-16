import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object


class OBJECT_OT_ml_modifier_copy(Operator):
    bl_idname = "object.ml_modifier_copy"
    bl_label = "Copy Modifier"
    bl_description = "Duplicate modifier at the same position in the stack"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier: StringProperty()

    def execute(self, context):
        ob = get_ml_active_object()

        # Make copying modifiers possible when an object is pinned
        override = context.copy()
        override['object'] = ob

        bpy.ops.object.modifier_copy(override, modifier=self.modifier)

        # Set correct active_mod index
        active_index = ob.ml_modifier_active_index
        ob.ml_modifier_active_index = active_index + 1

        return {'FINISHED'}