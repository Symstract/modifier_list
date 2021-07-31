import pytest

import bpy
from mathutils import Vector

from ...modules import modifier_categories


ADDON_PREFERENCES = bpy.context.preferences.addons["modifier_list"].preferences
ALL_MODIFIER_TYPES = [mod[2] for mod in modifier_categories.ALL_MODIFIERS_NAMES_ICONS_TYPES]
MESH_MODIFIER_TYPES = [mod[2] for mod in modifier_categories.MESH_ALL_NAMES_ICONS_TYPES]
VOLUME_MODIFIER_TYPES = [mod[2] for mod in modifier_categories.VOLUME_ALL_NAMES_ICONS_TYPES]


@pytest.fixture(scope="module")
def mesh_object():
    meshes = bpy.data.meshes
    obs = bpy.data.objects
    mesh = meshes.new(name="mesh")
    ob = obs.new("mesh", mesh)
    yield ob

    obs.remove(ob)
    meshes.remove(mesh)


@pytest.fixture(scope="module")
def volume_object():
    volumes = bpy.data.volumes
    obs = bpy.data.objects
    volume = volumes.new("volume")
    ob = obs.new("volume", volume)
    yield ob

    obs.remove(ob)
    volumes.remove(volume)


@pytest.fixture(scope="module")
def modifier_defaults_per_modifier():
    defaults_per_modifier = {}

    # For some modifiers, a different setting is shown for different
    # modes, e.g. when Simple Deform has deform_method set to 'TWIST' or
    # 'BEND', angle setting is shown, and when it's set to 'TAPER' or
    # 'STRETCH', it shows a factor setting. Those settings are, for some
    # reason, synched, so setting the other one would override the first
    # one. These cases are not handled here but they are handled in the
    # Add Modifier operator, so the overriding settings are ignored
    # here.
    settings_to_ignore_per_modifier = {
        "BEVEL": {"width_pct"},
        "SIMPLE_DEFORM": {"factor"}
    }

    for mod_type in ALL_MODIFIER_TYPES:
        defaults_group = getattr(ADDON_PREFERENCES.modifier_defaults, mod_type)

        defaults = {}

        cur_float_addition = 0.1
        cur_int_addition = 1

        for setting_identifier in defaults_group.__annotations__:
            setting = defaults_group.bl_rna.properties[setting_identifier]

            if mod_type in settings_to_ignore_per_modifier.keys():
                if setting.identifier in settings_to_ignore_per_modifier[mod_type]:
                    continue

            prop_class_name = type(setting).__name__

            if prop_class_name == "EnumProperty":
                enum_identifiers = [s.identifier for s in setting.enum_items.values()]
                if setting.is_enum_flag:
                    default = set(enum_identifiers) - setting.default_flag
                else:
                    enum_identifiers_without_default = [identifier
                                                        for identifier in enum_identifiers
                                                        if identifier != setting.default]
                    default = enum_identifiers_without_default[0]
            elif prop_class_name == "FloatProperty":
                if setting.is_array:
                    default = [min(value + cur_float_addition, setting.hard_max)
                               for value in setting.default_array]
                else:
                    default = min(setting.default + cur_float_addition, setting.hard_max)
                cur_float_addition += 0.1
            elif prop_class_name == "IntProperty":
                if setting.is_array:
                    default = [min(value + cur_int_addition, setting.hard_max)
                               for value in setting.default_array]
                else:
                    default = min(setting.default + cur_int_addition, setting.hard_max)
                cur_int_addition += 1
            elif prop_class_name == "BoolProperty":
                if setting.is_array:
                    default = [not bool for bool in setting.default_array]
                else:
                    default = not setting.default

            defaults[setting.identifier] = default

        defaults_per_modifier[mod_type] = defaults

    return defaults_per_modifier


@pytest.fixture(params=MESH_MODIFIER_TYPES)
def mesh_modifier_with_defaults_and_defaults(request, mesh_object, modifier_defaults_per_modifier):
    mod_type = request.param
    mod = mesh_object.modifiers.new(mod_type, mod_type)
    defaults = modifier_defaults_per_modifier[mod_type]

    for key, value in defaults.items():
        setattr(mod, key, value)

    yield mod, defaults

    mesh_object.modifiers.remove(mod)


@pytest.fixture(params=VOLUME_MODIFIER_TYPES)
def volume_modifier_with_defaults_and_defaults(request, volume_object,
                                               modifier_defaults_per_modifier):
    mod_type = request.param
    mod = volume_object.modifiers.new(mod_type, mod_type)
    defaults = modifier_defaults_per_modifier[mod_type]

    for key, value in defaults.items():
        setattr(mod, key, value)

    yield mod, defaults

    volume_object.modifiers.remove(mod)


def assert_modifier_defaults(modifier, defaults):
    for identifier, expected_value in defaults.items():
        actual_value = getattr(modifier, identifier)

        prop_id_str = f"Property: {identifier}"

        if isinstance(actual_value, Vector):
            message = f"{prop_id_str}, ({actual_value} - {Vector(expected_value)}).length < 0.0001"
            assert (actual_value - Vector(expected_value)).length < 0.0001, message
            continue

        if isinstance(actual_value, float):
            message = f"{prop_id_str}, {actual_value} - {expected_value} < 0.0001"
            assert actual_value - expected_value < 0.0001, message
            continue

        if type(actual_value).__name__ == "bpy_prop_array":
            actual_value = list(actual_value)
            if isinstance(actual_value[0], float):
                message = (f"{prop_id_str}, (Vector({actual_value}) - Vector({expected_value})"
                           ".length < 0.0001")
                assert (Vector(actual_value) - Vector(expected_value)).length < 0.0001, message
            elif isinstance(actual_value[0], bool):
                message = f"{prop_id_str}, {actual_value} == {expected_value}"
                assert actual_value == expected_value, message
            continue

        message = f"{prop_id_str}, {getattr(modifier, identifier)} == {expected_value}"
        assert getattr(modifier, identifier) == expected_value, message


def test_mesh_modifier_default_settings(mesh_modifier_with_defaults_and_defaults):
    assert_modifier_defaults(*mesh_modifier_with_defaults_and_defaults)


def test_volume_modifier_default_settings(volume_modifier_with_defaults_and_defaults):
    assert_modifier_defaults(*volume_modifier_with_defaults_and_defaults)
