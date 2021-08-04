import json
import math
import os

import bpy
# import rna_keymap_ui
from bpy.props import *
from bpy.types import AddonPreferences, PropertyGroup
from mathutils import Vector

from .icons import load_icons
from .modifier_categories import ALL_MODIFIERS_NAMES_ICONS_TYPES
from .ui.properties_editor import register_DATA_PT_modifiers
from .ui.ui_common import box_with_header, favourite_modifiers_configuration_layout
from .ui.sidebar import update_sidebar_category


# Property reading
# ======================================================================

def ensure_valid_read_value(value):
    if isinstance(value, list):
        if not value or isinstance(value[0], str):
            return set(value)
    elif isinstance(value, dict) and value["type"] == "Vector":
        return Vector(value["value"])

    return value


def fill_prefs(prefs_dict, prefs):
    for prop in prefs_dict.keys():
        if prop not in prefs.__annotations__:
            continue

        prop_in_prefs = getattr(prefs, prop)

        if isinstance(prop_in_prefs, PropertyGroup):
            fill_prefs(prefs_dict[prop], prop_in_prefs)
        else:
            setattr(prefs, prop, ensure_valid_read_value(prefs_dict[prop]))


def read_prefs(prefs_file):
    """Read preferences from a json"""
    if not os.path.exists(prefs_file) or not prefs_file.endswith(".json"):
        return

    with open(prefs_file) as f:
        try:
            prefs_dict = json.load(f)
        except json.decoder.JSONDecodeError:
            return

    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    fill_prefs(prefs_dict, prefs)


# Property writing
# ======================================================================

def ensure_valid_write_value(value):
    if isinstance(value, set):
        return list(value)
    elif isinstance(value, Vector):
        return {
            "type": "Vector",
            "value": value.to_tuple()
        }
    elif type(value).__name__ == "bpy_prop_array":
        return list(value)

    return value


def create_prefs_dict():
    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    prefs_dict = {}
    fill_prefs_dict(prefs, prefs_dict)
    return prefs_dict


def fill_prefs_dict(prefs, prefs_dict):
    for prop in prefs.__annotations__:
        prop_in_prefs = getattr(prefs, prop)
        if isinstance(prop_in_prefs, PropertyGroup):
            prefs_dict[prop] = {}
            fill_prefs_dict(prop_in_prefs, prefs_dict[prop])
        else:
            prefs_dict[prop] = ensure_valid_write_value(prop_in_prefs)


def write_prefs():
    """Write preferences into a json"""
    prefs_dict = create_prefs_dict()
    config_dir = bpy.utils.user_resource('CONFIG')
    ml_config_dir = os.path.join(config_dir, "modifier_list")

    if not os.path.exists(ml_config_dir):
        os.mkdir(ml_config_dir)

    prefs_file = os.path.join(ml_config_dir, "preferences.json")

    with open(prefs_file, 'w', encoding='utf-8') as f:
        json.dump(prefs_dict, f, ensure_ascii=False, indent=4)


# Callbacks
# ======================================================================

def use_properties_editor_callback(self, context):
    register_DATA_PT_modifiers(self, context)


def sidebar_category_callback(self, context):
    update_sidebar_category()


def icon_color_callback(self, context):
    load_icons()


# Modifier default settings
# ======================================================================

