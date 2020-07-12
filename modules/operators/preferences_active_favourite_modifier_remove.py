from bpy.types import Operator

from ..utils import get_favourite_modifiers


class WM_OT_ml_active_favourite_modifier_remove(Operator):
    bl_idname = "ui.ml_active_favourite_modifier_remove"
    bl_label = "Remove Active Favourite Modifier"
    bl_description = "Remove the active favourite modifer"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        prefs = context.preferences.addons["modifier_list"].preferences
        ml_props = context.window_manager.modifier_list
        active_index = ml_props.active_favourite_modifier_slot_index
        
        favourites_dict = get_favourite_modifiers()
        fav_mod_attr_names = list(favourites_dict.keys())
        
        fav_mods = list(favourites_dict.values())
        fav_mods.pop(active_index)
        fav_mods.insert(-1, "")

        for i, mod in enumerate(fav_mods):
            setattr(prefs, fav_mod_attr_names[i], mod)

        ml_props.active_favourite_modifier_slot_index = active_index - 1 if active_index > 0 else 0

        return {'FINISHED'}
