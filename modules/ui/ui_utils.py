def pin_object_button(context, layout):
    wm = context.window_manager
    unpin = True if wm.ml_pinned_object else False
    icon = 'PINNED' if wm.ml_pinned_object else 'UNPINNED'
    layout.operator("ui.ml_object_pin", text="", icon=icon, emboss=False).unpin = unpin