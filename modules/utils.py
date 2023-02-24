import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import distance_point_to_plane

from .modifier_categories import ALL_MODIFIERS_NAMES_ICONS_TYPES, HAVE_GIZMO_PROPERTY


# Generic utils
# ======================================================================

def get_editable_bpy_object_props(bpy_object, props_to_ignore={}):
    props = [getattr(bpy_object, p.identifier) for p in bpy_object.bl_rna.properties
             if not p.is_readonly and p.identifier not in props_to_ignore]
    return [p[:] if type(p).__name__ == "bpy_prop_array" else p for p in props]


def sync_bpy_object_props(source, dest):
    for p in source.bl_rna.properties:
        if not p.is_readonly:
            setattr(dest, p.identifier, getattr(source, p.identifier))


# ======================================================================

def object_type_has_modifiers(object):
    obs_with_mods = {
        'MESH',
        'CURVE',
        'CURVES',
        'SURFACE',
        'FONT',
        'LATTICE',
        'POINTCLOUD',
        'VOLUME'
    }
    return object.type in obs_with_mods


def get_favourite_modifiers():
    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    return {attr: getattr(prefs, attr) for attr in prefs.__annotations__
            if attr.startswith("modifier_") and attr[-1].isdigit()}


def favourite_modifiers_names_icons_types():
    """Iterator of tuples of the names, icons and types of the favourite
    modifiers.
    """
    all_mods_dict = {mod[0]: mod for mod in ALL_MODIFIERS_NAMES_ICONS_TYPES}
    favorite_mods = get_favourite_modifiers().values()
    return (all_mods_dict[mod] if mod else (None, None, None) for mod in favorite_mods)


def get_ml_active_object():
    """Get the active object or if some object is pinned, get that"""
    context = bpy.context
    ob = context.object
    ml_pinned_ob = context.scene.modifier_list.pinned_object
    area = context.area

    if ml_pinned_ob and area.type != 'PROPERTIES':
        if not (ml_pinned_ob.users == 1 and ml_pinned_ob.use_fake_user):
            return ml_pinned_ob

    return ob


def is_modifier_local(object, modifier):
    """Check if the given modifier is local."""
    if object.library:
        return False
    elif object.override_library and not modifier.is_property_overridable_library("name"):
        return False

    return True


def is_modifier_disabled(mod):
    """Checks if the name of the modifier should be diplayed with a red
    background.
    """
    if mod.type == 'ARMATURE' and not mod.object:
        return True

    elif mod.type == 'BOOLEAN':
        if ((mod.operand_type == 'OBJECT' and not mod.object)
                or (mod.operand_type == 'COLLECTION' and not mod.collection)):
            return True

    elif mod.type == 'CAST':
        if not any((mod.use_x, mod.use_y, mod.use_z)) or mod.factor == 0:
            return True

    elif mod.type == 'CURVE' and not mod.object:
        return True

    elif mod.type == 'DATA_TRANSFER' and not mod.object:
        return True

    elif mod.type == 'DISPLACE':
        if (mod.direction == 'RGB_TO_XYZ' and not mod.texture) or mod.strength == 0:
            return True

    elif mod.type == 'HOOK' and not mod.object:
        return True

    elif mod.type == 'LAPLACIANDEFORM' and not mod.vertex_group:
        return True

    elif mod.type == 'LAPLACIANSMOOTH':
        if not any((mod.use_x, mod.use_y, mod.use_z)) or mod.lambda_factor == 0:
            return True

    elif mod.type == 'LATTICE' and not mod.object:
        return True

    elif mod.type == 'MESH_CACHE' and (not mod.filepath or mod.factor == 0):
        return True

    elif mod.type == 'MESH_DEFORM' and not mod.object:
        return True

    elif mod.type == 'MESH_SEQUENCE_CACHE' and (not mod.cache_file or not mod.object_path):
        return True

    elif mod.type == 'MESH_TO_VOLUME' and not mod.object:
        return True

    elif mod.type == 'NODES' and not mod.node_group:
        return True

    elif mod.type == 'NORMAL_EDIT' and (mod.mode == 'DIRECTIONAL' and not mod.target):
        return True

    elif mod.type == 'PARTICLE_INSTANCE':
        if not mod.object:
            return True

        if not mod.object.particle_systems:
            return True
        else:
            for m in mod.object.modifiers:
                if m.type == 'PARTICLE_SYSTEM' and m.particle_system == mod.particle_system:
                    if not m.show_viewport:
                        return True

    elif mod.type == 'SHRINKWRAP' and not mod.target:
        return True

    elif mod.type == 'SMOOTH':
        if not any((mod.use_x, mod.use_y, mod.use_z)) or mod.factor == 0:
            return True

    elif mod.type == 'SUBSURF' and mod.levels == 0:
        return True

    elif mod.type == 'SURFACE_DEFORM' and not mod.target:
        return True

    elif mod.type == 'VERTEX_WEIGHT_EDIT' and not mod.vertex_group:
        return True

    elif mod.type == 'VERTEX_WEIGHT_MIX' and not mod.vertex_group_a:
        return True

    elif mod.type == 'VERTEX_WEIGHT_PROXIMITY' and (not mod.vertex_group or not mod.target):
        return True

    elif mod.type == 'VOLUME_DISPLACE' and not mod.texture:
        return True

    elif mod.type == 'VOLUME_TO_MESH' and not mod.object:
        return True

    return False


