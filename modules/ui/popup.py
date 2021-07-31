import bpy
from bpy.props import *
from bpy.types import Operator

from .modifiers_ui import modifiers_ui_with_list, modifiers_ui_with_stack
from .ui_common import pin_object_button
from .vertex_groups_ui import vertex_groups_ui
from ..utils import get_ml_active_object, object_type_has_modifiers


class VIEW3D_OT_ml_modifier_popup(Operator):
    bl_idname = "view3d.modifier_popup"
    bl_label = "Modifier Popup"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        self.panel_width = prefs.popup_width
        TABS_WIDTH = 26
        self.overall_width = self.panel_width + TABS_WIDTH

        if prefs.use_props_dialog:
            return context.window_manager.invoke_props_dialog(self, width=self.overall_width)

        return context.window_manager.invoke_popup(self, width=self.overall_width)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        ob = get_ml_active_object()

        if not ob:
            layout.label(text="No active object")
            return
        elif not object_type_has_modifiers(ob):
            layout.label(text="Wrong object type")
            return

        ml_props = bpy.context.window_manager.modifier_list
        popup_tab = ml_props.popup_active_tab

        prefs = bpy.context.preferences.addons["modifier_list"].preferences

        # Don't add a label when props_dialog is used, avoiding
        # wasting space.
        if not prefs.use_props_dialog:
            row = layout.row()
            pin_object_button(context, row)
            row.label(text="Modifier Popup")

        split_factor = self.panel_width / self.overall_width
        split = layout.split(factor=split_factor)

        # === Content ===
        col = split.column()
        if popup_tab == 'MODIFIERS':
            if prefs.popup_style == 'LIST':
                num_of_rows = prefs.mod_list_def_len
                modifiers_ui_with_list(context, col, num_of_rows=num_of_rows, use_in_popup=True)
            else:
                modifiers_ui_with_stack(context, col, use_in_popup=True)
        elif popup_tab == 'OBJECT_DATA':
            vertex_groups_ui(context, col, num_of_rows=7)

        # === Tabs ===
        col = split.column(align=True)
        col.scale_y = 1.3
        col.prop_tabs_enum(ml_props, "popup_active_tab", icon_only=True)

        # When using the dialog type popup, the label is automatic
        # and the pin button can't be put next to it. In that case,
        # display it here.
        if prefs.use_props_dialog:
            col.separator(factor=3)

            pin_object_button(context, col)
