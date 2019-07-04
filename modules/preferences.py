import math

import bpy
import addon_utils
import rna_keymap_ui
from bpy.props import *
from bpy.types import AddonPreferences

from .icons import reload_icons
from .ui.properties_editor import register_DATA_PT_modifiers


class Preferences(AddonPreferences):
    bl_idname = "modifier_list"

    use_popup: BoolProperty(name="Popup", description="Enable/disable popup", default=True)

    use_sidebar: BoolProperty(name="Sidebar",
                              description="Enable/disable the Sidebar tab", default=True)

    use_properties_editor: BoolProperty(name="Properties Editor",
                                       description="Enable/disable inside Properties Editor",
                                       default=True, update=register_DATA_PT_modifiers)

    favourites_per_row_items = [
        ("2", "2", "", 1),
        ("3", "3", "", 2)
    ]
    favourites_per_row: EnumProperty(items=favourites_per_row_items, name="Favourites Per Row",
                             description="The number of favourites per row", default="2")

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

    use_icons_in_favourites: BoolProperty(name="Use Icons In Favourites",
                                          description="Use icons in favourite modifier buttons",
                                          default=True)

    icon_color_items = [
        ("black", "Black", "", 1),
        ("white", "White", "", 2)
    ]
    icon_color: EnumProperty(items=icon_color_items, name="Icon Color",
                             description="Color of the addon's custom icons", default="white",
                             update=reload_icons)

    hide_general_settings_region: BoolProperty(
        name="Hide General Settings Region",
        description="Hide the region which shows modifier name and display settings. "
                    "The same settings are also inside the modifier list")

    popup_width: IntProperty(name="Width",
                              description="Width of the popup, excluding the navigation bar",
                              default=300)

    mod_list_def_len: IntProperty(
        name="",
        description="Default/min number of rows to display in the modifier list in the popup",
        default=7)

    use_props_dialog: BoolProperty(
        name="Use Dialog Type Popup",
        description="Use a dialog type popup which doesn't close when you are not hovering over it")

    parent_new_gizmo_to_object: BoolProperty(
        name="Auto Parent Gizmos To Active Object",
        description="Automatically parent gizmos to the active object on addition")

    match_gizmo_size_to_object: BoolProperty(
        name="Match Gizmo Size To Active Object",
        description="Automatically match the size of the gizmo to the largest dimension of the "
                    "active object (before modifiers).\n"
                    "NOTE: This can be a bit slow on heavy meshes")

    always_delete_gizmo: BoolProperty(
        name="Always Delete Gizmo",
        description="Always delete the gizmo object when applying or removing a modifier. "
                    "When off, the gizmo object is deleted only when holding shift")

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
        row.prop(self, "use_properties_editor")

        layout.separator()

        # === Favourite modifiers ===
        layout.label(text="Favourite Modifiers:")

        split = layout.split()
        split.label(text="Favourites Per Row")
        row = split.row()
        row.prop(self, "favourites_per_row", expand=True)

        # === Favourite modifiers selection ===
        col = layout.column(align=True)

        attr_iter = iter(get_pref_mod_attr_name())

        wm = bpy.context.window_manager

        # Draw 2 or 3 property searches per row
        for attr in attr_iter:
            row = col.row(align=True)
            row.prop_search(self, attr, wm, "ml_mesh_modifiers", text="", icon='MODIFIER')
            row.prop_search(self, next(attr_iter), wm, "ml_mesh_modifiers", text="", icon='MODIFIER')
            if self.favourites_per_row == '3':
                row.prop_search(self, next(attr_iter), wm, "ml_mesh_modifiers", text="", icon='MODIFIER')

        # =====================================

        layout.separator()

        layout.prop(self, "use_icons_in_favourites")

        layout.separator()

        # === General settings ===
        layout.label(text="General:")

        split = layout.split()
        split.label(text="Icon Color")
        row = split.row()
        row.prop(self, "icon_color", expand=True)

        layout.prop(self, "hide_general_settings_region")

        layout.separator()

        # === Popup settings ===
        layout.label(text="Popup:")

        row = layout.row()
        row.label(text="Popup Width")
        row.prop(self, "popup_width", text="")

        row = layout.row()
        row.label(text="Modifier List Default/Min Height in Popup")
        row.prop(self, "mod_list_def_len")

        layout.prop(self, "use_props_dialog")

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

        # === Gizmo object settings ===
        layout.label(text="Gizmo:")

        layout.prop(self, "parent_new_gizmo_to_object")
        layout.prop(self, "match_gizmo_size_to_object")
        layout.prop(self, "always_delete_gizmo")

        # === Info ===
        _, is_enabled = addon_utils.check("space_view3d_modifier_tools")
        if not is_enabled:
            layout.label(icon='INFO',
                         text="Enable Modifier Tools addon for modifier batch operators.")


def get_pref_mod_attr_name():
    """List of the names of favourite modifier attributes in Preferences
    class for making drawing favourite modifier selection rows in
    preferences easy.
    """
    attr_name_list = [attr for attr in Preferences.__annotations__ if "modifier_" in attr]
    return attr_name_list