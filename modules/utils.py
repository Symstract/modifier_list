import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import distance_point_to_plane

from .modifier_categories import have_gizmo_property


def get_ml_active_object():
    """Get the active object or if some object is pinned, get that"""
    context = bpy.context
    ob = context.object
    wm = context.window_manager

    if wm.ml_pinned_object:
        if wm.ml_pinned_object.users == 1 and not wm.ml_pinned_object.use_fake_user:
            wm.ml_pinned_object = None
            return ob
        else:
            return wm.ml_pinned_object
    else:
        return ob


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


def _position_gizmo_object(gizmo_object):
    """Position a gizmo (empty) object"""
    ob = get_ml_active_object()
    ob.update_from_editmode()
    ob_mat = ob.matrix_world
    mesh = ob.data

    if ob.mode == 'EDIT':
        sel_verts = [v for v in mesh.vertices if v.select]
        if len(sel_verts) == 1:
            place_at_vertex = True
            vert_loc = ob_mat @ sel_verts[0].co
        else:
            place_at_vertex = False
    else:
        place_at_vertex = False

    if place_at_vertex:
        gizmo_object.location = vert_loc
    else:
        gizmo_object.location = ob_mat.to_translation()

    gizmo_object.rotation_euler = ob_mat.to_euler()


def _create_gizmo_object(self, context, modifier):
    """Create a gizmo (empty) object"""
    gizmo_ob = bpy.data.objects.new(modifier + "_Gizmo", None)
    gizmo_ob.empty_display_type = 'ARROWS'

    ml_col = _get_ml_collection(context)
    ml_col.objects.link(gizmo_ob)

    _position_gizmo_object(gizmo_ob)

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
    # Avoid setting dimensions of a lattice to 0; it causes problems
    ensured_length = length if length > 0 else 0.1
    # Avoid overlapping
    length_with_offset = ensured_length + 0.005
    return length_with_offset


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


def _fit_lattice_to_selection(object, vertices, lattice_object):
    ob_mat = object.matrix_world
    ob_loc, ob_rot, _ = ob_mat.decompose()
    vert_locs = [v.co for v in vertices]
    avg_vert_loc = sum(vert_locs, Vector()) / len(vert_locs)
    lat_origin = _calc_lattice_origin(vert_locs, avg_vert_loc)

    lattice_object.matrix_world = (Matrix.Translation(ob_loc) @ ob_rot.to_matrix().to_4x4() @
                                   Matrix.Translation(lat_origin))

    lattice_object.dimensions = _calc_lattice_dimensions(vert_locs, avg_vert_loc)


def _fit_lattice_to_object(object, lattice_object):
    ob_mat = object.matrix_world
    ob_loc, ob_rot, _ = ob_mat.decompose()

    local_bbox_center = sum((Vector(b) for b in object.bound_box), Vector()) / 8

    lattice_object.matrix_world = (Matrix.Translation(ob_loc) @ ob_rot.to_matrix().to_4x4() @
                                   Matrix.Translation(local_bbox_center))

    dims = object.dimensions
    # Avoid setting dimensions of a lattice to 0; it causes problems.
    # Also add some offset to avoid overlapping.
    ensured_dims = [d + 0.005 if d > 0 else 0.1 for d in dims]

    lattice_object.dimensions = ensured_dims


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

    if ob.mode == 'EDIT':
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

def assign_gizmo_object_to_modifier(self, context, modifier):
    """Assign a gizmo object to the correct property of the given modifier"""
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
                gizmo_ob = _create_gizmo_object(self, context, modifier)
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
        gizmo_ob = _create_gizmo_object(self, context, modifier)

    if mod.type == 'ARRAY':
        mod.use_constant_offset = False
        mod.use_relative_offset = False
        mod.use_object_offset = True

    gizmo_ob_prop = have_gizmo_property[mod.type]

    setattr(mod, gizmo_ob_prop, gizmo_ob)

    if parent_gizmo:
        gizmo_ob.parent = ob
        gizmo_ob.matrix_parent_inverse = ob.matrix_world.inverted()


# Other gizmo functions
# ======================================================================

def get_gizmo_object():
    ob = get_ml_active_object()
    active_mod_index = ob.ml_modifier_active_index
    active_mod = ob.modifiers[active_mod_index]

    if active_mod.type not in have_gizmo_property:
        return None

    gizmo_ob_prop = have_gizmo_property[active_mod.type]
    gizmo_ob = getattr(active_mod, gizmo_ob_prop)
    return gizmo_ob


def get_vertex_group():
    ob = get_ml_active_object()
    active_mod_index = ob.ml_modifier_active_index
    active_mod = ob.modifiers[active_mod_index]

    if not hasattr(active_mod, "vertex_group"):
        return None

    vert_group = active_mod.vertex_group
    return vert_group


def _delete_empty_ml_collection():
    cols = bpy.data.collections
    ml_col_name = "ML_Gizmo Objects"

    if ml_col_name in cols:
        ml_col = cols[ml_col_name]
        if not ml_col.objects:
            cols.remove(ml_col)


def delete_gizmo_object(self, gizmo_object):
    obs = bpy.data.objects

    if gizmo_object:
        obs.remove(gizmo_object)
        _delete_empty_ml_collection()
        self.report({'INFO'}, "Deleted a gizmo object")


def delete_ml_vertex_group(vertex_group):
    ob = get_ml_active_object()
    vert_group_name = vertex_group

    if vert_group_name:
        if vert_group_name.startswith("ML_"):
            vert_group = ob.vertex_groups[vert_group_name]
            ob.vertex_groups.remove(vert_group)

