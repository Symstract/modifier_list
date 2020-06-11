def pin_object_button(context, layout):
    scene = context.scene
    unpin = True if scene.ml_pinned_object else False
    icon = 'PINNED' if scene.ml_pinned_object else 'UNPINNED'
    layout.operator("ui.ml_object_pin", text="", icon=icon, emboss=False).unpin = unpin
