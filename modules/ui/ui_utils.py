def favourite_modifiers_selection_layout(context, layout):
    wm = context.window_manager
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
        row.prop_search(prefs, attr, wm, "ml_mesh_modifiers", text="", icon='MODIFIER')
        row.prop_search(prefs, next(attrs), wm, "ml_mesh_modifiers", text="", icon='MODIFIER')
        if prefs.favourites_per_row == '3':
            row.prop_search(prefs, next(attrs), wm, "ml_mesh_modifiers", text="", icon='MODIFIER')


def pin_object_button(context, layout):
    scene = context.scene
    unpin = True if scene.ml_pinned_object else False
    icon = 'PINNED' if scene.ml_pinned_object else 'UNPINNED'
    layout.operator("ui.ml_object_pin", text="", icon=icon, emboss=False).unpin = unpin
