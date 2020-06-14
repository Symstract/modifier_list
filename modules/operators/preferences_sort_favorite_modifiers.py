from bpy.types import Operator

from ..modifier_categories import get_favourite_modifiers_names


class WM_OT_ml_sort_favourite_modifiers(Operator):
    bl_idname = "wm.ml_sort_favourite_modifiers"
    bl_label = "Sort Favourite Modifiers"
    bl_description = "Sort the favourite modifiers. Also removes empty slots between favourites"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        prefs = context.preferences.addons["modifier_list"].preferences
        fav_mod_attr_names = [("modifier_" + str(i).zfill(2)) for i in range(1, 13)]
        mods = [getattr(prefs, attr) for attr in fav_mod_attr_names if getattr(prefs, attr)]
        mods.sort()

        for attr in fav_mod_attr_names:
            setattr(prefs, attr, "")

        for i, mod in enumerate(mods):
            setattr(prefs, fav_mod_attr_names[i], mod)

        return {'FINISHED'}
