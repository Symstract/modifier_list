import addon_utils
import bpy
from bpy.props import *
from bpy.types import AddonPreferences
import rna_keymap_ui


class Preferences(AddonPreferences):
    bl_idname = __name__

    modifier_01: StringProperty()
    modifier_02: StringProperty()
    modifier_03: StringProperty()
    modifier_04: StringProperty()
    modifier_05: StringProperty()
    modifier_06: StringProperty()
    modifier_07: StringProperty()
    modifier_08: StringProperty()
    modifier_09: StringProperty()
    modifier_10: StringProperty()
    modifier_11: StringProperty()
    modifier_12: StringProperty()

    mod_list_def_len: IntProperty(name="",
                                  description="Default/min number of rows to display in the modifier list",
                                  default=7)

    def draw(self, context):
        layout = self.layout

        # === Favourite modifiers selection ===
        layout.label(text="Favourite modifiers:")

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
        layout.label(text="Default/min number of rows to display in the modifier list:")

        row = layout.row()
        split = row.split(factor=0.5)
        split.prop(self, "mod_list_def_len")

        layout.separator()

        # === Hotkey ===
        layout.label(text="Hotkey:")

        col = layout.column()
        kc = bpy.context.window_manager.keyconfigs.addon
        for km, kmi in addon_keymaps:
            km = km.active()
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

        layout.separator()

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