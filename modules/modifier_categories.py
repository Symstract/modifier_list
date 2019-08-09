import bpy


def all_modifier_names_icons_types():
    """List of tuples of the names, icons and types of all modifiers."""
    mods_enum = bpy.types.Modifier.bl_rna.properties['type'].enum_items

    all_mod_names = [modifier.name for modifier in mods_enum]
    all_mod_icons = [modifier.icon for modifier in mods_enum]
    all_mod_types = [modifier.identifier for modifier in mods_enum]

    all_mods_zipped = list(zip(all_mod_names, all_mod_icons, all_mod_types))
    return all_mods_zipped


def get_favourite_modifiers_names():
    """List of the names of the favourite modifiers"""
    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    # get correct class attributes and then their values
    attr_list = [attr for attr in dir(prefs) if  attr.startswith("modifier_")]
    attr_value_list = [getattr(prefs, attr) for attr in attr_list]
    return attr_value_list


def favourite_modifiers_names_icons_types():
    """Iterator of tuples of the names, icons and types of the favourite
    modifiers.
    """
    mods_enum = bpy.types.Modifier.bl_rna.properties['type'].enum_items
    all_mod_names = [modifier.name for modifier in mods_enum]
    all_mods_dict = dict(zip(all_mod_names, all_modifier_names_icons_types()))
    fav_mods_list = [all_mods_dict[mod] if mod in all_mods_dict else (None, None, None)
                     for mod in get_favourite_modifiers_names()]
    fav_mods_iter = iter(fav_mods_list)
    return fav_mods_iter


# === Don't support show_in_editmode ===
dont_support_show_in_editmode = {
    'MESH_SEQUENCE_CACHE', 'BUILD', 'DECIMATE', 'MULTIRES', 'CLOTH', 'COLLISION',
    'DYNAMIC_PAINT','EXPLODE', 'FLUID_SIMULATION', 'PARTICLE_SYSTEM','SMOKE', 'SOFT_BODY'
}

# === Support show_on_cage ===
deform_mods = {mod for _, _, mod in all_modifier_names_icons_types()[25:41]}
other_show_on_cage_mods = {
    'DATA_TRANSFER', 'NORMAL_EDIT', 'WEIGHTED_NORMAL', 'UV_PROJECT','VERTEX_WEIGHT_EDIT',
    'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_PROXIMITY', 'ARRAY', 'EDGE_SPLIT', 'MASK', 'MIRROR',
    'SOLIDIFY', 'SUBSURF', 'TRIANGULATE'
}
support_show_on_cage = deform_mods.union(other_show_on_cage_mods)

# === Support apply_as_shape_key ===
deform_mods = {mod for name, icon, mod in all_modifier_names_icons_types()[26:42]}
other_shape_key_mods = {'CLOTH', 'SOFT_BODY', 'MESH_CACHE'}
support_apply_as_shape_key = deform_mods.union(other_shape_key_mods)

# === Don't support copy ===
dont_support_copy = {
    'CLOTH', 'COLLISION', 'DYNAMIC_PAINT', 'FLUID_SIMULATION',
    'PARTICLE_SYSTEM', 'SMOKE', 'SOFT_BODY'
}

# === Have the ability to use an object to define the center of the effect ===
have_gizmo_property = {
    'NORMAL_EDIT': "target",
    'VERTEX_WEIGHT_PROXIMITY': "target",
    'ARRAY': "offset_object",
    'MIRROR': "mirror_object",
    'SCREW': "object",
    'CAST': "object",
    'HOOK': "object",
    'LATTICE': "object",
    'SIMPLE_DEFORM': "origin",
    'WAVE': "start_position_object"
}

# === Mesh modifiers by categories ===
mesh_modify_names_icons_types = [mod for mod in all_modifier_names_icons_types()[0:10]]

mesh_generate_names_icons_types = [mod for mod in all_modifier_names_icons_types()[10:26]]

