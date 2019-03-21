import bpy
from bpy.types import Panel

from .modifiers.modifiers_ui import modifiers_ui
from .vertex_groups_ui import vertex_groups_ui


class BasePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Modifier List"

    @classmethod
    def use_sidebar(cls):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences
        use_sidebar = prefs.use_sidebar
        return use_sidebar



class VIEW3D_PT_Modifiers(Panel, BasePanel):
    bl_idname = "view3d.ml_modifiers"
    bl_label = "Modifiers"

    @classmethod
    def poll(cls, context):
        if not cls.use_sidebar():
            return False
        if context.object is not None:
            return context.object.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE'}
        return False

    def draw(self, context):
        layout = self.layout
        modifiers_ui(context, layout)


class VIEW3D_PT_Vertex_groups(Panel, BasePanel):
    bl_idname = "view3d.ml_vertex_groups"
    bl_label = "Vertex Groups"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not cls.use_sidebar():
            return False
        if context.object is not None:
            return context.object.type in {'MESH', 'LATTICE'}
        return False

    def draw(self, context):
        layout = self.layout
        vertex_groups_ui(context, layout)