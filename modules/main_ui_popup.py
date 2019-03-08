import bpy
from bpy.props import *
from bpy.types import Operator
from .modifiers.modifiers_ui import ui_modifiers


panel_width = 300
tabs_width = 26
overall_width = panel_width + tabs_width

class VIEW_3D_PT_modifier_popup(Operator):
    bl_idname = "view3d.modifier_popup"
    bl_label = "Modifier Pop-up Panel"

    popup_tabs_items = [
        ("MODIFIERS", "Modifiers", "Modifiers", 'MODIFIER', 1),
        ("OBJECT_DATA", "Object Data", "Object Data", 'MESH_DATA', 2),
    ]

    popup_tab: EnumProperty(items=popup_tabs_items, name="Popup Tabs", default='MODIFIERS')


    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
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

            if self.popup_tab == 'MODIFIERS':
                ui_modifiers(context, col)
            elif self.popup_tab == 'OBJECT_DATA':
                col.label(text="Coming soon")

            # === Tabs ===
            col = split.column(align=True)
            col.scale_y = 1.3
            col.prop_tabs_enum(self, "popup_tab", icon_only=True)
