import bpy
from bpy.props import *
from bpy.types import Operator

from ..modifier_categories import ALL_MODIFIERS, HAVE_GIZMO_PROPERTY
from ..utils import get_ml_active_object, assign_gizmo_object_to_modifier


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
        mods_len = len(ob.modifiers) - 1
        ob.ml_modifier_active_index = mods_len

        # === Add a gizmo object ===
        mod = ob.modifiers[-1]

        # Search doesn't call invoke, so check if self.shift exists
        if hasattr(self, "shift"):
            if self.shift and ob.type == 'MESH':
                if mod.type in HAVE_GIZMO_PROPERTY or mod.type == 'UV_PROJECT':
                    placement = 'WORLD_ORIGIN' if self.alt else 'OBJECT'
                    assign_gizmo_object_to_modifier(self, context, mod.name, placement=placement)

        # === Move modifier into place ===
        # Search doesn't call invoke, so check if self.ctrl exists.
        # If not, can't support overriding insert_modifier_after_active
        # by holding control.

        # This doesn't work with library overrides because the context
        # of the layout can be wrong.
        # layout.context_pointer_set("modifier", active_modifier) is
        # used to set the modifier for the context of the layout and
        # modifier_move_up seems to use that modifier in it's poll,
        # instead of the one passed as an argument. And linked modifiers
        # can't be moved.
        if ob.override_library:
            return {'FINISHED'}

        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        if hasattr(self, "ctrl"):
            move = not self.ctrl if prefs.insert_modifier_after_active else self.ctrl
        else:
            move = prefs.insert_modifier_after_active

        if move:
            if bpy.app.version[1] >= 90:
                bpy.ops.object.modifier_move_to_index(modifier=mod.name, 
                                                      index=init_active_mod_index + 1)
            else:
                for _ in range(mods_len - 1 - init_active_mod_index):
                    bpy.ops.object.modifier_move_up(override, modifier=mod.name)

            if init_active_mod_index < mods_len - 1:
                ob.ml_modifier_active_index = init_active_mod_index + 1

        return {'FINISHED'}

    def invoke(self, context, event):
        self.ctrl = event.ctrl
        self.shift = event.shift
        self.alt = event.alt

        return self.execute(context)