mesh_deform_names_icons_types = [mod for mod in all_modifier_names_icons_types()[26:42]]

mesh_simulate_names_icons_types = [mod for mod in all_modifier_names_icons_types()[42:52]]

# === Curve, surface and text modifiers by categories ===
curve_modify_names_icons_types = (
    ('Mesh Cache', 'MOD_MESHDEFORM', 'MESH_CACHE'),
    ('Mesh Sequence Cache', 'MOD_MESHDEFORM', 'MESH_SEQUENCE_CACHE')
)

curve_generate_names_icons_types = (
    ('Array', 'MOD_ARRAY', 'ARRAY'),
    ('Bevel', 'MOD_BEVEL', 'BEVEL'),
    ('Build', 'MOD_BUILD', 'BUILD'),
    ('Decimate', 'MOD_DECIM', 'DECIMATE'),
    ('Edge Split', 'MOD_EDGESPLIT', 'EDGE_SPLIT'),
    ('Mirror', 'MOD_MIRROR', 'MIRROR'),
    ('Remesh', 'MOD_REMESH', 'REMESH'),
    ('Screw', 'MOD_SCREW', 'SCREW'),
    ('Solidify', 'MOD_SOLIDIFY', 'SOLIDIFY'),
    ('Subdivision Surface', 'MOD_SUBSURF', 'SUBSURF'),
    ('Triangulate', 'MOD_TRIANGULATE', 'TRIANGULATE'),
)

curve_deform_names_icons_types = (
    ('Armature', 'MOD_ARMATURE', 'ARMATURE'),
    ('Cast', 'MOD_CAST', 'CAST'),
    ('Curve', 'MOD_CURVE', 'CURVE'),
    ('Hook', 'HOOK', 'HOOK'),
    ('Lattice', 'MOD_LATTICE', 'LATTICE'),
    ('Mesh Deform', 'MOD_MESHDEFORM', 'MESH_DEFORM'),
    ('Shrinkwrap', 'MOD_SHRINKWRAP', 'SHRINKWRAP'),
    ('Simple Deform', 'MOD_SIMPLEDEFORM', 'SIMPLE_DEFORM'),
    ('Smooth', 'MOD_SMOOTH', 'SMOOTH'),
    ('Warp', 'MOD_WARP', 'WARP'),
    ('Wave', 'MOD_WAVE', 'WAVE'),
)

curve_simulate_names_icons_types = (
    ('Soft Body', 'MOD_SOFT', 'SOFT_BODY'),
)

curve_all_names_icons_types = (
    curve_modify_names_icons_types
    + curve_generate_names_icons_types
    + curve_deform_names_icons_types
    + curve_simulate_names_icons_types
)

# === Lattice modifiers by categories ===
lattice_modify_names_icons_types = (
    ('Mesh Cache', 'MOD_MESHDEFORM', 'MESH_CACHE'),
)

lattice_deform_names_icons_types = (
    ('Armature', 'MOD_ARMATURE', 'ARMATURE'),
    ('Cast', 'MOD_CAST', 'CAST'),
    ('Curve', 'MOD_CURVE', 'CURVE'),
    ('Hook', 'HOOK', 'HOOK'),
    ('Lattice', 'MOD_LATTICE', 'LATTICE'),
    ('Mesh Deform', 'MOD_MESHDEFORM', 'MESH_DEFORM'),
    ('Shrinkwrap', 'MOD_SHRINKWRAP', 'SHRINKWRAP'),
    ('Simple Deform', 'MOD_SIMPLEDEFORM', 'SIMPLE_DEFORM'),
    ('Warp', 'MOD_WARP', 'WARP'),
    ('Wave', 'MOD_WAVE', 'WAVE'),
)

lattice_simulate_names_icons_types = (
    ('Soft Body', 'MOD_SOFT', 'SOFT_BODY'),
)

lattice_all_names_icons_types = (
    curve_modify_names_icons_types
    + curve_deform_names_icons_types
    + curve_simulate_names_icons_types
)