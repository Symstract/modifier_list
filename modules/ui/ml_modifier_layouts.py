import bpy
from bl_ui.properties_data_modifier import DATA_PT_modifiers

from..utils import get_gizmo_object


# Modified to improve
# ======================================================================


def BOOLEAN(layout, ob, md):
    context = bpy.context
    mp = DATA_PT_modifiers(context)
    mp.BOOLEAN(layout, ob, md)

    if not md.object:
        return

    layout.separator()

    layout.label(text="Boolean Object:")

    is_hidden = md.object.hide_get()
    depress = is_hidden
    icon = 'HIDE_ON' if is_hidden else 'HIDE_OFF'
    layout.operator("object.ml_toggle_visibility_on_view_layer",
                    text="Hide", icon=icon, depress=depress).object_name = md.object.name

    layout.separator()

    layout.prop(md.object, "display_type")

    layout.separator()

    op = layout.operator("object.ml_smooth_shading_set", text="Shade Smooth")
    op.object_name = md.object.name
    op.shade_smooth = True

    op = layout.operator("object.ml_smooth_shading_set", text="Shade Flat")
    op.object_name = md.object.name
    op.shade_smooth = False


def LATTICE(layout, ob, md):
    context = bpy.context
    gizmo_ob = get_gizmo_object()

    if gizmo_ob:
        lat = gizmo_ob.data

        row = layout.row()
        row.enabled = not gizmo_ob.hide_viewport
        depress = gizmo_ob.mode == 'EDIT'
        if context.area.type == 'PROPERTIES':
            row.operator("object.lattice_toggle_editmode_prop_editor", text="Edit Lattice",
                         depress=depress)
        else:
            row.operator("object.lattice_toggle_editmode", text="Edit Lattice", depress=depress)

        layout.separator()

        row = layout.row()

        sub = row.column(align=True)
        sub.prop(lat, "points_u")
        sub.prop(lat, "points_v")
        sub.prop(lat, "points_w")

        sub = row.column(align=True)
        sub.prop(lat, "interpolation_type_u", text="")
        sub.prop(lat, "interpolation_type_v", text="")
        sub.prop(lat, "interpolation_type_w", text="")

        layout.separator()

        layout.prop(lat, "use_outside", text="Outside Only")

        layout.separator()

    mp = DATA_PT_modifiers(context)
    mp.LATTICE(layout, ob, md)



# Modified to work
# ======================================================================


def CORRECTIVE_SMOOTH(layout, ob, md):
    is_bind = md.is_bind

    layout.prop(md, "factor", text="Factor")
    layout.prop(md, "iterations")

    row = layout.row()
    row.prop(md, "smooth_type")

    split = layout.split()

    col = split.column()
    col.label(text="Vertex Group:")
    row = col.row(align=True)
    row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
    row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

    col = split.column()
    col.prop(md, "use_only_smooth")
    col.prop(md, "use_pin_boundary")

    layout.prop(md, "rest_source")
    if md.rest_source == 'BIND':
        layout.operator("object.correctivesmooth_bind",
                        text="Unbind" if is_bind else "Bind").modifier = md.name # Changed


