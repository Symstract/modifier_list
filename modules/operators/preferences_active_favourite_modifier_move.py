import bpy
from bpy.props import *
from bpy.types import Operator


from ..utils import get_favourite_modifiers


class FavouriteModifierMoveBase:
    def execute(self, context):
        ml_props = context.window_manager.modifier_list
        active_index = ml_props.active_favourite_modifier_slot_index
        new_index = active_index - 1 if self.direction == 'UP' else active_index + 1

        prefs = context.preferences.addons["modifier_list"].preferences
        favourites_dict = get_favourite_modifiers()
        fav_mod_attr_names = list(favourites_dict.keys())
        fav_mods = list(favourites_dict.values())
        fav_mods.insert(new_index, fav_mods.pop(active_index))

        for i, mod in enumerate(fav_mods):
            setattr(prefs, fav_mod_attr_names[i], mod)

        ml_props.active_favourite_modifier_slot_index = new_index

        return {'FINISHED'}


class UI_OT_ml_active_favourite_modifier_move_up(Operator, FavouriteModifierMoveBase):
    bl_idname = "ui.ml_active_favourite_modifier_move_up"
    bl_label = "Move Active Favourite Modifier Up"
    bl_description = "Move the active favourite modifier up"
    bl_options = {'INTERNAL'}

    direction = 'UP'

    @ classmethod
    def poll(cls, context):
        ml_props = context.window_manager.modifier_list
        return ml_props.active_favourite_modifier_slot_index > 0


class UI_OT_ml_active_favourite_modifier_move_down(Operator, FavouriteModifierMoveBase):
    bl_idname = "ui.ml_active_favourite_modifier_move_down"
    bl_label = "Move Active Favourite Modifier Down"
    bl_description = "Move the active favourite modifier down"
    bl_options = {'INTERNAL'}

    direction = 'DOWN'

    @ classmethod
    def poll(cls, context):
        ml_props = context.window_manager.modifier_list
        return ml_props.active_favourite_modifier_slot_index < len(get_favourite_modifiers()) - 1
