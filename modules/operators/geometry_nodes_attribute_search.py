from bpy.props import *
from bpy.types import Operator

from ..utils import get_ml_active_object


def attr_or_vertex_group_name_enum_items(self, context):
    ob = get_ml_active_object()
    groups = [(group.name, f"Point > {group.name}", "")
              for group in ob.vertex_groups]
    attrs = [(attr.name, f"{attr.domain.capitalize()} > {attr.name}", "")
             for attr in ob.data.attributes]
    return groups + attrs


class OBJECT_OT_ml_geometry_nodes_attribute_search(Operator):
    """This operator is a workaround for the issue that currently the
    native attribute search is not accessible through Python. This
    operator is used in Geometry Nodes modifier's layout next to every
    attribute name field to search attributes or vertex groups and
    assing one to the appropriate property. The reasons why a regular
    search field can't be used are that with it it's not possible to
    show both attributes and vertex groups and that new attributes can't
    be added.
    """
    bl_idname = "object.ml_geometry_nodes_attribute_search"
    bl_label = "Attribute Search"
    bl_description = ("Search attributes and vertex groups")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}
    bl_property = "attr_or_vertex_group_name"

    attr_or_vertex_group_name: EnumProperty(items=attr_or_vertex_group_name_enum_items)
    property_name: StringProperty()

    def execute(self, context):
        ob = get_ml_active_object()
        active_mod = ob.modifiers[ob.ml_modifier_active_index]
        setattr(active_mod, self.property_name, self.attr_or_vertex_group_name)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'CANCELLED'}
