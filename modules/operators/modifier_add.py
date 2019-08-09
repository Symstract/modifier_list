import bpy
from bpy.props import *
from bpy.types import Operator

from ..modifier_categories import all_modifier_names_icons_types, have_gizmo_property
from ..utils import get_ml_active_object ,assign_gizmo_object_to_modifier


class OBJECT_OT_ml_modifier_add(Operator):
    bl_idname = "object.ml_modifier_add"
    bl_label = "Add Modifier"
    bl_description = ("Add a procedural operation/effect to the active object\n"
                     "\n"
                     "Hold shift to add the modifier with a gizmo object (for certain modifiers).\n"
                     "When a single vertex is selected, the gizmo is placed at the vertex location.\n"
                     "NOTE: This is only for meshes")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    modifier_type: StringProperty()

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
            for mod in all_modifier_names_icons_types():
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

        # Search doesn't call invoke, so check if self.add_gizmo exists
        if hasattr(self, "add_gizmo"):
            if self.add_gizmo and ob.type == 'MESH':
                if mod.type in have_gizmo_property or mod.type == 'UV_PROJECT':
                    assign_gizmo_object_to_modifier(self, context, mod.name)

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
                bpy.ops.object.ml_modifier_move_up()

        return {'FINISHED'}

    def invoke(self, context, event):
        self.add_gizmo = True if event.shift else False
        self.ctrl = True if event.ctrl else False

        return self.execute(context)