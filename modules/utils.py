import bpy
from mathutils import Vector

from .modifier_categories import have_gizmo_property


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


def _create_vertex_group_from_selection(object, vertex_indices, group_name):
    """Create a vertex group for a modifier to use """
    vert_group = object.vertex_groups.new(name=group_name)
    bpy.ops.object.mode_set(mode='OBJECT')
    vert_group.add(vertex_indices, 1, 'ADD')
    bpy.ops.object.mode_set(mode='EDIT')
    return vert_group


def _create_gizmo_object(self, context, modifier):
    """Create a gizmo (empty) object"""
    ob = context.object
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

    gizmo_ob = bpy.data.objects.new(modifier + "_Gizmo", None)
    gizmo_ob.empty_display_type = 'ARROWS'

    if place_at_vertex:
        gizmo_ob.location = vert_loc
    else:
        gizmo_ob.location = ob_mat.to_translation()

    gizmo_ob.rotation_euler = ob_mat.to_euler()

    ml_col = _get_ml_collection(context)
    ml_col.objects.link(gizmo_ob)

    return gizmo_ob


def _create_lattice_gizmo_object(self, context, modifier):
    """Create a gizmo (lattice) object"""
    ob = context.object
    ob.update_from_editmode()
    ob_mat = ob.matrix_world
    mesh = ob.data
    active_mod_index = ob.ml_modifier_active_index
    active_mod = ob.modifiers[active_mod_index]

    if ob.mode == 'EDIT':
        sel_verts = [v for v in mesh.vertices if v.select]
        if len(sel_verts) >= 2:
            place_at_verts = True

            vert_indices = [v.index for v in sel_verts]
            vert_locs = [v.co for v in sel_verts]
            local_verts_avg_loc = sum(vert_locs, Vector()) / len(sel_verts)
            global_verts_avg_loc = ob_mat @ local_verts_avg_loc

            vert_group = _create_vertex_group_from_selection(ob, vert_indices, "ML_Lattice")
            active_mod.vertex_group = vert_group.name
        else:
            place_at_verts = False
    else:
        place_at_verts = False

    lattice = bpy.data.lattices.new(modifier + "_Gizmo")
    gizmo_ob = bpy.data.objects.new(modifier + "_Gizmo", lattice)

    if place_at_verts:
        gizmo_ob.location = global_verts_avg_loc
    else:
        local_bound_box_center = sum((Vector(b) for b in ob.bound_box), Vector()) / 8
        global_bound_box_center = ob_mat @ local_bound_box_center
        gizmo_ob.location = global_bound_box_center

    gizmo_ob.dimensions = ob.dimensions
    gizmo_ob.rotation_euler = ob_mat.to_euler()

    ml_col = _get_ml_collection(context)
    ml_col.objects.link(gizmo_ob)

    return gizmo_ob


def assign_gizmo_object_to_modifier(self, context, modifier):
    """Assign a gizmo object to the correct property of the given modifier"""
    ob = context.object
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

def get_gizmo_object(context):
    ob = context.object
    active_mod_index = ob.ml_modifier_active_index
    active_mod = ob.modifiers[active_mod_index]

    if active_mod.type not in have_gizmo_property:
        return None

    gizmo_ob_prop = have_gizmo_property[active_mod.type]
    gizmo_ob = getattr(active_mod, gizmo_ob_prop)
    return gizmo_ob


def get_vertex_group(context):
    ob = context.object
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


def delete_gizmo_object(self, context, gizmo_object):
    obs = bpy.data.objects

    if gizmo_object:
        obs.remove(gizmo_object)
        _delete_empty_ml_collection()
        self.report({'INFO'}, "Deleted a gizmo object")


def delete_ml_vertex_group(context, vertex_group):
    ob = context.object
    vert_group_name = vertex_group

    if vert_group_name:
        if vert_group_name.startswith("ML_"):
            vert_group = ob.vertex_groups[vert_group_name]
            ob.vertex_groups.remove(vert_group)

