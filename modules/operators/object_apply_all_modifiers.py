"""
This operator is inspired by Modifier Tools add-on, thanks for the authors
meta-androcto, saidenka and lijenstina.
https://wiki.blender.org/wiki/Extensions:2.6/Py/Scripts/3D_interaction/modifier_tools
"""

import numpy as np

import bpy
from bpy.props import *
from bpy.types import Operator

from ..multiuser_data_modifier_apply_utils import LinkedObjectDataChanger
from ..utils import get_ml_active_object


show_done_label_in_dialog = False


class VIEW3D_OT_ml_apply_all_modifiers_multi_user_data_dialog(Operator):
    bl_idname = "view3d.ml_apply_all_modifiers_multi_user_data_dialog"
    bl_label = "Apply All Modifiers Dialog"
    bl_options = {'INTERNAL'}

    op_name: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=380)

    def draw(self, context):
        layout = self.layout

        # Popups can't be closed manually, so just show a label after
        # the modifier has been applied.
        if show_done_label_in_dialog:
            layout.label(text="Done")
            return

        layout.label(text="Active object's data is used by multiple objects. "
                          "What would you like to do?")

        layout.separator()

        op = layout.operator(self.op_name, text="Apply To Active Object Only (Break Link)")
        op.multi_user_data_apply_method = 'APPLY_TO_SINGLE'

        op = layout.operator(self.op_name, text="Apply To All Objects")
        op.multi_user_data_apply_method = 'APPLY_TO_ALL'

        layout.separator()

        sel_obs = context.selected_objects

        if (len(sel_obs) > 1 or (sel_obs and get_ml_active_object() not in sel_obs)):
            layout.label(text="In order to apply all modifiers of all objects, first make their "
                              "data unique.")


# It doesn't seem possible to access attributes in execute which are
# defined in invoke when using window_manager.invoke_confirm. So need to
# store this globally then.
disallow_applying_hidden_modifiers = False


