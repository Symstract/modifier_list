from bpy.types import Panel

from .modifiers.modifiers_ui import modifiers_ui
from .vertex_groups_ui import vertex_groups_ui

class VIEW3D_PT_Modifiers(Panel):
    bl_idname = "view3d.modifiers"
    bl_label = "Modifiers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MPP'

    def draw(self, context):
        layout = self.layout
        modifiers_ui(context, layout)


class VIEW3D_PT_Vertex_groups(Panel):
    bl_idname = "view3d.vertex_groups"
    bl_label = "Vertex Groups"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MPP'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        vertex_groups_ui(context, layout)