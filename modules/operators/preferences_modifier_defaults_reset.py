from bpy.types import Operator


class WM_OT_ml_modifier_defaults_reset(Operator):
    bl_idname = "wm.ml_modifier_defaults_reset"
    bl_label = "Reset Modifier Defaults"
    bl_description = ("Reset the currently shown modifier default "
                      "settings to their default values")
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        ml_props = context.window_manager.modifier_list
        mod = ml_props.preferences_ui_props.modifier_to_show_defaults_for
        return mod and mod != "Geometry Nodes"

    def execute(self, context):
        ml_props = context.window_manager.modifier_list
        mod_name = ml_props.preferences_ui_props.modifier_to_show_defaults_for
        mod_type = ml_props.all_modifiers[mod_name].value
        all_defaults = context.preferences.addons["modifier_list"].preferences.modifier_defaults
        mod_defaults_group = getattr(all_defaults, mod_type)

        for setting, _ in list(mod_defaults_group.items()):
            mod_defaults_group.property_unset(setting)

        return {'FINISHED'}