def DATA_TRANSFER(layout, ob, md):
    row = layout.row(align=True)
    row.prop(md, "object")
    sub = row.row(align=True)
    sub.active = bool(md.object)
    sub.prop(md, "use_object_transform", text="", icon='GROUP')

    layout.separator()

    split = layout.split(factor=0.333)
    split.prop(md, "use_vert_data")
    use_vert = md.use_vert_data
    row = split.row()
    row.active = use_vert
    row.prop(md, "vert_mapping", text="")
    if use_vert:
        col = layout.column(align=True)
        split = col.split(factor=0.333, align=True)
        sub = split.column(align=True)
        sub.prop(md, "data_types_verts")
        sub = split.column(align=True)
        row = sub.row(align=True)
        row.prop(md, "layers_vgroup_select_src", text="")
        row.label(icon='RIGHTARROW')
        row.prop(md, "layers_vgroup_select_dst", text="")
        row = sub.row(align=True)
        row.label(text="", icon='NONE')

    layout.separator()

    split = layout.split(factor=0.333)
    split.prop(md, "use_edge_data")
    use_edge = md.use_edge_data
    row = split.row()
    row.active = use_edge
    row.prop(md, "edge_mapping", text="")
    if use_edge:
        col = layout.column(align=True)
        split = col.split(factor=0.333, align=True)
        sub = split.column(align=True)
        sub.prop(md, "data_types_edges")

    layout.separator()

    split = layout.split(factor=0.333)
    split.prop(md, "use_loop_data")
    use_loop = md.use_loop_data
    row = split.row()
    row.active = use_loop
    row.prop(md, "loop_mapping", text="")
    if use_loop:
        col = layout.column(align=True)
        split = col.split(factor=0.333, align=True)
        sub = split.column(align=True)
        sub.prop(md, "data_types_loops")
        sub = split.column(align=True)
        row = sub.row(align=True)
        row.label(text="", icon='NONE')
        row = sub.row(align=True)
        row.prop(md, "layers_vcol_select_src", text="")
        row.label(icon='RIGHTARROW')
        row.prop(md, "layers_vcol_select_dst", text="")
        row = sub.row(align=True)
        row.prop(md, "layers_uv_select_src", text="")
        row.label(icon='RIGHTARROW')
        row.prop(md, "layers_uv_select_dst", text="")
        col.prop(md, "islands_precision")

    layout.separator()

    split = layout.split(factor=0.333)
    split.prop(md, "use_poly_data")
    use_poly = md.use_poly_data
    row = split.row()
    row.active = use_poly
    row.prop(md, "poly_mapping", text="")
    if use_poly:
        col = layout.column(align=True)
        split = col.split(factor=0.333, align=True)
        sub = split.column(align=True)
        sub.prop(md, "data_types_polys")

    layout.separator()

    split = layout.split()
    col = split.column()
    row = col.row(align=True)
    sub = row.row(align=True)
    sub.active = md.use_max_distance
    sub.prop(md, "max_distance")
    row.prop(md, "use_max_distance", text="", icon='STYLUS_PRESSURE')

    col = split.column()
    col.prop(md, "ray_radius")

    layout.separator()

    split = layout.split()
    col = split.column()
    col.prop(md, "mix_mode")
    col.prop(md, "mix_factor")

    col = split.column()
    row = col.row()
    row.active = bool(md.object)
    row.operator("object.datalayout_transfer", text="Generate Data Layers").modifier = md.name # Changed
    row = col.row(align=True)
    row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
    sub = row.row(align=True)
    sub.active = bool(md.vertex_group)
    sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')


def EXPLODE(layout, ob, md):
    split = layout.split()

    col = split.column()
    col.label(text="Vertex Group:")
    col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
    sub = col.column()
    sub.active = bool(md.vertex_group)
    sub.prop(md, "protect")
    col.label(text="Particle UV")
    col.prop_search(md, "particle_uv", ob.data, "uv_layers", text="")

    col = split.column()
    col.prop(md, "use_edge_cut")
    col.prop(md, "show_unborn")
    col.prop(md, "show_alive")
    col.prop(md, "show_dead")
    col.prop(md, "use_size")

    layout.operator("object.explode_refresh", text="Refresh").modifier = md.name # Changed


def HOOK(layout, ob, md):
    use_falloff = (md.falloff_type != 'NONE')
    split = layout.split()

    col = split.column()
    col.label(text="Object:")
    col.prop(md, "object", text="")
    if md.object and md.object.type == 'ARMATURE':
        col.label(text="Bone:")
        col.prop_search(md, "subtarget", md.object.data, "bones", text="")
    col = split.column()
    col.label(text="Vertex Group:")
    col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

    layout.separator()

    row = layout.row(align=True)
    if use_falloff:
        row.prop(md, "falloff_radius")
    row.prop(md, "strength", slider=True)
    layout.prop(md, "falloff_type")

    col = layout.column()
    if use_falloff:
        if md.falloff_type == 'CURVE':
            col.template_curve_mapping(md, "falloff_curve")

    split = layout.split()

    col = split.column()
    col.prop(md, "use_falloff_uniform")

    if ob.mode == 'EDIT':
        row = col.row(align=True)
        row.operator("object.hook_reset", text="Reset").modifier = md.name # Changed
        row.operator("object.hook_recenter", text="Recenter").modifier = md.name # Changed

        row = layout.row(align=True)
        row.operator("object.hook_select", text="Select").modifier = md.name # Changed
        row.operator("object.hook_assign", text="Assign").modifier = md.name # Changed


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
    row.operator("object.laplaciandeform_bind",
                 text="Unbind" if is_bind else "Bind").modifier = md.name # Changed


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


