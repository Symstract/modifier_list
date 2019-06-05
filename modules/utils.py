import bpy

from . import modifier_categories


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


def _create_gizmo_object(self, context, modifier, place_at_vertex):
    """Create a gizmo (empty) object"""
    ob = context.object
    ob.update_from_editmode()
    ob_mat = ob.matrix_world
    mesh = ob.data

    sel_verts = [v for v in mesh.vertices if v.select]

    if place_at_vertex :
        if len(sel_verts) != 1:
            self.report(type={'INFO'}, message="Please, select (only) a single vertex")
            return
        else:
            vert_loc = ob_mat @ sel_verts[0].co

    gizmo_ob = bpy.data.objects.new(modifier + "_Gizmo", None)
    gizmo_ob.empty_display_type = 'ARROWS'

    if place_at_vertex:
        gizmo_ob.location = vert_loc
    else:
        gizmo_ob.location = ob_mat.to_translation()

    ml_col = _get_ml_collection(context)
    ml_col.objects.link(gizmo_ob)

    return gizmo_ob


def assign_gizmo_object_to_modifier(self, context, modifier, place_at_vertex=False):
    """Assign a gizmo object to the correct property of the given modifier"""
    ob = context.object
    mod = ob.modifiers[modifier]

    # If modifier is UV Project, handle it differently here
    if mod.type == 'UV_PROJECT':
        projectors = ob.modifiers[modifier].projectors
        projector_count = ob.modifiers[modifier].projector_count

        for p in projectors[0:projector_count]:
            if not p.object:
                gizmo_ob = _create_gizmo_object(self, context, modifier,
                                                place_at_vertex=place_at_vertex)
                p.object = gizmo_ob
                break

        return

    # If modifier is not UV Project, continue normally
    gizmo_ob = _create_gizmo_object(self, context, modifier, place_at_vertex=place_at_vertex)

    if mod.type == 'ARRAY':
        mod.use_object_offset = True

    gizmo_ob_prop = modifier_categories.have_gizmo_property[mod.type]

    setattr(mod, gizmo_ob_prop, gizmo_ob)