class VIEW3D_OT_ml_apply_all_modifiers(Operator):
    bl_idname = "view3d.ml_apply_all_modifiers"
    bl_label = "Apply All Modifiers"
    bl_description = "Apply all modifiers of the selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    multi_user_data_apply_method_items = [
        ('NONE', "None", ""),
        ("APPLY_TO_SINGLE", "Apply To Single", ""),
        ("APPLY_TO_ALL", "Apply To All", "")
    ]
    multi_user_data_apply_method: EnumProperty(
        items=multi_user_data_apply_method_items,
        default='NONE',
        options={'HIDDEN', 'SKIP_SAVE'})

    def __init__(self):
        self.objects_have_local_data = False
        self.objects_have_modifiers = False
        self.objects_have_local_modifiers = False
        self.skipped_objects_with_non_local_data = False
        self.skipped_linked_modifiers = False
        self.ojects_with_modifiers_failed_to_apply = []

    @classmethod
    def poll(cls, context):
        return get_ml_active_object() is not None or bool(context.selected_objects)

    def execute(self, context):
        is_edit_mode = context.mode in {'EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE',
                                        'EDIT_TEXT', 'EDIT_LATTICE'}

        if is_edit_mode:
            bpy.ops.object.editmode_toggle()
            bpy.ops.ed.undo_push(message="Toggle Editmode")

        if self.multi_user_data_apply_method != 'NONE':
            self.linked_object_data_changer = LinkedObjectDataChanger(get_ml_active_object())
            self.linked_object_data_changer.make_active_instance_data_unique()

        self.apply_modifiers(context)

        # Cancel if no modifiers were applied

        some_mods_were_applied = self.check_for_applied_modifiers_and_report()

        if not some_mods_were_applied:
            if self.multi_user_data_apply_method != 'NONE':
                self.linked_object_data_changer.reassign_old_data_to_active_instance()
            return {'CANCELLED'}

        if is_edit_mode:
            bpy.ops.ed.undo_push(message="Apply All Modifiers")
            bpy.ops.object.editmode_toggle()

        # Apply the modifier to all instances
        if self.multi_user_data_apply_method == 'APPLY_TO_ALL':
            self.linked_object_data_changer.assign_new_data_to_other_instances()

        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        # Info messages for when some modifiers were applied
        if self.ojects_with_modifiers_failed_to_apply:
            self.some_modifiers_could_not_be_applied_report()
        elif 'APPLY' in prefs.batch_ops_reports:
            self.apply_report()

        global show_done_label_in_dialog
        show_done_label_in_dialog = True

        return {'FINISHED'}

    def invoke(self, context, event):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences
        global disallow_applying_hidden_modifiers
        disallow_applying_hidden_modifiers = (
            not prefs.disallow_applying_hidden_modifiers if event.alt
            else prefs.disallow_applying_hidden_modifiers)

        if self.multi_user_data_apply_method == 'NONE' and get_ml_active_object().data.users > 1:
            global show_done_label_in_dialog
            show_done_label_in_dialog = False
            bpy.ops.view3d.ml_apply_all_modifiers_multi_user_data_dialog('INVOKE_DEFAULT',
                                                                         op_name=self.bl_idname)
            return {'CANCELLED'}
        elif prefs.show_confirmation_popups and self.multi_user_data_apply_method == 'NONE':
            return context.window_manager.invoke_confirm(self, event)

        return self.execute(context)

    def apply_modifiers(self, context):
        ml_act_ob = get_ml_active_object()

        # When the active object has multi-user data, only its modifiers
        # should be applied.
        if self.multi_user_data_apply_method != 'NONE':
            obs = [ml_act_ob]
        else:
            obs = context.selected_objects.copy()
            if ml_act_ob not in obs:
                obs.append(ml_act_ob)

        override = context.copy()

        for ob in obs:
            override['object'] = ob
            data = ob.data
            mods = ob.modifiers

            # Skip linked objects with no library override and local
            # data.
            if ob.library or (ob.override_library and (data.library or data.override_library)):
                self.skipped_objects_with_non_local_data = True
                continue

            self.objects_have_local_data = True

            for mod in mods:
                self.objects_have_modifiers = True

                if disallow_applying_hidden_modifiers and not mod.show_viewport:
                    continue

                # Only try to apply local modifiers
                if not ob.override_library or mod.is_property_overridable_library("name"):
                    try:
                        bpy.ops.object.modifier_apply(override, modifier=mod.name)
                    except:
                        if ob.name not in self.ojects_with_modifiers_failed_to_apply:
                            self.ojects_with_modifiers_failed_to_apply.append(ob.name)
                    self.objects_have_local_modifiers = True
                else:
                    self.skipped_linked_modifiers = True

            # Make sure some modifier is always active even if all
            # modifiers can't be applied
            mods_len = len(mods) - 1
            new_index = np.clip(mods_len, 0, 99)
            ob.ml_modifier_active_index = new_index

    def check_for_applied_modifiers_and_report(self):
        if not self.objects_have_local_data:
            self.report({'INFO'}, "No objects with local data")
            return False
        elif not self.objects_have_modifiers:
            self.report({'INFO'}, "No modifiers to apply")
            return False
        elif not self.objects_have_local_modifiers:
            self.report({'INFO'}, "No local modifiers to apply")
            return False

        return True

    def some_modifiers_could_not_be_applied_report(self):
        failed_obs = ", ".join(self.ojects_with_modifiers_failed_to_apply)
        if len(self.ojects_with_modifiers_failed_to_apply) < 8:
            self.report({'INFO'}, f"Some modifier(s) couldn't be applied on {failed_obs}")
        else:
            self.report({'INFO'}, "Some modifier(s) couldn't be applied. Check the system "
                                  "console for a list of the objects.")
            print(f"Some modifier(s) couldn't be applied on {failed_obs}")

    def apply_report(self):
        skipped_obs_with_non_local_data_message = (" for objects with local data"
                                                   if self.skipped_objects_with_non_local_data
                                                   else "")
        if disallow_applying_hidden_modifiers:
            message = ("Applied all visible local modifiers" if self.skipped_linked_modifiers
                       else "Applied all visible modifiers")
            self.report({'INFO'}, message + skipped_obs_with_non_local_data_message)
        else:
            message = ("Applied all local modifiers" if self.skipped_linked_modifiers
                       else "Applied all modifiers")
            self.report({'INFO'}, message + skipped_obs_with_non_local_data_message)
