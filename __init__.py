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
    "name": "Modifier List",
    "author": "Antti Tikka",
    "version": (1, 7, 0),
    "blender": (2, 81, 0),
    "location": "Properties Editor & View3D > Sidebar & View3D > Alt + Spacebar",
    "description": "Alternative UI layout for modifiers with handy features "
                   "+ a Sidebar tab and a popup.",
    "warning": "Development version",
    "wiki_url": "https://github.com/Symstract/modifier_list",
    "category": "3D View"
}


import bpy


modules_to_ignore = (
    "properties",
)

classes_to_ignore = (
    "DATA_PT_modifiers",
)

panel_order = (
    "VIEW3D_PT_ml_modifiers",
    "VIEW3D_PT_ml_vertex_groups",
)


addon_keymaps = []


def register():
    from .addon_registration import register_bl_classes, call_register

    register_bl_classes("modules", modules_to_ignore=modules_to_ignore,
                        classes_to_ignore=classes_to_ignore, panel_order=panel_order,
                        addon_name_for_counter=bl_info["name"])

    call_register("modules")

    # === Keymap ===
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("view3d.modifier_popup", 'SPACE', 'PRESS', alt=True)
        addon_keymaps.append((km, kmi))


def unregister():
    # === Keymap ===
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    from .addon_registration import unregister_bl_classes, call_unregister

    call_unregister("modules")

    unregister_bl_classes(addon_name_for_counter=bl_info["name"])
