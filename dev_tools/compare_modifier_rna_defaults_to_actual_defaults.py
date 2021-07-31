"""For some reason some modifier properties' RNA defaults are different
than the actual initial values the modifier has when it's added. This
script can be run in Blender to compare them and get a dictionary of the
actual defaults that don't match the RNA defaults.

Bacause this is intended to be used for the modifier defaults feature,
collection, pointer and string properties are ignored.
"""


import sys
from pathlib import Path
from pprint import pprint

import bpy
from mathutils import Vector

# Make importing addon modules work (need to use absolute imports)
sys.path.append(str(Path(__file__).resolve().parents[1]))

from modules import modifier_categories
from modules.preferences import MODIFIER_CLASS_MAP


def get_modifier_settings_rna_defaults():
    defaults = {}

    for identifier, class_name in MODIFIER_CLASS_MAP.items():
        cls = getattr(bpy.types, class_name)
        get_modifier_settings_rna_defaults_for_modifier(identifier, cls, defaults)

    return defaults


def get_modifier_settings_rna_defaults_for_modifier(identifier, cls, defaults_dict):
    attrs_to_filter = {
        "show_render",
        "show_viewport",
        "show_in_editmode",
        "show_on_cage",
        "use_apply_on_spline",
        "show_expanded",
        "is_active",
        "debug_options"
    }
    all_mod_attrs = cls.bl_rna.properties.values()
    mod_settings = [attr for attr in all_mod_attrs
                    if attr.identifier not in attrs_to_filter
                    and not attr.identifier.startswith("_")]

    for setting in mod_settings:
        if setting.is_readonly:
            continue

        prop_class_name = type(setting).__name__

        if prop_class_name in {"CollectionProperty", "PointerProperty", "StringProperty"}:
            continue

        if prop_class_name == "EnumProperty" and setting.is_enum_flag:
            default = setting.default_flag
        elif hasattr(setting, "is_array") and setting.is_array:
            default = list(setting.default_array)
        else:
            default = setting.default

        defaults = defaults_dict.setdefault(identifier, {})
        defaults[setting.identifier] = default


def compare_modifier_defaults(object, modifier_types, rna_defaults_per_modifier):
    """Compares modifier properties' RNA defaults to the actual defaults
    for all modifiers in modifier_types and returns the actual defaults
    that don't match the RNA defaults per modifier.
    """
    actual_defaults_not_matching_rna_per_modifier = {}

    for identifier, defaults in rna_defaults_per_modifier.items():
        if identifier not in modifier_types:
            continue

        mod = object.modifiers.new(identifier, identifier)

        for key, value in defaults.items():
            defaults_match = True
            actual_default = getattr(mod, key)

            if isinstance(actual_default, Vector):
                if (actual_default - Vector(value)).length > 0.0001:
                    defaults_match = False
            elif isinstance(actual_default, float):
                if actual_default - value > 0.0001:
                    defaults_match = False
            elif type(actual_default).__name__ == "bpy_prop_array":
                actual_default_as_list = list(actual_default)
                if isinstance(actual_default_as_list[0], float):
                    if (Vector(actual_default_as_list) - Vector(value)).length > 0.0001:
                        defaults_match = False
                elif isinstance(actual_default_as_list[0], bool):
                   if actual_default_as_list != value:
                       defaults_match = False
            elif getattr(mod, key) != value:
                defaults_match = False

            if not defaults_match:
                if type(actual_default).__name__ == "bpy_prop_array":
                    actual_default = list(actual_default)
                actual_defaults_not_matching_rna_per_modifier.setdefault(
                    identifier, {})[key] = actual_default

        object.modifiers.remove(mod)

    return actual_defaults_not_matching_rna_per_modifier


def compare_mesh_modifier_defaults(rna_defaults_per_modifier):
    modifier_types = {mod[2] for mod in modifier_categories.MESH_ALL_NAMES_ICONS_TYPES}

    mesh = bpy.data.meshes.new("mesh")
    ob = bpy.data.objects.new("mesh", mesh)

    actual_defaults = compare_modifier_defaults(ob, modifier_types, rna_defaults_per_modifier)

    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(mesh)

    return actual_defaults


def compare_volume_modifier_defaults(rna_defaults_per_modifier):
    modifier_types = {mod[2] for mod in modifier_categories.VOLUME_ALL_NAMES_ICONS_TYPES}

    volume = bpy.data.volumes.new("volume")
    ob = bpy.data.objects.new("volume", volume)

    actual_defaults = compare_modifier_defaults(ob, modifier_types, rna_defaults_per_modifier)

    bpy.data.objects.remove(ob)
    bpy.data.volumes.remove(volume)

    return actual_defaults


def main():
    rna_defaults_per_modifier = get_modifier_settings_rna_defaults()

    print("Mesh modifier defaults not matching rna defaults per modifier:")
    pprint(compare_mesh_modifier_defaults(rna_defaults_per_modifier))

    print()

    print("Volume modifier defaults not matching rna defaults per modifier:")
    pprint(compare_volume_modifier_defaults(rna_defaults_per_modifier))

    print()


if __name__ == "__main__":
    main()
