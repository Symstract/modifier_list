import bpy
from bl_ui.properties_data_modifier import DATA_PT_modifiers

from..utils import get_gizmo_object


# Modified to improve
# ======================================================================
def LATTICE(layout, ob, md):
    context = bpy.context
    gizmo_ob = get_gizmo_object(context)

    if gizmo_ob:
        lat = gizmo_ob.data

        row = layout.row()
        row.prop(lat, "points_u")
        row.prop(lat, "interpolation_type_u", text="")

        row = layout.row()
        row.prop(lat, "points_v")
        row.prop(lat, "interpolation_type_v", text="")

        row = layout.row()
        row.prop(lat, "points_w")
        row.prop(lat, "interpolation_type_w", text="")

        layout.separator()

        layout.prop(lat, "use_outside", text="Outside Only")

        layout.separator()

    mp = DATA_PT_modifiers(context)
    mp.LATTICE(layout, ob, md)



# Modified to work
# ======================================================================

def LAPLACIANDEFORM(layout, ob, md):
    is_bind = md.is_bind

    layout.prop(md, "iterations")

    row = layout.row()
    row.active = not is_bind
    row.label(text="Anchors Vertex Group:")

    row = layout.row()
    row.enabled = not is_bind
    row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

    layout.separator()

    row = layout.row()
    row.enabled = bool(md.vertex_group)
    row.operator("object.laplaciandeform_bind", text="Unbind" if is_bind else "Bind").modifier = md.name # Changed


def MESH_DEFORM(layout, ob, md):
    split = layout.split()

    col = split.column()
    col.enabled = not md.is_bound
    col.label(text="Object:")
    col.prop(md, "object", text="")

    col = split.column()
    col.label(text="Vertex Group:")
    row = col.row(align=True)
    row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
    sub = row.row(align=True)
    sub.active = bool(md.vertex_group)
    sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

    layout.separator()
    row = layout.row()
    row.enabled = not md.is_bound
    row.prop(md, "precision")
    row.prop(md, "use_dynamic_bind")

    layout.separator()
    if md.is_bound:
        layout.operator("object.meshdeform_bind", text="Unbind").modifier = md.name # Changed
    else:
        layout.operator("object.meshdeform_bind", text="Bind").modifier = md.name # Changed


def SURFACE_DEFORM(layout, _ob, md):
        col = layout.column()
        col.active = not md.is_bound

        col.prop(md, "target")
        col.prop(md, "falloff")

        layout.separator()

        col = layout.column()

        if md.is_bound:
            col.operator("object.surfacedeform_bind", text="Unbind").modifier = md.name # Changed
        else:
            col.active = md.target is not None
            col.operator("object.surfacedeform_bind", text="Bind").modifier = md.name # Changed