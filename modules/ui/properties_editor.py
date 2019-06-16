import bpy
from bpy.types import Panel
from bl_ui.properties_data_modifier import DATA_PT_modifiers as original_DATA_PT_modifiers

from .modifiers_ui import modifiers_ui
from ..utils import get_ml_active_object


class DATA_PT_modifiers(Panel):
    bl_label = "Modifiers"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "modifier"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        ob = get_ml_active_object()
        if ob is not None:
            return ob.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'LATTICE'}
        return False

    def draw(self, context):
        layout = self.layout
        modifiers_ui(context, layout)


def register_DATA_PT_modifiers(self, context):
    """Callback function for enabling/disabling Modifier List layout
    in properties panel.
    """
    from bpy.utils import register_class, unregister_class

    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    use_properties_editor = prefs.use_properties_editor

    if use_properties_editor:
        register_class(DATA_PT_modifiers)
    else:
        try:
            unregister_class(DATA_PT_modifiers)
            register_class(original_DATA_PT_modifiers)
        except RuntimeError:
            pass


def register():
    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    use_properties_editor = prefs.use_properties_editor

    if use_properties_editor:
        from bpy.utils import register_class

        register_class(DATA_PT_modifiers)


def unregister():
    from bpy.utils import unregister_class

    try:
        unregister_class(DATA_PT_modifiers)
    except RuntimeError:
        pass