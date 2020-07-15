from bpy.types import Operator

from ..utils import get_favourite_modifiers


class WM_OT_ml_sort_favourite_modifiers(Operator):
    bl_idname = "wm.ml_sort_favourite_modifiers"
    bl_label = "Sort Favourite Modifiers"
    bl_description = "Sort the favourite modifiers. Also removes empty slots between favourites"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        prefs = context.preferences.addons["modifier_list"].preferences
        favourites_dict = get_favourite_modifiers()
        fav_mod_attr_names = list(favourites_dict.keys())
        mods = list(filter(None, favourites_dict.values()))
        mods.sort()
        mods.extend(["" for _ in range(len(favourites_dict) - len(mods))])

        for i, mod in enumerate(mods):
            setattr(prefs, fav_mod_attr_names[i], mod)

        return {'FINISHED'}
