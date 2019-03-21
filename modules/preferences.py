import math

import addon_utils
import bpy
from bpy.props import *
from bpy.types import AddonPreferences
import rna_keymap_ui


class Preferences(AddonPreferences):
    bl_idname = "modifier_list"

    use_popup: BoolProperty(name="Popup", description="Enable/disable popup",
                              default=True)

    use_sidebar: BoolProperty(name="Sidebar Tab", description="Enable/disable sidebar tab",
                              default=True)

    modifier_01: StringProperty(description="Add a favourite modifier")
    modifier_02: StringProperty(description="Add a favourite modifier")
    modifier_03: StringProperty(description="Add a favourite modifier")
    modifier_04: StringProperty(description="Add a favourite modifier")
    modifier_05: StringProperty(description="Add a favourite modifier")
    modifier_06: StringProperty(description="Add a favourite modifier")
    modifier_07: StringProperty(description="Add a favourite modifier")
    modifier_08: StringProperty(description="Add a favourite modifier")
    modifier_09: StringProperty(description="Add a favourite modifier")
    modifier_10: StringProperty(description="Add a favourite modifier")
    modifier_11: StringProperty(description="Add a favourite modifier")
    modifier_12: StringProperty(description="Add a favourite modifier")

    mod_list_def_len: IntProperty(name="",
                                  description="Default/min number of rows to display in the modifier list in the popup",
                                  default=7)

    def draw(self, context):
        layout = self.layout

        # === Enable/disable popup and sidebar
        row = layout.row()

        # Disabled for now because of a bug in 2.8.
        # https://developer.blender.org/T60766
        # row.prop(self, "use_popup")

        # wm = bpy.context.window_manager
        # km = wm.keyconfigs.addon.keymaps['3D View']
        # kmi = km.keymap_items["view3d.modifier_popup"]
        # kmi.active = self.use_popup

        row.prop(self, "use_sidebar")

        layout.separator()

        # === Favourite modifiers selection ===
        layout.label(text="Favourite Modifiers:")

        col = layout.column(align=True)

        num_of_mods = len(get_pref_mod_attr_name())
        num_of_rows = math.ceil(num_of_mods / 2)

        attr_iter = iter(get_pref_mod_attr_name())

        wm = bpy.context.window_manager

        # Draw two property searches per row
        for attr in attr_iter:
            row = col.split(factor=0.5, align=True)
            row.prop_search(self, attr, wm, "all_modifiers", text="", icon='MODIFIER')
            row.prop_search(self, next(attr_iter), wm, "all_modifiers", text="", icon='MODIFIER')

        layout.separator()

        # === Number of rows in the modifier list ===
        row = layout.row()
        row.label(text="Modifier List Default/Min Height in Popup")
        row.prop(self, "mod_list_def_len")

        layout.separator()

        # Disabled for now because of a bug in 2.8.
        # # === Hotkey ===
        # layout.label(text="Hotkey:")

        # col = layout.column()
        # kc = bpy.context.window_manager.keyconfigs.addon
        # for km, kmi in addon_keymaps:
        #     km = km.active()
        #     col.context_pointer_set("keymap", km)
        #     rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

        # layout.separator()

        # === Info ===
        is_loaded, is_enabled = addon_utils.check("space_view3d_modifier_tools")
        if not is_enabled:
            layout.label(icon='INFO', text="Enable Modifier Tools addon for modifier batch operators.")


def get_pref_mod_attr_name():
    """List of the names of favourite modifier attributes in Preferences
    class for making drawing favourite modifier selection rows in
    preferences easy.
    """
    attr_name_list = [attr for attr in Preferences.__annotations__ if "modifier_" in attr]
    return attr_name_list