import bpy
from bpy.props import *
from bpy.types import Operator


from ..utils import get_favourite_modifiers


class UI_OT_ml_favourite_modifier_toggle(Operator):
    bl_idname = "ui.ml_favourite_modifier_toggle"
    bl_label = "Toggle Favourite Modifier"
    bl_description = "Toggle a favourite modifier"
    bl_options = {'INTERNAL'}

    modifier: StringProperty()

    def execute(self, context):
        prefs = context.preferences.addons["modifier_list"].preferences
        ml_props = context.window_manager.modifier_list
        active_index = ml_props.active_favourite_modifier_slot_index

        favourites_dict = get_favourite_modifiers()
        fav_mod_attr_names = list(favourites_dict.keys())
        mods = list(favourites_dict.values())

        # Remove favourite
        if self.modifier in mods:
            mods.remove(self.modifier)
            mods.insert(-1, "")
            if active_index > 0:
                ml_props.active_favourite_modifier_slot_index = active_index - 1
        else:
            # No space for new favourite
            if all(mods):
                return {'CANCELLED'}
            # Add new favourite to active slot
            if not mods[active_index]:
                mods[active_index] = self.modifier
            # Add new favourite to next slot
            else:
                mods.insert(active_index + 1, self.modifier)
                mods.reverse()
                mods.remove("")
                mods.reverse()
                if active_index < len(mods) - 1:
                    ml_props.active_favourite_modifier_slot_index = active_index + 1

        # Sort favourites
        if prefs.auto_sort_favourites_when_choosing_from_menu:
            mods = list(filter(None, mods))
            mods.sort()
            mods.extend(["" for _ in range(len(favourites_dict) - len(mods))])
            if self.modifier in mods:
                ml_props.active_favourite_modifier_slot_index = mods.index(self.modifier)
        
        for i, mod in enumerate(mods):
            setattr(prefs, fav_mod_attr_names[i], mod)

        return {'FINISHED'}
