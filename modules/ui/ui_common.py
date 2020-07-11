from .. import modifier_categories


def box_with_header(layout, text, expand_data, expand_prop):
    """Template for a header for boxes used as panels.
    
    Includes a triangle icon whose state is defined by expand_prop, a
    property of expand_data.

    Returns a box.
    """
    box = layout.box()

    row = box.row()
    icon = 'TRIA_DOWN' if getattr(expand_data, expand_prop) else 'TRIA_RIGHT'
    row.prop(expand_data, expand_prop, icon=icon, text="", emboss=False)
    row.label(text=text)

    return box


def favourite_modifiers_selection_layout(context, layout):
    prefs = context.preferences.addons["modifier_list"].preferences
    ml_props = context.window_manager.modifier_list

    # === Modifier menu ===
    
    box = box_with_header(layout, "Menu", ml_props.preferences_ui_props,
                          "favourite_modifiers_menu_expand")

    if ml_props.preferences_ui_props.favourite_modifiers_menu_expand:
        box.prop(ml_props, "auto_sort_favourites_when_choosing_from_menu")

        box.separator()

        row = box.row()
        row.alignment = 'LEFT'

        fav_mod_attr_names = [("modifier_" + str(i).zfill(2)) for i in range(1, 13)]
        mods = [getattr(prefs, attr) for attr in fav_mod_attr_names]

        col = row.column(align=True)
        col.label(text="Modify")
        col.separator(factor=0.3)
        for name, icon, _ in modifier_categories.MESH_MODIFY_NAMES_ICONS_TYPES:
            col.operator("ui.ml_favourite_modifier_toggle", text=name, icon=icon,
                        depress=name in mods).modifier = name

        col = row.column(align=True)
        col.label(text="Generate")
        col.separator(factor=0.3)
        for name, icon, _ in modifier_categories.MESH_GENERATE_NAMES_ICONS_TYPES:
            col.operator("ui.ml_favourite_modifier_toggle", text=name, icon=icon,
                        depress=name in mods).modifier = name

        col = row.column(align=True)
        col.label(text="Deform")
        col.separator(factor=0.3)
        for name, icon, _ in modifier_categories.MESH_DEFORM_NAMES_ICONS_TYPES:
            col.operator("ui.ml_favourite_modifier_toggle", text=name, icon=icon,
                        depress=name in mods).modifier = name

        col = row.column(align=True)
        col.label(text="Simulate")
        col.separator(factor=0.3)
        for name, icon, _ in modifier_categories.MESH_SIMULATE_NAMES_ICONS_TYPES:
            col.operator("ui.ml_favourite_modifier_toggle", text=name, icon=icon,
                        depress=name in mods).modifier = name
        
        layout.separator()

    row = layout.row()

    col = row.column(align=True)

    active_slot_index = ml_props.active_favourite_modifier_slot_index
    attrs = [attr for attr in dir(prefs) if attr.startswith("modifier_")]

    # Draw 2 or 3 property searches per row
    for i, attr in enumerate(attrs):
        if (i == 0 or (prefs.favourites_per_row == '2' and i % 2 == 0)
                or (prefs.favourites_per_row == '3' and i % 3 == 0)):
            split = col.split(align=True)
        
        sub_row = split.row(align=True)
        icon = 'LAYER_ACTIVE' if i == active_slot_index else 'LAYER_USED'
        sub_row.operator("ui.ml_active_favourite_modifier_slot_set", icon=icon, text="",
                         emboss=False).index = i
        sub_row.prop_search(prefs, attr, ml_props, "mesh_modifiers", text="", icon='MODIFIER')

    sub = row.column(align=True)

    sub.operator("ui.ml_active_favourite_modifier_move_up", icon='TRIA_UP', text="")
    sub.operator("ui.ml_active_favourite_modifier_move_down", icon='TRIA_DOWN', text="")

    sub.separator(factor=3)

    sub.operator("wm.ml_sort_favourite_modifiers", icon="SORTALPHA", text="")


def pin_object_button(context, layout):
    ml_pinned_ob = context.scene.modifier_list.pinned_object
    unpin = True if ml_pinned_ob else False
    icon = 'PINNED' if ml_pinned_ob else 'UNPINNED'
    layout.operator("ui.ml_object_pin", text="", icon=icon, emboss=False).unpin = unpin
