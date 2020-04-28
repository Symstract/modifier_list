import bpy
from bpy.props import *
from bpy.types import Operator

from ..modifier_categories import ALL_MODIFIERS, have_gizmo_property
from ..utils import get_ml_active_object ,assign_gizmo_object_to_modifier


class OBJECT_OT_ml_modifier_add(Operator):
    bl_idname = "object.ml_modifier_add"
    bl_label = "Add Modifier"
    bl_description = ("Hold shift to add the modifier with a gizmo object (for certain modifiers).\n"
                      "\n"
                      "Placement:\n"
                      "Alt: world origin.\n"
                      "If in Edit Mode and there is a selection: the average location of "
                      "the selected elements.\n"
                      "Else: active object's origin")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier_type: StringProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        ob = get_ml_active_object()
        return ob.library is None or ob.override_library is not None

    def execute(self, context):
        ob = get_ml_active_object()

        # Store initial active_index
        init_active_mod_index = ob.ml_modifier_active_index

        # Make adding modifiers possible when an object is pinned
        override = context.copy()
        override['object'] = ob

        try:
            bpy.ops.object.modifier_add(override, type=self.modifier_type)
        except TypeError:
            for mod in ALL_MODIFIERS:
                if mod[2] == self.modifier_type:
                    modifier_name = mod[0]
                    break
            self.report({'ERROR'}, f"Cannot add {modifier_name} modifier for this object type")
            return {'FINISHED'}

        # Enable auto smooth if modifier is weighted normal
        if self.modifier_type == 'WEIGHTED_NORMAL':
            ob.data.use_auto_smooth = True

        # Set correct active_mod index
        mods = ob.modifiers
        mods_len = len(mods) - 1
        ob.ml_modifier_active_index = mods_len

        # === Add a gizmo object ===
        mod = ob.modifiers[-1]

        # Search doesn't call invoke, so check if self.shift exists
        if hasattr(self, "shift"):
            if self.shift and ob.type == 'MESH':
                if mod.type in have_gizmo_property or mod.type == 'UV_PROJECT':
                    placement = 'WORLD_ORIGIN' if self.alt else 'OBJECT'
                    assign_gizmo_object_to_modifier(self, context, mod.name, placement=placement)

        # === Move modifier into place ===
        # Search doesn't call invoke, so check if self.ctrl exists.
        # If not, can't support overriding insert_modifier_after_active
        # by holding control.
        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        if hasattr(self, "ctrl"):
            move = not self.ctrl if prefs.insert_modifier_after_active else self.ctrl
        else:
            move = prefs.insert_modifier_after_active

        if move:
            times_to_move = mods_len - 1 - init_active_mod_index

            for _ in range (times_to_move):
                bpy.ops.object.modifier_move_up(override, modifier=mod.name)

            if times_to_move > 0:
                ob.ml_modifier_active_index = init_active_mod_index + 1

        return {'FINISHED'}

    def invoke(self, context, event):
        self.ctrl = event.ctrl
        self.shift = event.shift
        self.alt = event.alt

        return self.execute(context)