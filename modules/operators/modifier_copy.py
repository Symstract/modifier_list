import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object, is_modifier_local


class OBJECT_OT_ml_modifier_copy(Operator):
    bl_idname = "object.ml_modifier_copy"
    bl_label = "Copy Modifier"
    bl_description = "Duplicate modifier at the same position in the stack"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, ontext):
        ob = get_ml_active_object()

        if not ob:
            return False

        if ob.override_library:
            return True

        mod = ob.modifiers[ob.ml_modifier_active_index]
        return is_modifier_local(ob, mod)

    def execute(self, context):
        ob = get_ml_active_object()
        mod = ob.modifiers[ob.ml_modifier_active_index]

        # Make copying modifiers possible when an object is pinned
        
        ### Draise - removed for Blender 4.0.0 compatibility

        #override = context.copy()
        #override['object'] = ob

        with context.temp_override(id=ob): ### Draise - added "with" for Blender 4.0.0 compatibility
            bpy.ops.object.modifier_copy(modifier=mod.name)

        return {'FINISHED'}
