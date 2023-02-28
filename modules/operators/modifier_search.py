import bpy
from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object, object_type_has_modifiers


def modifier_enum_items(self, context):
    ob = get_ml_active_object()
    ml_props = context.window_manager.modifier_list

    if ob.type == 'MESH':
        mods = ml_props.mesh_modifiers
    elif ob.type in {'CURVE', 'FONT'}:
        mods = ml_props.curve_text_modifiers
    elif ob.type == 'CURVES':
        mods = ml_props.curves_modifiers
    elif ob.type == 'LATTICE':
        mods = ml_props.lattice_modifiers
    elif ob.type == 'POINTCLOUD':
        mods = ml_props.pointcloud_modifiers
    elif ob.type == 'SURFACE':
        mods = ml_props.surface_modifiers
    elif ob.type == 'VOLUME':
        mods = ml_props.volume_modifiers

    names = mods.keys()
    return [(name, name, "") for name in names]


class OBJECT_OT_ml_add_modifier_from_search(Operator):
    bl_idname = "object.ml_modifier_add_from_search"
    bl_label = "Add Modifier from Search"
    bl_description = "Search for a modifier and add it to the active object."
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "modifier_name"

    modifier_name: EnumProperty(items=modifier_enum_items, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        ob = get_ml_active_object()

        if not ob:
            return False

        if not object_type_has_modifiers(ob):
            return False

        return ob.library is None or ob.override_library is not None

    def execute(self, context):
        ml_props = context.window_manager.modifier_list
        mod_type = ml_props.all_modifiers[self.modifier_name].value
        bpy.ops.object.ml_modifier_add(modifier_type=mod_type)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'CANCELLED'}
