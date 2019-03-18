from bl_ui.properties_data_mesh import (
    MESH_UL_vgroups,
    MESH_MT_vertex_group_context_menu
)


def vertex_groups_ui(context, layout, num_of_rows=5):
    # Copy-paste from Blender

    ob = context.object
    group = ob.vertex_groups.active

    row = layout.row()
    row.template_list("MESH_UL_vgroups", "", ob, "vertex_groups", ob.vertex_groups, "active_index", rows=num_of_rows)

    col = row.column(align=True)

    col.operator("object.vertex_group_add", icon='ADD', text="")
    props = col.operator("object.vertex_group_remove", icon='REMOVE', text="")
    props.all_unlocked = props.all = False

    col.separator()

    col.menu("MESH_MT_vertex_group_context_menu", icon='DOWNARROW_HLT', text="")

    if group:
        col.separator()
        col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

    if ob.vertex_groups and (ob.mode == 'EDIT' or (ob.mode == 'WEIGHT_PAINT' and ob.type == 'MESH' and ob.data.use_paint_mask_vertex)):
        row = layout.row()

        sub = row.row(align=True)
        sub.operator("object.vertex_group_assign", text="Assign")
        sub.operator("object.vertex_group_remove_from", text="Remove")

        sub = row.row(align=True)
        sub.operator("object.vertex_group_select", text="Select")
        sub.operator("object.vertex_group_deselect", text="Deselect")

        layout.prop(context.tool_settings, "vertex_group_weight", text="Weight")



