# Copyright (C) 2019 Antti Tikka

# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK *****


bl_info = {
    "name": "Modifier Popup Panel",
    "author": "Antti Tikka",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "View 3D -> Alt + Spacebar",
    "description": "A handy popup panel for showing modifiers in 3D view",
    "warning": "1.1 development version",
    "wiki_url": "https://github.com/Symstract/Modifier-Popup-Panel/tree/2.8",
    "category": "3D View"
}


if "bpy" in locals():
    import importlib
    importlib.reload(modifiers_ui)
    importlib.reload(main_ui_popup)
else:
    from .modules.modifiers import modifiers_ui
    from .modules import main_ui_popup

import os

import bpy
from bpy.app.handlers import persistent
from bpy.props import *


def set_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    all_modifiers = bpy.context.window_manager.all_modifiers

    if not all_modifiers:
        for name, icon, mod in modifiers_ui.all_name_icon_type():
            item = all_modifiers.add()
            item.name = name
            item.value = mod


@persistent
def on_file_load(dummy):
    set_modifier_collection_items()


addon_keymaps = []

preview_collections = {}


def register():
    print("register called")
    from .addon_registration import register_bl_classes
    register_bl_classes("modules", addon_name=bl_info["name"])

    # === Properties ===
    bpy.types.Object.modifier_active_index = IntProperty()

    # Use Window Manager for storing modifier search property
    # and modifier collection because it can be accessed on
    # registering and it's not scene specific.
    wm = bpy.types.WindowManager
    wm.mod_to_add = StringProperty(name="Modifier to add", update=modifiers_ui.add_modifier,
                                   description="Search for a modifier and add it to the stack")
    wm.all_modifiers = CollectionProperty(type=modifiers_ui.AllModifiersCollection)

    bpy.app.handlers.load_post.append(on_file_load)

    set_modifier_collection_items()

    # === Keymap ===
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(main_ui_popup.VIEW_3D_PT_modifier_popup.bl_idname, 'SPACE', 'PRESS', alt=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))

    # === Icons ===
    from bpy.utils import previews
    pcoll = previews.new()

    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    icons_dir_files = os.listdir(icons_dir)

    all_icon_files = [icon for icon in icons_dir_files if icon.endswith(".png")]
    all_icon_names = [icon[0:-4] for icon in all_icon_files]
    all_icon_files_and_names = zip(all_icon_names, all_icon_files)

    for icon_name, icon_file in all_icon_files_and_names:
        pcoll.load(icon_name, os.path.join(icons_dir, icon_file), 'IMAGE')

    preview_collections["main"] = pcoll


def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    from .addon_registration import unregister_bl_classes
    unregister_bl_classes(addon_name=bl_info["name"])

    bpy.app.handlers.load_post.remove(on_file_load)

    del bpy.types.Object.modifier_active_index

