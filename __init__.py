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
    "version": (1, 7, 4),
    "blender": (2, 92, 0),
    "location": "Properties Editor & View3D > Sidebar & View3D > Alt + Spacebar",
    "description": "Alternative UI layout for modifiers with handy features "
                   "+ a Sidebar tab and a popup.",
    "warning": "",
    "doc_url": "https://github.com/Symstract/modifier_list",
    "category": "3D View"
}


import bpy

from . import addon_registration


# register_bl_classes arguments

modules_to_ignore = (
    "preferences",
    "properties",
)

classes_to_ignore = (
    "DATA_PT_modifiers",
)

panel_order = (
    "VIEW3D_PT_ml_modifiers",
    "VIEW3D_PT_ml_vertex_groups",
)

# call_register arguments

module_order = (
    "preferences",
)


addon_keymaps = []


def register():
    addon_registration.import_modules("modules")
    addon_registration.register_bl_classes(modules_to_ignore=modules_to_ignore,
                                           classes_to_ignore=classes_to_ignore,
                                           panel_order=panel_order,
                                           addon_name_for_counter=bl_info["name"])
    addon_registration.call_register(module_order=module_order)

    # === Keymap ===
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("view3d.modifier_popup", 'SPACE', 'PRESS', alt=True)
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Property Editor', space_type='PROPERTIES')
        kmi = km.keymap_items.new("object.ml_modifier_add_from_search", 'A', 'PRESS', ctrl=True,
                                  shift=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("object.ml_modifier_add_from_menu", 'A', 'PRESS', shift=True)
        addon_keymaps.append((km, kmi))


def unregister():
    # === Keymap ===
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    addon_registration.call_unregister(module_order=reversed(module_order))
    addon_registration.unregister_bl_classes(addon_name_for_counter=bl_info["name"])
