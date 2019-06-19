import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_gizmo_object, get_ml_active_object


is_initially_ob_pinned = False
initial_mode = None
initially_selected_ob = None


def scene_correct_state_ensure(dummy):
    """Handler for making sure the active object, object selection
    and object pinning are set correctly even if the user goes manually
    out of lattice edit mode instead of using the dedicated button.
    """
    ob = bpy.context.object
    if ob:
        if ob.mode == 'OBJECT':
            wm = bpy.context.window_manager
            if not is_initially_ob_pinned:
                wm.ml_pinned_object = None
            bpy.context.view_layer.objects.active = initially_selected_ob
            bpy.app.handlers.depsgraph_update_post.remove(scene_correct_state_ensure)


class OBJECT_OT_ml_lattice_toggle_editmode(Operator):
    bl_idname = "object.lattice_toggle_editmode"
    bl_label = "Toggle Lattice Edit Mode"
    bl_description = "Toggle lattice edit mode"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        ob = context.object
        wm = context.window_manager
        depsgraph_handlers = bpy.app.handlers.depsgraph_update_post

        global initial_mode
        global is_initially_ob_pinned
        global initially_selected_ob

        if ob.type == 'LATTICE':
            is_lattice_edit_mode_on = ob.mode == 'EDIT'
        else:
            is_lattice_edit_mode_on = False

        if not is_lattice_edit_mode_on:
            initial_mode = context.mode
            is_initially_ob_pinned = bool(wm.ml_pinned_object)
            initially_selected_ob = ob

            wm.ml_pinned_object = get_ml_active_object()
            gizmo_ob = get_gizmo_object()

            bpy.ops.object.mode_set(mode='OBJECT')

            context.view_layer.objects.active = gizmo_ob

            bpy.ops.object.mode_set(mode='EDIT')

            depsgraph_handlers.append(scene_correct_state_ensure)

        else:
            try:
                depsgraph_handlers.remove(scene_correct_state_ensure)
            except:
                pass

            bpy.ops.object.mode_set(mode='OBJECT')

            if is_initially_ob_pinned:
                context.view_layer.objects.active = initially_selected_ob

                if initial_mode == 'EDIT_MESH':
                    context.view_layer.objects.active = wm.ml_pinned_object
                    bpy.ops.object.mode_set(mode='EDIT')

            else:
                if initial_mode == 'OBJECT':
                    ob.select_set(False)
                    context.view_layer.objects.active = wm.ml_pinned_object
                    wm.ml_pinned_object = None
                else:
                    context.view_layer.objects.active = wm.ml_pinned_object
                    bpy.ops.object.mode_set(mode='EDIT')
                    wm.ml_pinned_object = None

        return {'FINISHED'}