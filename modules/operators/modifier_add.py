import bpy
from bpy.props import *
from bpy.types import Operator

from ..modifier_categories import ALL_MODIFIERS_NAMES_ICONS_TYPES, HAVE_GIZMO_PROPERTY
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
        return ob is not None and (ob.library is None or ob.override_library is not None)

    def execute(self, context):
        ob = get_ml_active_object()

        self.add_modifier_pre_step(ob)

        # Store initial active_index
        init_active_mod_index = ob.ml_modifier_active_index

        # Make adding modifiers possible when an object is pinned
        
        ### Draise - Removed for compatibility with 4.0.0

        #override = context.copy()
        #override['object'] = ob

        ### Draise - Added the "with" for compatibility with 4.0.0
        try:
            with context.temp_override(id=ob): 
                bpy.ops.object.modifier_add(type=self.modifier_type)
        except TypeError:
            for mod in ALL_MODIFIERS_NAMES_ICONS_TYPES:
                if mod[2] == self.modifier_type:
                    modifier_name = mod[0]
                    break
            self.report({'ERROR'}, f"Cannot add {modifier_name} modifier for this object type")
            return {'FINISHED'}
        # Non-editable override objects don't support adding modifiers
        except RuntimeError as rte:
            self.report(type={'ERROR'}, message=str(rte).replace("Error: ", ""))
            return {'FINISHED'}

        self.set_modifier_default_settings()

        # Set correct active_mod index
        max_active_mod_index = len(ob.modifiers) - 1
        ob.ml_modifier_active_index = max_active_mod_index

        # === Add a gizmo object ===
        mod = ob.modifiers[-1]

        if self.shift and ob.type in {'CURVE', 'FONT', 'LATTICE', 'MESH', 'SURFACE'}:
            if mod.type in HAVE_GIZMO_PROPERTY or mod.type == 'UV_PROJECT':
                placement = 'WORLD_ORIGIN' if self.alt else 'OBJECT'
                assign_gizmo_object_to_modifier(self, context, mod.name, placement=placement)

        # === Move modifier into place ===
        # This doesn't work with library overrides because the context
        # of the layout can be wrong.
        # layout.context_pointer_set("modifier", active_modifier) is
        # used to set the modifier for the context of the layout and
        # modifier_move_to_index seems to use that modifier in it's poll,
        # instead of the one passed as an argument. And linked modifiers
        # can't be moved.
        if ob.override_library:
            return {'FINISHED'}

        prefs = bpy.context.preferences.addons["modifier_list"].preferences
        move = not self.ctrl if prefs.insert_modifier_after_active else self.ctrl

        if move:
            if init_active_mod_index != max_active_mod_index:
                bpy.ops.object.modifier_move_to_index(modifier=mod.name,
                                                      index=init_active_mod_index + 1)
            if init_active_mod_index < max_active_mod_index - 1:
                ob.ml_modifier_active_index = init_active_mod_index + 1

        return {'FINISHED'}

    def invoke(self, context, event):
        self.ctrl = event.ctrl
        self.shift = event.shift
        self.alt = event.alt

        return self.execute(context)

    def add_modifier_pre_step(self, object):
        if self.modifier_type in {'NORMAL_EDIT', 'WEIGHTED_NORMAL'}:
            object.data.use_auto_smooth = True

    def set_modifier_default_settings(self):
        mod = get_ml_active_object().modifiers[-1]
        mod_type = mod.type
        prefs = bpy.context.preferences.addons["modifier_list"].preferences
        defaults_group = getattr(prefs.modifier_defaults, mod.type)
        defaults = [(attr, getattr(defaults_group, attr))
                    for attr in defaults_group.__annotations__]

        for setting, value in defaults:
            # Some setting are synched, so the other one would override
            # the first one. So, only the other should be set, according
            # to the setting that determines which one is used.

            if mod_type == 'BEVEL':
                offset_type = defaults_group.offset_type

                if setting == "width" and offset_type == 'PERCENT':
                    continue

                if setting == "width_pct" and offset_type != 'PERCENT':
                    continue

            elif mod_type == 'SIMPLE_DEFORM':
                deform_method = defaults_group.deform_method

                if setting == "angle" and deform_method not in {'TWIST', 'BEND'}:
                    continue

                if setting == "factor" and deform_method not in {'TAPER', 'STRETCH'}:
                    continue

            setattr(mod, setting, value)
