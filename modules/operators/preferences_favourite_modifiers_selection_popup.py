from bpy.types import Operator

from ..ui.ui_common import favourite_modifiers_selection_layout


class WM_OT_ml_favourite_modifiers_selection_popup(Operator):
    bl_idname = "wm.ml_favourite_modifiers_selection_popup"
    bl_label = "Select Favourite Modifiers"
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

        favourite_modifiers_selection_layout(context, layout)

        layout.separator()
