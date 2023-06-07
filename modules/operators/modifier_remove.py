import numpy as np

import bpy
from bpy.props import *
from bpy.types import Operator

from . import lattice_toggle_editmode, lattice_toggle_editmode_prop_editor
from ..utils import (
    delete_gizmo_object,
    delete_ml_vertex_group,
    get_gizmo_object_from_modifier,
    get_ml_active_object,
    is_modifier_local
)


class OBJECT_OT_ml_modifier_remove(Operator):
    bl_idname = "object.ml_modifier_remove"
    bl_label = "Remove Modifier"
    bl_description = ("Remove modifier from the active object.\n"
                     "\n"
                     "Hold shift to also delete its gizmo object (if it has one)")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, ontext):
        ob = get_ml_active_object()

        if not ob:
            return False

        if not ob.modifiers:
            return False

        mod = ob.modifiers[ob.ml_modifier_active_index]
        return is_modifier_local(ob, mod)

    def execute(self, context):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        ml_active_ob = get_ml_active_object()

        # Make using operators possible when an object is pinned
        
        ### Draise - removed for Blender 4.0.0 compatibility

        #override = context.copy()
        #override['object'] = ml_active_ob

        active_mod_index = ml_active_ob.ml_modifier_active_index
        active_mod = ml_active_ob.modifiers[active_mod_index]

        if self.shift or prefs.always_delete_gizmo:
            self.remove_gizmo_and_vertex_group(context, ml_active_ob, active_mod)

        ### Draise - added "with" for Blender 4.0.0 compatibility
        with context.temp_override(id=ml_active_ob):
            bpy.ops.object.modifier_remove(modifier=active_mod.name)
        ml_active_ob.ml_modifier_active_index = np.clip(active_mod_index - 1, 0, 999)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.shift = event.shift

        return self.execute(context)

    def remove_gizmo_and_vertex_group(self, context, object, modifier):
        # When using lattice_toggle_editmode(_prop_editor)
        # operator, the mode the user was in before that is
        # stored inside that module. That can also be
        # utilised here, so we can return into the correct
        # mode after deleting a lattice in lattice edit
        # mode.
        switch_into_editmode = False

        if context.active_object and context.active_object.type == 'LATTICE':
            if context.area.type == 'PROPERTIES':
                if lattice_toggle_editmode_prop_editor.init_mode == 'EDIT_MESH':
                    switch_into_editmode = True
            elif lattice_toggle_editmode.init_mode == 'EDIT_MESH':
                switch_into_editmode = True

        gizmo_ob = get_gizmo_object_from_modifier(modifier)
        delete_gizmo_object(self, gizmo_ob)

        if modifier.type == 'LATTICE':
            context.view_layer.objects.active = object
            if hasattr(modifier, "vertex_group"):
                delete_ml_vertex_group(object, modifier.vertex_group)
            if switch_into_editmode:
                bpy.ops.object.editmode_toggle()
