import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_gizmo_object_from_modifier, get_ml_active_object


is_init_ob_pinned = False
init_mode = None
init_act_ob_name = None


def scene_correct_state_after_editmode_toggle_ensure(scene):
    """Handler for making sure the active object, object selection
    and object pinning are set correctly even if the user goes manually
    out of lattice edit mode instead of using the dedicated
    button.
    """
    ob = bpy.context.object
    depsgraph_handlers = bpy.app.handlers.depsgraph_update_post
    undo_handlers = bpy.app.handlers.undo_post
    init_act_ob = bpy.data.objects[init_act_ob_name]

    if ob:
        if ob.mode == 'OBJECT':
            if not is_init_ob_pinned:
                scene.ml_pinned_object = None
            bpy.context.view_layer.objects.active = init_act_ob
            depsgraph_handlers.remove(scene_correct_state_after_editmode_toggle_ensure)

            try:
                undo_handlers.remove(scene_correct_state_after_undo_ensure)
            except ValueError:
                pass


def scene_correct_state_after_undo_ensure(scene):
    """Handler for making sure the active object, object selection
    and object pinning are set correctly even if the user goes out of
    lattice edit mode by using undo instead of using the dedicated
    button.
    """
    ob = bpy.context.object
    depsgraph_handlers = bpy.app.handlers.depsgraph_update_post
    undo_handlers = bpy.app.handlers.undo_post
    init_act_ob = bpy.data.objects[init_act_ob_name]

    if ob:
        if ob.mode == 'OBJECT' or (ob.mode == 'EDIT' and ob.type != 'LATTICE'):
            if not is_init_ob_pinned:
                scene.ml_pinned_object = None
            bpy.context.view_layer.objects.active = init_act_ob
            undo_handlers.remove(scene_correct_state_after_undo_ensure)

        try:
            depsgraph_handlers.remove(scene_correct_state_after_editmode_toggle_ensure)
        except ValueError:
            pass

    else:
        try:
            undo_handlers.remove(scene_correct_state_after_undo_ensure)
        except ValueError:
            pass


class OBJECT_OT_ml_lattice_toggle_editmode(Operator):
    bl_idname = "object.lattice_toggle_editmode"
    bl_label = "Toggle Lattice Edit Mode"
    bl_description = "Toggle lattice edit mode"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        ob = context.object
        scene = context.scene
        depsgraph_handlers = bpy.app.handlers.depsgraph_update_post
        undo_handlers = bpy.app.handlers.undo_post

        global init_mode
        global is_init_ob_pinned
        global init_act_ob_name

        # Make sure the handlers are removed
        try:
            depsgraph_handlers.remove(scene_correct_state_after_editmode_toggle_ensure)
        except ValueError:
            pass

        try:
            undo_handlers.remove(scene_correct_state_after_undo_ensure)
        except ValueError:
            pass

        if ob.type == 'LATTICE':
            is_lattice_edit_mode_on = ob.mode == 'EDIT'
        else:
            is_lattice_edit_mode_on = False

        if not is_lattice_edit_mode_on:
            init_mode = context.mode
            is_init_ob_pinned = bool(scene.ml_pinned_object)
            init_act_ob_name = ob.name

            ml_active_ob = get_ml_active_object()
            
            scene.ml_pinned_object = ml_active_ob
            
            active_mod_index = ml_active_ob.ml_modifier_active_index
            active_mod = ml_active_ob.modifiers[active_mod_index]
            gizmo_ob = get_gizmo_object_from_modifier(active_mod)

            bpy.ops.object.mode_set(mode='OBJECT')

            context.view_layer.objects.active = gizmo_ob

            bpy.ops.object.mode_set(mode='EDIT')

            depsgraph_handlers.append(scene_correct_state_after_editmode_toggle_ensure)
            undo_handlers.append(scene_correct_state_after_undo_ensure)

        else:
            try:
                depsgraph_handlers.remove(scene_correct_state_after_editmode_toggle_ensure)
            except ValueError:
                pass

            try:
                undo_handlers.remove(scene_correct_state_after_undo_ensure)
            except ValueError:
                pass

            bpy.ops.object.mode_set(mode='OBJECT')

            init_act_ob = bpy.data.objects[init_act_ob_name]

            if is_init_ob_pinned:
                bpy.context.view_layer.objects.active = init_act_ob

                if init_mode == 'EDIT_MESH':
                    bpy.ops.object.mode_set(mode='EDIT')

            else:
                if init_mode == 'OBJECT':
                    ob.select_set(False)
                    context.view_layer.objects.active = init_act_ob
                else:
                    context.view_layer.objects.active = init_act_ob
                    bpy.ops.object.mode_set(mode='EDIT')

                scene.ml_pinned_object = None

        return {'FINISHED'}


def unregister():
    depsgraph_handlers = bpy.app.handlers.depsgraph_update_post
    undo_handlers = bpy.app.handlers.undo_post

    try:
        depsgraph_handlers.remove(scene_correct_state_after_editmode_toggle_ensure)
    except ValueError:
        pass

    try:
        undo_handlers.remove(scene_correct_state_after_undo_ensure)
    except ValueError:
        pass