def MULTIRES(layout, ob, md):
    layout.row().prop(md, "subdivision_type", expand=True)

    split = layout.split()
    col = split.column()
    col.prop(md, "levels", text="Preview")
    col.prop(md, "sculpt_levels", text="Sculpt")
    col.prop(md, "render_levels", text="Render")
    col.prop(md, "quality")

    col = split.column()

    col.enabled = ob.mode != 'EDIT'
    col.operator("object.multires_subdivide", text="Subdivide").modifier = md.name # Changed
    col.operator("object.multires_higher_levels_delete", text="Delete Higher").modifier = md.name # Changed
    col.operator("object.multires_reshape", text="Reshape").modifier = md.name # Changed
    col.operator("object.multires_base_apply", text="Apply Base").modifier = md.name # Changed
    col.prop(md, "uv_smooth", text="")
    col.prop(md, "show_only_control_edges")
    col.prop(md, "use_creases")

    layout.separator()

    col = layout.column()
    row = col.row()
    if md.is_external:
        row.operator("object.multires_external_pack", text="Pack External").modifier = md.name # Changed
        row.label()
        row = col.row()
        row.prop(md, "filepath", text="")
    else:
        row.operator("object.multires_external_save", text="Save External...").modifier = md.name # Changed
        row.label()


def OCEAN(layout, _ob, md):
    if not bpy.app.build_options.mod_oceansim:
        layout.label(text="Built without OceanSim modifier")
        return

    layout.prop(md, "geometry_mode")

    if md.geometry_mode == 'GENERATE':
        row = layout.row()
        row.prop(md, "repeat_x")
        row.prop(md, "repeat_y")

    layout.separator()

    split = layout.split()

    col = split.column()
    col.prop(md, "time")
    col.prop(md, "depth")
    col.prop(md, "random_seed")

    col = split.column()
    col.prop(md, "resolution")
    col.prop(md, "size")
    col.prop(md, "spatial_size")

    layout.label(text="Waves:")

    split = layout.split()

    col = split.column()
    col.prop(md, "choppiness")
    col.prop(md, "wave_scale", text="Scale")
    col.prop(md, "wave_scale_min")
    col.prop(md, "wind_velocity")

    col = split.column()
    col.prop(md, "wave_alignment", text="Alignment")
    sub = col.column()
    sub.active = (md.wave_alignment > 0.0)
    sub.prop(md, "wave_direction", text="Direction")
    sub.prop(md, "damping")

    layout.separator()

    layout.prop(md, "use_normals")

    split = layout.split()

    col = split.column()
    col.prop(md, "use_foam")
    sub = col.row()
    sub.active = md.use_foam
    sub.prop(md, "foam_coverage", text="Coverage")

    col = split.column()
    col.active = md.use_foam
    col.label(text="Foam Data Layer Name:")
    col.prop(md, "foam_layer_name", text="")

    layout.separator()

    # Changed:
    if md.is_cached:
        bake = layout.operator("object.ocean_bake", text="Delete Bake")
        bake.free = True
        bake.modifier = md.name
    else:
        bake = layout.operator("object.ocean_bake")
        bake.free = False
        bake.modifier = md.name

    split = layout.split()
    split.enabled = not md.is_cached

    col = split.column(align=True)
    col.prop(md, "frame_start", text="Start")
    col.prop(md, "frame_end", text="End")

    col = split.column(align=True)
    col.label(text="Cache path:")
    col.prop(md, "filepath", text="")

    split = layout.split()
    split.enabled = not md.is_cached

    col = split.column()
    col.active = md.use_foam
    col.prop(md, "bake_foam_fade")

    col = split.column()