MODIFIER_CLASS_MAP = {
    "ARMATURE": "ArmatureModifier",
    "ARRAY": "ArrayModifier",
    "BEVEL": "BevelModifier",
    "BOOLEAN": "BooleanModifier",
    "BUILD": "BuildModifier",
    "CAST": "CastModifier",
    "CLOTH": "ClothModifier",
    "COLLISION": "CollisionModifier",
    "CORRECTIVE_SMOOTH": "CorrectiveSmoothModifier",
    "CURVE": "CurveModifier",
    "DATA_TRANSFER": "DataTransferModifier",
    "DECIMATE": "DecimateModifier",
    "DISPLACE": "DisplaceModifier",
    "DYNAMIC_PAINT": "DynamicPaintModifier",
    "EDGE_SPLIT": "EdgeSplitModifier",
    "EXPLODE": "ExplodeModifier",
    "FLUID": "FluidModifier",
    "HOOK": "HookModifier",
    "LAPLACIANDEFORM": "LaplacianDeformModifier",
    "LAPLACIANSMOOTH": "LaplacianSmoothModifier",
    "LATTICE": "LatticeModifier",
    "MASK": "MaskModifier",
    "MESH_CACHE": "MeshCacheModifier",
    "MESH_DEFORM": "MeshDeformModifier",
    "MESH_SEQUENCE_CACHE": "MeshSequenceCacheModifier",
    "MESH_TO_VOLUME": "MeshToVolumeModifier",
    "MIRROR": "MirrorModifier",
    "MULTIRES": "MultiresModifier",
    "NODES": "NodesModifier",
    "NORMAL_EDIT": "NormalEditModifier",
    "OCEAN": "OceanModifier",
    "PARTICLE_INSTANCE": "ParticleInstanceModifier",
    "PARTICLE_SYSTEM": "ParticleSystemModifier",
    "REMESH": "RemeshModifier",
    "SCREW": "ScrewModifier",
    "SHRINKWRAP": "ShrinkwrapModifier",
    "SIMPLE_DEFORM": "SimpleDeformModifier",
    "SKIN": "SkinModifier",
    "SMOOTH": "SmoothModifier",
    "SOFT_BODY": "SoftBodyModifier",
    "SOLIDIFY": "SolidifyModifier",
    "SUBSURF": "SubsurfModifier",
    "SURFACE_DEFORM": "SurfaceDeformModifier",
    "TRIANGULATE": "TriangulateModifier",
    "UV_PROJECT": "UVProjectModifier",
    "UV_WARP": "UVWarpModifier",
    "VERTEX_WEIGHT_EDIT": "VertexWeightEditModifier",
    "VERTEX_WEIGHT_MIX": "VertexWeightMixModifier",
    "VERTEX_WEIGHT_PROXIMITY": "VertexWeightProximityModifier",
    "VOLUME_DISPLACE": "VolumeDisplaceModifier",
    "VOLUME_TO_MESH": "VolumeToMeshModifier",
    "WARP": "WarpModifier",
    "WAVE": "WaveModifier",
    "WEIGHTED_NORMAL": "WeightedNormalModifier",
    "WELD": "WeldModifier",
    "WIREFRAME": "WireframeModifier"
}


# For some reason some modifier properties' RNA defaults are different
# than the actual initial values the modifier has when it's added, so
# these need to be listed here.
ACTUAL_MODIFIER_DEFAULTS_PER_MODIFIER = {
    "BEVEL": {
        "loop_slide": True,
        "use_clamp_overlap": True
    },
    "DATA_TRANSFER": {
        "data_types_edges": set(),
        "data_types_loops": set(),
        "data_types_polys": set(),
        "data_types_verts": set(),
        "mix_factor": 1.0
    },
    "DECIMATE": {"delimit": set()},
    "HOOK": {"matrix_inverse": (
                0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0
            )
    },
    "MESH_CACHE": {"flip_axis": set()},
    "MESH_SEQUENCE_CACHE": {"read_data": {'VERT', 'UV', 'POLY', 'COLOR'}},
    "MESH_TO_VOLUME": {
        "density": 1.0,
        "exterior_band_width": 0.1,
        "interior_band_width": 0.1,
        "use_fill_volume": True,
        "voxel_amount": 32,
        "voxel_size": 0.1
    },
    "MIRROR": {
        "use_axis": (True, False, False),
        "use_mirror_merge": True
    },
    "NORMAL_EDIT": {"use_direction_parallel": False},
    "SUBSURF": {"use_limit_surface": True},
    "VERTEX_WEIGHT_PROXIMITY": {
        "proximity_geometry": {'VERTEX'},
        "proximity_mode": 'OBJECT'
    },
    "VOLUME_DISPLACE": {
        "strength": 0.5,
        "texture_mid_level": (0.5, 0.5, 0.5),
        "texture_sample_radius": 1.0},
    "VOLUME_TO_MESH": {
        "threshold": 0.1,
        "voxel_amount": 32,
        "voxel_size": 0.1
    },
}


