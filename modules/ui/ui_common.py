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
    prefs = context.preferences.addons["modifier_list"].preferences
    attrs = (attr for attr in dir(prefs) if attr.startswith("modifier_"))

    row = layout.row()
    row.alignment = 'RIGHT'
    row.operator("wm.ml_sort_favourite_modifiers", icon="SORTALPHA", text="")

    # layout.separator()

    col = layout.column(align=True)

    # Draw 2 or 3 property searches per row
    for attr in attrs:
        row = col.row(align=True)
        row.prop_search(prefs, attr, ml_props, "mesh_modifiers", text="", icon='MODIFIER')
        row.prop_search(prefs, next(attrs), ml_props, "mesh_modifiers", text="", icon='MODIFIER')
        if prefs.favourites_per_row == '3':
            row.prop_search(prefs, next(attrs), ml_props, "mesh_modifiers",
                            text="", icon='MODIFIER')


def pin_object_button(context, layout):
    ml_pinned_ob = context.scene.modifier_list.pinned_object
    unpin = True if ml_pinned_ob else False
    icon = 'PINNED' if ml_pinned_ob else 'UNPINNED'
    layout.operator("ui.ml_object_pin", text="", icon=icon, emboss=False).unpin = unpin
