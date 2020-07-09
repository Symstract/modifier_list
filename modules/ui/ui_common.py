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
    ml_props = context.window_manager.modifier_list
    active_slot_index = ml_props.active_favourite_modifier_slot_index
    prefs = context.preferences.addons["modifier_list"].preferences
    attrs = [attr for attr in dir(prefs) if attr.startswith("modifier_")]

    row = layout.row()
    row.alignment = 'LEFT'
    row.operator("wm.ml_sort_favourite_modifiers", icon="SORTALPHA", text="Sort")

    row = layout.row()

    col = row.column(align=True)

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


def pin_object_button(context, layout):
    ml_pinned_ob = context.scene.modifier_list.pinned_object
    unpin = True if ml_pinned_ob else False
    icon = 'PINNED' if ml_pinned_ob else 'UNPINNED'
    layout.operator("ui.ml_object_pin", text="", icon=icon, emboss=False).unpin = unpin