# Functions for adding a gizmo object
# ======================================================================

def _get_ml_collection(context):
    """Get the ml gizmo collection or create it if it doesnt exist yet"""
    scene = context.scene

    if "ML_Gizmo Objects" not in scene.collection.children:
        ml_col = bpy.data.collections.new("ML_Gizmo Objects")
        scene.collection.children.link(ml_col)
    else:
        ml_col = bpy.data.collections["ML_Gizmo Objects"]

    return ml_col


def _create_vertex_group_from_vertices(object, vertex_indices, group_name):
    """Create a vertex group for a modifier to use.
    Works only in object mode."""
    vert_group = object.vertex_groups.new(name=group_name)
    vert_group.add(vertex_indices, 1, 'ADD')
    return vert_group


def _get_selected_points_from_curve(curve):
    sel_points = []

    for spline in curve.splines:
        if spline.type == 'BEZIER':
            for p in spline.bezier_points:
                if p.select_control_point:
                    sel_points.append(p)
        else:
            for p in spline.points:
                if p.select:
                    sel_points.append(p)
                    print(p.co)

    return sel_points


def _position_gizmo_object_at_object(gizmo_object, object):
    """Position a gizmo (empty) object at the active
    object or at the selected vertices.
    """
    ob = object
    ob_mat = ob.matrix_world
    data = ob.data

    place_at_verts = False

    if ob.type in {'CURVE', 'MESH'} and ob.mode == 'EDIT':
        if ob.type == 'MESH':
            sel_points = [v for v in data.vertices if v.select]
        else:
            sel_points = _get_selected_points_from_curve(data)
        if sel_points:
            place_at_verts = True

    if place_at_verts:
        sel_points_coords = [v.co for v in sel_points]
        if ob.type == 'CURVE':
            # Make sure all coords are 3D because SplinePoint.co is
            # 4D, unlike BezierSplinePoint.co which is 3D.
            sel_points_coords = [co.to_3d() for co in sel_points_coords]
        average_vert_co = sum(sel_points_coords, Vector()) / len(sel_points_coords)
        global_average_vert_co = ob_mat @ average_vert_co
        gizmo_object.location = global_average_vert_co
    else:
        gizmo_object.location = ob_mat.to_translation()

    gizmo_object.rotation_euler = ob_mat.to_euler()


def _position_gizmo_object_at_cursor(gizmo_object):
    """Position a gizmo (empty) object at the 3D Cursor"""
    context = bpy.context
    ob = get_ml_active_object()
    ob_mat = ob.matrix_world

    gizmo_object.location = context.scene.cursor.location
    gizmo_object.rotation_euler = ob_mat.to_euler()


def _match_gizmo_size_to_object(gizmo_object, object):
    """Match the size of a gizmo to the size of the object
    (before modifiers).
    """
    ob_scale = object.matrix_world.to_scale()
    verts = object.data.vertices

    max_dim = 0

    for i in range(3):
        axis = [v.co[i] for v in verts]
        axis_dim = (max(axis) - min(axis)) * ob_scale[i]
        if axis_dim > max_dim:
            max_dim = axis_dim

    max_dim_divided = max_dim / 2
    max_dim_with_offset = max_dim_divided + max_dim_divided / 9

    gizmo_object.empty_display_size = max_dim_with_offset


def _create_gizmo_object(self, context, modifier, placement='OBJECT'):
    """Create a gizmo (empty) object.

    placement: enum in {'CURSOR', 'OBJECT', 'WORLD_ORIGIN'}
    """
    gizmo_ob = bpy.data.objects.new(modifier + "_Gizmo", None)
    gizmo_ob.empty_display_type = 'ARROWS'

    ml_col = _get_ml_collection(context)
    ml_col.objects.link(gizmo_ob)

    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    ob = get_ml_active_object()

    # Only use update_from_editmode if necessary
    if placement == 'OBJECT' or prefs.match_gizmo_size_to_object:
        if ob.mode == 'EDIT':
            ob.update_from_editmode()

    if placement == 'CURSOR':
        _position_gizmo_object_at_cursor(gizmo_ob)
    elif placement == 'OBJECT':
        _position_gizmo_object_at_object(gizmo_ob, ob)

    if prefs.match_gizmo_size_to_object:
        _match_gizmo_size_to_object(gizmo_ob, ob)

    return gizmo_ob


