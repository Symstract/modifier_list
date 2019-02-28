from bpy.types import Operator

from .modifiers import ui_modifiers


class VIEW_3D_PT_modifier_popup(Operator):
    bl_idname = "view3d.modifier_popup"
    bl_label = "Modifier Pop-up Panel"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        ui_modifiers(col)