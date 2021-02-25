from bpy.types import Operator

from ..ui.ui_common import favourite_modifiers_configuration_layout


class WM_OT_ml_favourite_modifiers_configuration_popup(Operator):
    bl_idname = "wm.ml_favourite_modifiers_configuration_popup"
    bl_label = "Configure Favourite Modifiers"
    bl_description = "Choose and order your favourite modifiers"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=650)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        layout.separator()

        favourite_modifiers_configuration_layout(context, layout)

        layout.separator()