SETTINGS_TO_IGNORE_PER_MODIFIER = {
    "DATA_TRANSFER": {
        # These are enums whose items depend on the source object and
        # can't therefore be set beforehand. Or, actually, one of the
        # items in enum_items seems to be 'ACTIVE' but then it doesn't
        # seem to be a valid option for the modifier.
        "layers_vgroup_select_src",
        "layers_vcol_select_src",
        "layers_uv_select_src",
        # As with the settings above, these settings' enum_items also
        # include the option 'ACTIVE' but again it's not a valid option
        # to set for the modifier. Other options are 'NAME' and 'INDEX'
        # and the data layer names of the destination object. The
        # simplest thing is to just ignore these as well.
        "layers_vgroup_select_dst",
        "layers_vcol_select_dst",
        "layers_uv_select_dst",
        # For some reason, setting data_types_polys to any value
        # disables the 'UV' option in data_types_loops enum, so it has
        # to be ignored.
        "data_types_polys"
    },
    "HOOK": {
        # It shouldn't be useful to set a default for this, this isn't
        # even shown in the modifier's UI.
        "matrix_inverse"
    },
    "MULTIRES": {
        # levels, sculpt_levels or render_levels can't be set directly,
        # which wouldn't make sense anyway.
        "levels",
        "sculpt_levels",
        "render_levels"
    }
}


class ModifierDefaults(PropertyGroup):
    pass


def add_modifier_defaults_groups():
    modifier_defaults_groups = []

    ModifierDefaults.__annotations__ = dict()

    for identifier, class_name in MODIFIER_CLASS_MAP.items():
        specific_modifier_group = type(identifier + "_Defaults", (PropertyGroup,), {})
        modifier_defaults_groups.append(specific_modifier_group)
        ModifierDefaults.__annotations__[identifier] = PointerProperty(
            type=specific_modifier_group)
        cls = getattr(bpy.types, class_name)
        add_modifier_defaults_group_props(identifier, cls, specific_modifier_group)

    return modifier_defaults_groups


def add_modifier_defaults_group_props(identifier, cls, property_group):
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

    property_group.__annotations__ = dict()

    for setting in mod_settings:
        if setting.is_readonly:
            continue

        if identifier in SETTINGS_TO_IGNORE_PER_MODIFIER.keys():
            if setting.identifier in SETTINGS_TO_IGNORE_PER_MODIFIER[identifier]:
                continue

        prop_class_name = type(setting).__name__

        if prop_class_name in {"CollectionProperty", "PointerProperty", "StringProperty"}:
            continue

        kwargs = {
            "name": setting.name,
            "description": setting.description
        }

        if prop_class_name == "EnumProperty":
            enum_items = [(s.identifier, s.name, s.description, s.value)
                            for s in setting.enum_items.values()]
            kwargs["items"] = enum_items
            if setting.is_enum_flag:
                kwargs["options"] = {'ENUM_FLAG'}
                kwargs["default"] = setting.default_flag
            else:
                kwargs["default"] = setting.default
        elif prop_class_name in {"FloatProperty", "IntProperty"}:
            kwargs["min"] = setting.hard_min
            kwargs["max"] = setting.hard_max
            kwargs["soft_min"] = setting.soft_min
            kwargs["soft_max"] = setting.soft_max

            # Some modifier properties have a wrong subtype, which need
            # to be worked around. Also, even reading some would cause
            # warnings in the console.
            # https://developer.blender.org/T89213
            # Shrkinwrap's "offset" and "project_limit" and Warp's
            # "falloff_radius" have been fixed in Blender 3.0.
            if ((identifier == 'SHRINKWRAP' and setting.identifier in {"offset", "project_limit"})
                    or (identifier == 'WARP' and setting.identifier == "falloff_radius")):
                kwargs["subtype"] = 'DISTANCE'
            elif identifier == 'NORMAL_EDIT' and setting.identifier == "offset":
                kwargs["subtype"] = 'COORDINATES'
            elif not (identifier == 'OCEAN' and setting.identifier == "wind_velocity"):
                kwargs["subtype"] = setting.subtype

            if prop_class_name == "FloatProperty":
                kwargs["unit"] = setting.unit

        if hasattr(setting, "is_array") and setting.is_array:
            kwargs["size"] = setting.array_length
            kwargs["default"] = setting.default_array
            if prop_class_name == "FloatProperty":
                prop = FloatVectorProperty
            elif prop_class_name == "IntProperty":
                prop = IntVectorProperty
            elif prop_class_name == "BoolProperty":
                prop = BoolVectorProperty
        else:
            prop = getattr(bpy.props, prop_class_name)
            if prop_class_name != "EnumProperty":
                kwargs["default"] = setting.default

        # Override the RNA default with the actual default if they don't
        # match.
        if identifier in ACTUAL_MODIFIER_DEFAULTS_PER_MODIFIER.keys():
            actual_defaults = ACTUAL_MODIFIER_DEFAULTS_PER_MODIFIER[identifier]
            if setting.identifier in actual_defaults.keys():
                kwargs["default"] = actual_defaults[setting.identifier]

        property_group.__annotations__[setting.identifier] = prop(**kwargs)