def REMESH(layout, _ob, md):
    # Layout for sculpt-mode-features branch

    if not bpy.app.build_options.mod_remesh:
        layout.label(text="Built without Remesh modifier")
        return

    layout.prop(md, "mode")

    if md.mode not in {'VOXEL', 'QUAD'}:
        row = layout.row()
        row.prop(md, "octree_depth")
        row.prop(md, "scale")

    if md.mode == 'SHARP':
        layout.prop(md, "sharpness")

    if md.mode == 'VOXEL':
        col = layout.column(align=True)
        col.prop(md, "voxel_size")
        col.prop(md, "isovalue")
        col.prop(md, "adaptivity")
        layout.prop(md, "filter_type")
        if md.filter_type != "NONE":
            layout.prop(md, "filter_bias")
            if md.filter_type in {"GAUSSIAN", "MEDIAN", "MEAN"}:
                layout.prop(md, "filter_width")
            if md.filter_type in {"DILATE", "ERODE"}:
                layout.prop(md, "filter_offset_distance")
        row = layout.row()
        row.prop(md, "live_remesh")
        row.prop(md, "smooth_normals")
        row = layout.row()
        row.prop(md, "relax_triangles")
        row.prop(md, "reproject_vertex_paint")
        layout.label(text="CSG Operands")
        layout.operator("remesh.csg_add", text="", icon="ADD").modifier = md.name # Changed
        for i,csg in enumerate(md.csg_operands):
            box = layout.box()
            row = box.row(align=True)
            icon = "HIDE_ON"
            if csg.enabled:
                icon = "HIDE_OFF"
            row.prop(csg, "enabled", text="", icon=icon, emboss=True)
            row.prop(csg, "object", text="")
            row.prop(csg, "operation", text="")
            row = box.row(align=True)
            icon = "RESTRICT_VIEW_ON"
            if csg.sync_voxel_size:
                icon = "RESTRICT_VIEW_OFF"
            row.prop(csg, "use_voxel_percentage", text="", icon='CANCEL', emboss=True)
            if not csg.use_voxel_percentage:
                row.prop(csg, "sync_voxel_size", text="", icon=icon, emboss=True)
                row.prop(csg, "voxel_size")
            else:
                row.prop(csg, "voxel_percentage")
            row.prop(csg, "sampler", text="")

            # Changed:
            csg_remove = row.operator("remesh.csg_remove", text="", icon="REMOVE")
            csg_remove.modifier = md.name
            csg_remove.index = i

            csg_move_up = row.operator("remesh.csg_move_up", text="", icon="TRIA_UP")
            csg_move_up.modifier = md.name
            csg_move_up.index = i

            csg_move_down = row.operator("remesh.csg_move_down", text="", icon="TRIA_DOWN")
            csg_move_down.modifier = md.name
            csg_move_down.index = i
    elif md.mode == 'QUAD':
        col = layout.column(align=True)
        col.prop(md, "gradient_size")
        col.prop(md, "stiffness")
        col.prop(md, "iterations")
        row = layout.row()
        row.prop(md, "live_remesh")
        row.prop(md, "direct_round")
    else:
        layout.prop(md, "use_smooth_shade")
        layout.prop(md, "use_remove_disconnected")
        row = layout.row()
        row.active = md.use_remove_disconnected
        row.prop(md, "threshold")


def SKIN(layout, _ob, md):
    row = layout.row()
    row.operator("object.skin_armature_create", text="Create Armature").modifier = md.name # Changed
    row.operator("mesh.customdata_skin_add")

    layout.separator()

    row = layout.row(align=True)
    row.prop(md, "branch_smoothing")
    row.prop(md, "use_smooth_shade")

    split = layout.split()

    col = split.column()
    col.label(text="Selected Vertices:")
    sub = col.column(align=True)
    sub.operator("object.skin_loose_mark_clear", text="Mark Loose").action = 'MARK'
    sub.operator("object.skin_loose_mark_clear", text="Clear Loose").action = 'CLEAR'

    sub = col.column()
    sub.operator("object.skin_root_mark", text="Mark Root")
    sub.operator("object.skin_radii_equalize", text="Equalize Radii")

    col = split.column()
    col.label(text="Symmetry Axes:")
    col.prop(md, "use_x_symmetry")
    col.prop(md, "use_y_symmetry")
    col.prop(md, "use_z_symmetry")


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