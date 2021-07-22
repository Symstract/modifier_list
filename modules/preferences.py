import json
import math
import os

import bpy
# import rna_keymap_ui
from bpy.props import *
from bpy.types import AddonPreferences

from .icons import load_icons
from .ui.properties_editor import register_DATA_PT_modifiers
from .ui.ui_common import box_with_header, favourite_modifiers_configuration_layout
from .ui.sidebar import update_sidebar_category


def read_prefs(prefs_file):
    """Read preferences from a json"""
    if not os.path.exists(prefs_file) or not prefs_file.endswith(".json"):
        return

    prefs = bpy.context.preferences.addons["modifier_list"].preferences

    with open(prefs_file) as f:
        try:
            prefs_dict = json.load(f)
            for prop in prefs_dict.keys():
                if prop in prefs.__annotations__:
                    value = prefs_dict[prop]
                    ensured_value = set(value) if type(value) is list else value
                    setattr(prefs, prop, ensured_value)
        except json.decoder.JSONDecodeError:
            pass


def write_prefs():
    """Write preferences into a json"""
    prefs = bpy.context.preferences.addons["modifier_list"].preferences

    prefs_dict = {}

    for prop in prefs.__annotations__:
        value = getattr(prefs, prop)
        ensured_value = list(value) if type(value) is set else value
        prefs_dict[prop] = ensured_value

    config_dir = bpy.utils.user_resource('CONFIG')
    ml_config_dir = os.path.join(config_dir, "modifier_list")

    if not os.path.exists(ml_config_dir):
        os.mkdir(ml_config_dir)

    prefs_file = os.path.join(ml_config_dir, "preferences.json")

    with open(prefs_file, 'w', encoding='utf-8') as f:
        json.dump(prefs_dict, f, ensure_ascii=False, indent=4)


def use_properties_editor_callback(self, context):
    register_DATA_PT_modifiers(self, context)


def sidebar_category_callback(self, context):
    update_sidebar_category()


def icon_color_callback(self, context):
    load_icons()