# === Lattice ===

def _calc_lattice_axis_length(vertex_coords, plane_co, plane_no):
    max_dist = 0
    min_dist = 0

    for v in vertex_coords:
        dist = distance_point_to_plane(v, plane_co, plane_no)
        if dist > max_dist:
            max_dist = dist
        elif dist < min_dist:
            min_dist = dist

    length = max_dist + abs(min_dist)
    return length


def _calc_lattice_dimensions(vertex_coords, plane_co, plane_no=None):
    normal_vecs = [Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))]

    # for v in normal_vecs:
    #     v.rotate(plane_no.to_track_quat('X', 'Z'))

    dims = [_calc_lattice_axis_length(vertex_coords, plane_co, normal) for normal in normal_vecs]
    return dims


def _calc_lattice_axis_midpoint_location(vertex_coords, plane_co, plane_no):
    max_dist = 0
    min_dist = 0

    max_vert_co = Vector((0, 0, 0))
    min_vert_co = Vector((0, 0, 0))

    for v in vertex_coords:
        dist = distance_point_to_plane(v, plane_co, plane_no)
        if dist > max_dist:
            max_dist = dist
            max_vert_co = v
        elif dist < min_dist:
            min_dist = dist
            min_vert_co = v

    midpoint_co = (max_vert_co + min_vert_co) / 2
    if midpoint_co == Vector((0, 0, 0)):
        midpoint_co = plane_co
    return midpoint_co


def _calc_lattice_origin(vertex_coords, plane_co, plane_no=None):
    normal_vecs = [Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))]
    origin = Vector((0, 0, 0))

    for i, normal in enumerate(normal_vecs):
        origin[i] = _calc_lattice_axis_midpoint_location(vertex_coords, plane_co, normal)[i]

    return origin


def _set_lattice_points(lattice_object, lattice_dimensions):
    """Set the number of points per axis for a lattice.

    If the lattice has zero lenght on an axis, the amount of points on
    that axis is 1; otherwise it's 2. That way there's no unnecessary
    points.
    """
    lat = lattice_object.data
    points = "points_u", "points_v", "points_w"

    for i, p in enumerate(points):
        num_of_points = 1 if lattice_dimensions[i] == 0 else 2
        setattr(lat, p, num_of_points)


def _fit_lattice_to_selection(object, vertices, lattice_object):
    ob_mat = object.matrix_world
    ob_loc, ob_rot, ob_scale = ob_mat.decompose()
    vert_locs = [Matrix.Diagonal(ob_scale) @ v.co for v in vertices]
    avg_vert_loc = sum(vert_locs, Vector()) / len(vert_locs)
    lat_origin = _calc_lattice_origin(vert_locs, avg_vert_loc)

    lattice_object.matrix_world = (Matrix.Translation(ob_loc) @ ob_rot.to_matrix().to_4x4() @
                                   Matrix.Translation(lat_origin))

    dims = _calc_lattice_dimensions(vert_locs, avg_vert_loc)
    # Avoid setting dimensions of a lattice to 0; it causes problems.
    ensured_dims = [d if d > 0 else 0.1 for d in dims]

    lattice_object.dimensions = ensured_dims

    _set_lattice_points(lattice_object, dims)


def _fit_lattice_to_object(object, lattice_object):
    ob_mat = object.matrix_world
    ob_loc, ob_rot, _ = ob_mat.decompose()

    local_bbox_center = sum((Vector(b) for b in object.bound_box), Vector()) / 8

    lattice_object.matrix_world = (Matrix.Translation(ob_loc) @ ob_rot.to_matrix().to_4x4() @
                                   Matrix.Translation(local_bbox_center))

    dims = object.dimensions
    # Avoid setting dimensions of a lattice to 0; it causes problems.
    ensured_dims = [d if d > 0 else 0.1 for d in dims]

    lattice_object.dimensions = ensured_dims

    _set_lattice_points(lattice_object, dims)


def _position_lattice_gizmo_object(gizmo_object):
    """Position a lattice gizmo object"""
    ob = get_ml_active_object()
    mesh = ob.data
    active_mod_index = ob.ml_modifier_active_index
    active_mod = ob.modifiers[active_mod_index]

    has_already_vert_group = bool(active_mod.vertex_group)
    if has_already_vert_group:
        vert_group_index = ob.vertex_groups[active_mod.vertex_group].index
    else:
        vert_group_index = None

    if ob.type != 'MESH':
        place_at_verts = False
    elif ob.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')
        if not has_already_vert_group:
            sel_verts = [v for v in mesh.vertices if v.select]
            place_at_verts = len(sel_verts) >= 2
            if place_at_verts:
                vert_indices = [v.index for v in sel_verts]
                vert_group = _create_vertex_group_from_vertices(ob, vert_indices, "ML_Lattice")
                active_mod.vertex_group = vert_group.name
        else:
            sel_verts = [v for v in mesh.vertices if vert_group_index in
                         [vg.group for vg in v.groups]]
            place_at_verts = len(sel_verts) >= 2
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        if has_already_vert_group:
            sel_verts = [v for v in mesh.vertices if vert_group_index in
                         [vg.group for vg in v.groups]]
            place_at_verts = len(sel_verts) >= 2
        else:
            place_at_verts = False

    if place_at_verts:
        _fit_lattice_to_selection(ob, sel_verts, gizmo_object)
    else:
        _fit_lattice_to_object(ob, gizmo_object)


