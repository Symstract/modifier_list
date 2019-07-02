import os

import bpy
from bpy.utils import previews


preview_collections = {}


def load_icons():
    global preview_collections

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

    preview_collections["main"] = pcoll


def reload_icons(self, context):
    """Callback function for addon preferences that makes changing icon
    color possible without reloading the addon.
    """
    for pcoll in preview_collections.values():
        previews.remove(pcoll)
    preview_collections.clear()

    load_icons()


def register():
    load_icons()


def unregister():
    for pcoll in preview_collections.values():
        previews.remove(pcoll)
    preview_collections.clear()
