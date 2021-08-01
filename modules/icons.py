import os

import bpy
from bpy.utils import previews


_preview_collections = {}


def get_icons():
    """Returns the preview collection containing all icons."""
    return _preview_collections["main"]


def load_icons():
    """Loads/reloads icons from the icons directory.

    This is also used in a callback function in addon preferences, which
    makes changing icon color possible without reloading the addon.
    """
    # === Remove the current icons and clear preview_collections ===
    for pcoll in _preview_collections.values():
        previews.remove(pcoll)

    _preview_collections.clear()

    # === Load new icons ===
    pcoll = previews.new()

    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    color = prefs.icon_color

    icons_dir = os.path.join(os.path.dirname(__file__), os.path.pardir, "icons", color)
    icons_dir_files = os.listdir(icons_dir)

    all_icon_files = [icon for icon in icons_dir_files if icon.endswith(".png")]
    all_icon_names = [icon[0:-4] for icon in all_icon_files]
    all_icon_files_and_names = zip(all_icon_names, all_icon_files)

    for icon_name, icon_file in all_icon_files_and_names:
        pcoll.load(icon_name, os.path.join(icons_dir, icon_file), 'IMAGE')

    _preview_collections["main"] = pcoll


def register():
    load_icons()


def unregister():
    for pcoll in _preview_collections.values():
        previews.remove(pcoll)
    _preview_collections.clear()