class Preferences(AddonPreferences):
    bl_idname = "modifier_list"

    # === General settings ===
    # Disabled for now because of a bug in 2.8.
    # https://developer.blender.org/T60766
    # use_popup: BoolProperty(name="Popup", description="Enable/disable popup", default=True)

    use_sidebar: BoolProperty(
        name="Sidebar",
        description="Enable/disable the Sidebar tab",
        default=True)

    use_properties_editor: BoolProperty(
        name="Properties Editor",
        description="Enable/disable inside Properties Editor",
        default=True,
        update=use_properties_editor_callback)

    keep_sidebar_visible: BoolProperty(
        name="Keep Sidebar Panels Visible",
        description="Keep the sidebar panels always visible")

    sidebar_category: StringProperty(
        name="Sidebar Category",
        default="Modifier List",
        update=sidebar_category_callback)

    favourites_per_row_items = [
        ("2", "2", "", 1),
        ("3", "3", "", 2)
    ]
    favourites_per_row: EnumProperty(
        items=favourites_per_row_items,
        name="Favourites Per Row",
        description="The number of favourites per row",
        default="2")

    auto_sort_favourites_when_choosing_from_menu: BoolProperty(
        name="Auto Sort Favourites When Choosing From Menu",
        description="Automatically sort favourite modifiers when choosing from the menu. "
                    "Also removes empty slots between favourites")

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

    use_icons_in_favourites: BoolProperty(
        name="Use Icons In Favourites",
        description="Use icons in favourite modifier buttons",
        default=True)

    insert_modifier_after_active: BoolProperty(
        name="Insert New Modifier After Active",
        description="When adding a new modifier, insert it after the active one. \n"
                    "Hold Control to override this. (When off, the behaviour is reversed). \n"
                    "NOTE: This is really slow on heavy meshes")

    disallow_applying_hidden_modifiers: BoolProperty(
        name="Disallow Applying Hidden Modifiers",
        description="Disallow applying modifier's which are hidden in the viewport. \n"
                    "Hold Alt to override this. (When off, the behaviour is reversed)")

    icon_color_items = [
        ("black", "Black", "", 1),
        ("white", "White", "", 2)
    ]
    icon_color: EnumProperty(
        items=icon_color_items,
        name="Icon Color",
        description="Color of the addon's custom icons",
        default="white",
        update=icon_color_callback)

    reverse_list: BoolProperty(
        name="Reverse List",
        description="Reverse the order of the list persistently (requires restart)")

    hide_general_settings_region: BoolProperty(
        name="Hide General Settings Region",
        description="Hide the region which shows modifier name and display settings. "
                    "The same settings are also inside the modifier list")

    show_confirmation_popups: BoolProperty(
        name="Show Confirmation Popups",
        description="Show confirmation popups for Apply All Modifiers "
                    "and Remove All Modifiers operators",
        default=True)

    batch_ops_reports_items = [
        ("APPLY", "Apply", ""),
        ("REMOVE", "Remove", ""),
        ("TOGGLE_VISIBILITY", "Toggle visibility", "")
    ]
    batch_ops_reports: EnumProperty(
        items=batch_ops_reports_items,
        name="Show Info Messages For",
        description="Show batch operator info messages for",
        default={'APPLY', 'REMOVE', 'TOGGLE_VISIBILITY'},
        options={'ENUM_FLAG'})

    # === Popup settings ===
    popup_width: IntProperty(
        name="Width",
        description="Width of the popup, excluding the navigation bar",
        default=300)

    mod_list_def_len: IntProperty(
        name="",
        description="Default/min number of rows to display in the modifier list in the popup",
        default=7)

    use_props_dialog: BoolProperty(
        name="Use Dialog Type Popup",
        description="Use a dialog type popup which doesn't close when you are not hovering over "
                    "it")

    # === Gizmo object settings ===
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

        prefs_ui_props = context.window_manager.modifier_list.preferences_ui_props

        # === Info ===
        col = layout.column()
        col.label(icon='INFO',
                  text="Preferences are auto saved into your Blender config folder, eg:")
        col.label(text="      '...\\Blender Foundation\\Blender\\<blender version>"
                       "\\config\\modifier_list\\preferences.json'")

        layout.separator()

        # === Import ===
        filepath = os.path.dirname(bpy.utils.resource_path('USER')) + os.path.sep
        layout.operator("wm.ml_preferences_import", icon='IMPORT').filepath = filepath

        layout.separator()

        # === Enable/disable popup and sidebar
        # row = layout.row()

        # Disabled for now because of a bug in 2.8.
        # https://developer.blender.org/T60766
        # row.prop(self, "use_popup")

        # wm = bpy.context.window_manager
        # km = wm.keyconfigs.addon.keymaps['3D View']
        # kmi = km.keymap_items["view3d.modifier_popup"]
        # kmi.active = self.use_popup

        layout.prop(self, "use_properties_editor")
        layout.prop(self, "use_sidebar")

        if self.use_sidebar:
            layout.separator()

            layout.prop(self, "keep_sidebar_visible")
            split = layout.split()
            split.label(text="Sidebar Category")
            split.prop(self, "sidebar_category", text="")

        layout.separator()

        # === Favourite modifiers ===
        box = box_with_header(layout, "Favourite Modifiers", prefs_ui_props,
                              "favourite_modifiers_expand")

        if prefs_ui_props.favourite_modifiers_expand:
            split = box.split()
            split.label(text="Favourites Per Row")
            split.row().prop(self, "favourites_per_row", expand=True)

            box.separator()

            favourite_modifiers_configuration_layout(context, box)

            box.separator()

            box.prop(self, "use_icons_in_favourites")

        # === General settings ===
        box = box_with_header(layout, "General", prefs_ui_props, "general_expand")

        if prefs_ui_props.general_expand:
            box.prop(self, "insert_modifier_after_active")
            box.prop(self, "disallow_applying_hidden_modifiers")

            split = box.split()
            split.label(text="Icon Color")
            split.row().prop(self, "icon_color", expand=True)

            box.prop(self, "reverse_list")
            box.prop(self, "hide_general_settings_region")
            box.prop(self, "show_confirmation_popups")

            split = box.split()
            split.label(text="Show Info Messages For")
            split.row().prop(self, "batch_ops_reports", expand=True)

        # === Popup settings ===
        box = box_with_header(layout, "Popup", prefs_ui_props, "popup_expand")

        if prefs_ui_props.popup_expand:
            row = box.row()
            row.label(text="Popup Width")
            row.prop(self, "popup_width", text="")

            row = box.row()
            row.label(text="Modifier List Default/Min Height in Popup")
            row.prop(self, "mod_list_def_len")

            box.prop(self, "use_props_dialog")

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
        box = box_with_header(layout, "Gizmo", prefs_ui_props, "gizmo_expand")

        if prefs_ui_props.gizmo_expand:
            box.prop(self, "parent_new_gizmo_to_object")
            box.prop(self, "match_gizmo_size_to_object")
            box.prop(self, "always_delete_gizmo")


def register():
    # === Read preferences from a json ===
    config_dir = bpy.utils.user_resource('CONFIG')
    prefs_file = os.path.join(config_dir, "modifier_list", "preferences.json")
    read_prefs(prefs_file)


def unregister():
    # === Write preferences into a json ===
    write_prefs()
