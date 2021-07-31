import bpy

from .. import modifier_categories
from ..utils import get_favourite_modifiers


def box_with_header(layout, text, expand_data, expand_prop):
    """Template for a header for boxes used as panels.

    Includes a triangle icon whose state is defined by expand_prop, a
    property of expand_data.

    Returns the header row and the box.
    """
    box = layout.box()

    row = box.row()
    icon = 'TRIA_DOWN' if getattr(expand_data, expand_prop) else 'TRIA_RIGHT'
    row.prop(expand_data, expand_prop, icon=icon, text="", emboss=False)
    row.label(text=text)

    return row, box


def favourite_modifiers_configuration_layout(context, layout):
    prefs = context.preferences.addons["modifier_list"].preferences
    ml_props = context.window_manager.modifier_list
    favourites_dict = get_favourite_modifiers()
    favourite_mod_attr_names = favourites_dict.keys()
    favourite_mods = set(favourites_dict.values())

    # === Modifier menu ===

    _, box = box_with_header(layout, "Menu", ml_props.preferences_ui_props,
                             "favourite_modifiers_menu_expand")

    if ml_props.preferences_ui_props.favourite_modifiers_menu_expand:
        box.prop(prefs, "auto_sort_favourites_when_choosing_from_menu")

        box.separator()

        row = box.row()
        row.alignment = 'LEFT'

        col = row.column(align=True)
        col.label(text="Modify")
        col.separator(factor=0.3)
        for name, icon, _ in modifier_categories.ALL_MODIFY_NAMES_ICONS_TYPES:
            col.operator("ui.ml_favourite_modifier_toggle", text=name, icon=icon,
                         depress=name in favourite_mods).modifier = name

        col = row.column(align=True)
        col.label(text="Generate")
        col.separator(factor=0.3)
        for name, icon, _ in modifier_categories.ALL_GENERATE_NAMES_ICONS_TYPES:
            col.operator("ui.ml_favourite_modifier_toggle", text=name, icon=icon,
                         depress=name in favourite_mods).modifier = name

        col = row.column(align=True)
        col.label(text="Deform")
        col.separator(factor=0.3)
        for name, icon, _ in modifier_categories.ALL_DEFORM_NAMES_ICONS_TYPES:
            col.operator("ui.ml_favourite_modifier_toggle", text=name, icon=icon,
                         depress=name in favourite_mods).modifier = name

        col = row.column(align=True)
        label = "Simulate" if bpy.app.version[1] < 90 else "Physics"
        col.label(text=label)
        col.separator(factor=0.3)
        for name, icon, _ in modifier_categories.ALL_SIMULATE_NAMES_ICONS_TYPES:
            col.operator("ui.ml_favourite_modifier_toggle", text=name, icon=icon,
                         depress=name in favourite_mods).modifier = name

        layout.separator()

    # === Favourite slots ===

    row = layout.row()

    col = row.column(align=True)

    active_slot_index = ml_props.active_favourite_modifier_slot_index

    # Draw 2 or 3 property searches per row
    for i, attr in enumerate(favourite_mod_attr_names):
        if (i == 0 or (prefs.favourites_per_row == '2' and i % 2 == 0)
                or (prefs.favourites_per_row == '3' and i % 3 == 0)):
            split = col.split(align=True)

        sub_row = split.row(align=True)
        icon = 'LAYER_ACTIVE' if i == active_slot_index else 'LAYER_USED'
        sub_row.operator("ui.ml_active_favourite_modifier_slot_set", icon=icon, text="",
                         depress=i == active_slot_index).index = i
        sub_row.prop_search(prefs, attr, ml_props, "all_modifiers", text="", icon='MODIFIER')

    sub = row.column(align=True)

    sub.operator("ui.ml_active_favourite_modifier_remove", icon='REMOVE', text="")

    sub.separator()

    sub.operator("ui.ml_active_favourite_modifier_move_up", icon='TRIA_UP', text="")
    sub.operator("ui.ml_active_favourite_modifier_move_down", icon='TRIA_DOWN', text="")

    sub.separator(factor=2)

    sub.operator("wm.ml_sort_favourite_modifiers", icon="SORTALPHA", text="")


def pin_object_button(context, layout):
    ml_pinned_ob = context.scene.modifier_list.pinned_object
    unpin = True if ml_pinned_ob else False
    icon = 'PINNED' if ml_pinned_ob else 'UNPINNED'
    layout.operator("ui.ml_object_pin", text="", icon=icon, emboss=False).unpin = unpin