# Preferences
# ======================================================================

class Preferences(AddonPreferences):
    bl_idname = "modifier_list"

    # === General settings ===
    use_sidebar: BoolProperty(
        name="Sidebar",
        description="Enable/disable the Sidebar tab",
        default=True)

    use_properties_editor: BoolProperty(
        name="Properties Editor",
        description="Enable/disable inside Properties Editor",
        default=True,
        update=use_properties_editor_callback)

    style_items = [
        ("LIST", "List", "", 1),
        ("STACK", "Stack", "", 2)
    ]

    properties_editor_style: EnumProperty(
        items=style_items,
        name="Properties Editor Style",
        description="Display modifiers inside Properties Editor as")

    sidebar_style: EnumProperty(
        items=style_items,
        name="Sidebar Style",
        description="Display modifiers inside the sidebar as")

    popup_style: EnumProperty(
        items=style_items,
        name="Popup Style",
        description="Display modifiers inside the popup as")

    keep_sidebar_visible: BoolProperty(
        name="Keep Sidebar Panels Visible",
        description="Keep the sidebar panels always visible")

    sidebar_category: StringProperty(
        name="Sidebar Category",
        default="Modifier List",
        update=sidebar_category_callback)

    favourites_per_row_items = [
        ("2", "2", "", 1),
        ("3", "3", "", 2)
    ]
    favourites_per_row: EnumProperty(
        items=favourites_per_row_items,
        name="Favourites Per Row",
        description="The number of favourites per row",
        default="2")

    auto_sort_favourites_when_choosing_from_menu: BoolProperty(
        name="Auto Sort Favourites When Choosing From Menu",
        description="Automatically sort favourite modifiers when choosing from the menu. "
                    "Also removes empty slots between favourites")

    modifier_01: StringProperty(description="Add a favourite modifier")
    modifier_02: StringProperty(description="Add a favourite modifier")
    modifier_03: StringProperty(description="Add a favourite modifier")
    modifier_04: StringProperty(description="Add a favourite modifier")
    modifier_05: StringProperty(description="Add a favourite modifier")
    modifier_06: StringProperty(description="Add a favourite modifier")
    modifier_07: StringProperty(description="Add a favourite modifier")
    modifier_08: StringProperty(description="Add a favourite modifier")
    modifier_09: StringProperty(description="Add a favourite modifier")
    modifier_10: StringProperty(description="Add a favourite modifier")
    modifier_11: StringProperty(description="Add a favourite modifier")
    modifier_12: StringProperty(description="Add a favourite modifier")

    use_icons_in_favourites: BoolProperty(
        name="Use Icons In Favourites",
        description="Use icons in favourite modifier buttons",
        default=True)

    insert_modifier_after_active: BoolProperty(
        name="Insert New Modifier After Active",
        description="When adding a new modifier, insert it after the active one. \n"
                    "Hold Control to override this. (When off, the behaviour is reversed). \n"
                    "NOTE: This is really slow on heavy meshes")

    disallow_applying_hidden_modifiers: BoolProperty(
        name="Disallow Applying Hidden Modifiers",
        description="Disallow applying modifier's which are hidden in the viewport. \n"
                    "Hold Alt to override this. (When off, the behaviour is reversed)")

    icon_color_items = [
        ("black", "Black", "", 1),
        ("white", "White", "", 2)
    ]
    icon_color: EnumProperty(
        items=icon_color_items,
        name="Icon Color",
        description="Color of the addon's custom icons",
        default="white",
        update=icon_color_callback)

    reverse_list: BoolProperty(
        name="Reverse List",
        description="Reverse the order of the list persistently (requires restart)")

    hide_general_settings_region: BoolProperty(
        name="Hide General Settings Region",
        description="Hide the region which shows modifier name and display settings. "
                    "The same settings are also inside the modifier list")

    show_confirmation_popups: BoolProperty(
        name="Show Confirmation Popups",
        description="Show confirmation popups for Apply All Modifiers "
                    "and Remove All Modifiers operators",
        default=True)

    show_batch_ops_in_main_layout_with_stack_style: BoolProperty(
        name="Show Batch Operators In Main Layout With Stack Style",
        description="When using the stack layout, show the batch operators in the main layout in "
                    "their own row. Otherwise they are located in the Modifier Extras popover",
        default=True)

    batch_ops_reports_items = [
        ("APPLY", "Apply", ""),
        ("REMOVE", "Remove", ""),
        ("TOGGLE_VISIBILITY", "Toggle visibility", "")
    ]
    batch_ops_reports: EnumProperty(
        items=batch_ops_reports_items,
        name="Show Info Messages For",
        description="Show batch operator info messages for",
        default={'APPLY', 'REMOVE', 'TOGGLE_VISIBILITY'},
        options={'ENUM_FLAG'})

    # === Popup settings ===
    popup_width: IntProperty(
        name="Width",
        description="Width of the popup, excluding the navigation bar",
        default=300)

    mod_list_def_len: IntProperty(
        name="",
        description="Default/min number of rows to display in the modifier list in the popup",
        default=7)

    use_props_dialog: BoolProperty(
        name="Use Dialog Type Popup",
        description="Use a dialog type popup which doesn't close when you are not hovering over "
                    "it")

    # === Gizmo object settings ===
    parent_new_gizmo_to_object: BoolProperty(
        name="Auto Parent Gizmos To Active Object",
        description="Automatically parent gizmos to the active object on addition")

    match_gizmo_size_to_object: BoolProperty(
        name="Match Gizmo Size To Active Object",
        description="Automatically match the size of the gizmo to the largest dimension of the "
                    "active object (before modifiers).\n"
                    "NOTE: This can be a bit slow on heavy meshes")

    always_delete_gizmo: BoolProperty(
        name="Always Delete Gizmo",
        description="Always delete the gizmo object when applying or removing a modifier. "
                    "When off, the gizmo object is deleted only when holding shift")

    # === Modifier defaults ===
    modifier_defaults: PointerProperty(type=ModifierDefaults)

    def draw(self, context):
        layout = self.layout

        ml_props = context.window_manager.modifier_list
        prefs_ui_props = ml_props.preferences_ui_props

        # === Info ===
        col = layout.column()
        col.label(icon='INFO',
                  text="Preferences are auto saved into your Blender config folder, eg:")
        col.label(text="      '...\\Blender Foundation\\Blender\\<blender version>"
                       "\\config\\modifier_list\\preferences.json'")

        layout.separator()

        # === Import ===
        filepath = os.path.dirname(bpy.utils.resource_path('USER')) + os.path.sep
        layout.operator("wm.ml_preferences_import", icon='IMPORT').filepath = filepath

        layout.separator()

        # === Enable/disable in Properties Editor and sidebar ===
        layout.prop(self, "use_properties_editor")
        layout.prop(self, "use_sidebar")

        layout.separator()

        # === UI style ===
        layout.label(text="Style:")

        split = layout.split()
        split.label(text="Properties Editor")
        split.row().prop(self, "properties_editor_style", expand=True)

        # template_modifiers() doesn't currently work outside of
        # Properties Editor, so sidebar_style and popup_style are
        # disabled. https://developer.blender.org/T88655.
        layout.label(text="The next two settings are currently disabled because of a bug in "
                     "Blender (T88655)", icon='INFO')

        split = layout.split()
        split.label(text="Sidebar")
        row = split.row()
        row.enabled = False
        row.prop(self, "sidebar_style", expand=True)

        split = layout.split()
        split.label(text="Popup")
        row = split.row()
        row.enabled = False
        row.prop(self, "popup_style", expand=True)

        # === Sidebar ===
        if self.use_sidebar:
            layout.separator()

            layout.prop(self, "keep_sidebar_visible")
            split = layout.split()
            split.label(text="Sidebar Category")
            split.prop(self, "sidebar_category", text="")

        layout.separator()

        # === Favourite modifiers ===
        _, box = box_with_header(layout, "Favourite Modifiers", prefs_ui_props,
                                 "favourite_modifiers_expand")

        if prefs_ui_props.favourite_modifiers_expand:
            split = box.split()
            split.label(text="Favourites Per Row")
            split.row().prop(self, "favourites_per_row", expand=True)

            box.separator()

            favourite_modifiers_configuration_layout(context, box)

            box.separator()

            box.prop(self, "use_icons_in_favourites")

        # === General ===
        _, box = box_with_header(layout, "General", prefs_ui_props, "general_expand")

        if prefs_ui_props.general_expand:
            box.prop(self, "insert_modifier_after_active")
            box.prop(self, "disallow_applying_hidden_modifiers")

            split = box.split()
            split.label(text="Icon Color")
            split.row().prop(self, "icon_color", expand=True)

            box.prop(self, "reverse_list")
            box.prop(self, "hide_general_settings_region")
            box.prop(self, "show_confirmation_popups")
            box.prop(self, "show_batch_ops_in_main_layout_with_stack_style")

            split = box.split()
            split.label(text="Show Info Messages For")
            split.row().prop(self, "batch_ops_reports", expand=True)

        # === Popup ===
        _, box = box_with_header(layout, "Popup", prefs_ui_props, "popup_expand")

        if prefs_ui_props.popup_expand:
            row = box.row()
            row.label(text="Width")
            row.prop(self, "popup_width", text="")

            row = box.row()
            row.label(text="Modifier List Default/Min Height")
            row.prop(self, "mod_list_def_len")

            box.prop(self, "use_props_dialog")

        # === Gizmo object ===
        _, box = box_with_header(layout, "Gizmo", prefs_ui_props, "gizmo_expand")

        if prefs_ui_props.gizmo_expand:
            box.prop(self, "parent_new_gizmo_to_object")
            box.prop(self, "match_gizmo_size_to_object")
            box.prop(self, "always_delete_gizmo")

        # === Modifier Defaults ===
        _, box = box_with_header(layout, "Modifier Defaults", prefs_ui_props,
                                 "modifier_defaults_expand")

        if prefs_ui_props.modifier_defaults_expand:
            row = box.row()
            row.prop_search(prefs_ui_props, "modifier_to_show_defaults_for", ml_props,
                            "all_modifiers", text="", icon='MODIFIER')

            sub = row.row()
            sub.scale_x = 0.7
            sub.operator("wm.ml_modifier_defaults_reset", text="Reset to Defaults",
                         icon='LOOP_BACK')

            mod_name = prefs_ui_props.modifier_to_show_defaults_for

            if not mod_name:
                box.label(text="Select a modifier to show defaults for")
                return

            if mod_name == "Geometry Nodes":
                box.label(text="No supported settings")
                return

            box.separator(factor=0.1)

            sub = box.box()

            mod_type = ml_props.all_modifiers[mod_name].value
            prop_group = getattr(self.modifier_defaults, mod_type)

            for prop in prop_group.__annotations__.keys():
                sub.prop(prop_group, prop)


# Registering
# ======================================================================

classes = None


def register():
    defaults_groups = add_modifier_defaults_groups()

    global classes
    classes = [
        *defaults_groups,
        ModifierDefaults,
        Preferences
    ]

    for cls in classes:
        bpy.utils.register_class(cls)

    # === Read preferences from a json ===
    config_dir = bpy.utils.user_resource('CONFIG')
    prefs_file = os.path.join(config_dir, "modifier_list", "preferences.json")
    read_prefs(prefs_file)


def unregister():
    # === Write preferences into a json ===
    write_prefs()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