def _create_lattice_gizmo_object(self, context, modifier):
    """Create a gizmo (lattice) object"""
    lattice = bpy.data.lattices.new(modifier + "_Gizmo")
    gizmo_ob = bpy.data.objects.new(modifier + "_Gizmo", lattice)

    ml_col = _get_ml_collection(context)
    ml_col.objects.link(gizmo_ob)

    _position_lattice_gizmo_object(gizmo_ob)

    return gizmo_ob


# ==========

def assign_gizmo_object_to_modifier(self, context, modifier, placement='OBJECT'):
    """Assign a gizmo object to the correct property of the given modifier.

    placement: enum in {'CURSOR', 'OBJECT', 'WORLD_ORIGIN'}
    """
    ob = get_ml_active_object()
    mod = ob.modifiers[modifier]
    prefs = bpy.context.preferences.addons["modifier_list"].preferences
    parent_gizmo = prefs.parent_new_gizmo_to_object

    # If modifier is UV Project, handle it differently here
    if mod.type == 'UV_PROJECT':
        projectors = ob.modifiers[modifier].projectors
        projector_count = ob.modifiers[modifier].projector_count

        for p in projectors[0:projector_count]:
            if not p.object:
                gizmo_ob = _create_gizmo_object(self, context, modifier, placement)
                p.object = gizmo_ob
                if parent_gizmo:
                    gizmo_ob.parent = ob
                    gizmo_ob.matrix_parent_inverse = ob.matrix_world.inverted()
                break

        return

    # If modifier is not UV Project, continue normally
    if mod.type == 'LATTICE':
        gizmo_ob = _create_lattice_gizmo_object(self, context, modifier)
    else:
        gizmo_ob = _create_gizmo_object(self, context, modifier, placement)

    if mod.type == 'ARRAY':
        mod.use_constant_offset = False
        mod.use_relative_offset = False
        mod.use_object_offset = True

    if parent_gizmo:
        gizmo_ob.parent = ob
        gizmo_ob.matrix_parent_inverse = ob.matrix_world.inverted()

        # Make sure modifiers use the updated transformation
        # (needed at least for Hook)
        bpy.context.view_layer.update()

    gizmo_ob_prop = HAVE_GIZMO_PROPERTY[mod.type]

    setattr(mod, gizmo_ob_prop, gizmo_ob)

    # If gizmo is parented in edit mode, Hook has wrong tranformation
    # if it isn't explicitly reset here.
    if mod.type == 'HOOK' and ob.mode == 'EDIT':
        bpy.ops.object.hook_reset(modifier=mod.name)

    if mod.type == 'LATTICE':
        if context.area.type == 'PROPERTIES':
            bpy.ops.object.lattice_toggle_editmode_prop_editor()
        else:
            bpy.ops.object.lattice_toggle_editmode()


# Other gizmo functions
# ======================================================================

def get_gizmo_object_from_modifier(modifier):
    if modifier.type not in HAVE_GIZMO_PROPERTY:
        return None

    gizmo_ob_prop = HAVE_GIZMO_PROPERTY[modifier.type]
    gizmo_ob = getattr(modifier, gizmo_ob_prop)
    return gizmo_ob


def _delete_empty_ml_collection():
    cols = bpy.data.collections
    ml_col_name = "ML_Gizmo Objects"

    if ml_col_name in cols:
        ml_col = cols[ml_col_name]
        if not ml_col.objects:
            cols.remove(ml_col)


def delete_gizmo_object(self, gizmo_object):
    if gizmo_object:
        if gizmo_object.type in {'EMPTY', 'LATTICE'} and "_Gizmo" in gizmo_object.name:
            bpy.data.objects.remove(gizmo_object)
            _delete_empty_ml_collection()
            self.report({'INFO'}, "Deleted a gizmo object")


def delete_ml_vertex_group(object, vertex_group_name):
    vert_groups = object.vertex_groups

    if vertex_group_name:
        if vertex_group_name.startswith("ML_"):
            if vertex_group_name in vert_groups:
                vert_group = vert_groups[vertex_group_name]
                vert_groups.remove(vert_group)
