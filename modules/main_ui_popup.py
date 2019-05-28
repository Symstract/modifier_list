import bpy
from bpy.props import *
from bpy.types import Operator

from .modifiers.modifiers_ui import modifiers_ui
from .vertex_groups_ui import vertex_groups_ui


panel_width = 300
tabs_width = 26
overall_width = panel_width + tabs_width


class VIEW3D_OT_ml_modifier_popup(Operator):
    bl_idname = "view3d.modifier_popup"
    bl_label = "Modifier Popup Panel"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        if prefs.use_props_dialog:
            return context.window_manager.invoke_props_dialog(self, width=overall_width)

        return context.window_manager.invoke_popup(self, width=overall_width)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        ob = context.object

        if not ob:
            layout.label(text="No active object")
        elif ob.type not in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE'}:
            layout.label(text="Wrong object type")
        else:
            split_factor = panel_width / overall_width
            split = layout.split(factor=split_factor)


            # === Content ===
            col = split.column()

            wm = bpy.context.window_manager
            popup_tab = wm.ml_popup_active_tab

            prefs = bpy.context.preferences.addons["modifier_list"].preferences

            # Don't add a label when props_dialog is used, avoiding
            # wasting space.
            use_label = not prefs.use_props_dialog

            if popup_tab == 'MODIFIERS':
                num_of_rows = prefs.mod_list_def_len
                if use_label:
                    col.label(text="Modifiers")
                modifiers_ui(context, col, num_of_rows=num_of_rows)
            elif popup_tab == 'OBJECT_DATA':
                if use_label:
                    col.label(text="Vertex Groups")
                vertex_groups_ui(context, col, num_of_rows=7)

            # === Tabs ===
            col = split.column(align=True)
            col.scale_y = 1.3
            col.prop_tabs_enum(wm, "ml_popup_active_tab", icon_only=True)


def register():
    popup_tabs_items = [
        ("MODIFIERS", "Modifiers", "Modifiers", 'MODIFIER', 1),
        ("OBJECT_DATA", "Object Data", "Object Data", 'MESH_DATA', 2),
    ]

    wm = bpy.types.WindowManager
    wm.ml_popup_active_tab = EnumProperty(items=popup_tabs_items, name="Popup Tabs", default='MODIFIERS')



