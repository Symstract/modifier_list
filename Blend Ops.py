# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#Not PEP8 compliant

bl_info = {
    "name": "Blend Ops",
    "description": "UI Replacement addon that provides substance integration options",
    "author": "Nick Bosse",
    "version": (0, 1, 1, 6),
    "blender": (2, 79, 0),
    "location": "View 3D > Q",
    "category": "3D View",
    "dependencies": "Q Hotkey, Node Group: 'NodeGroup', BoolTools addon"}

import bpy
import os
import sys
from bpy.types import Menu, Operator


class BlackOpsMeshMenu(Menu):
    bl_label = "Add Black Ops Mesh"
    bl_idname = "view3d.black_ops.sub_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.black_plane", text="Black Plane", icon="MESH_GRID")
        layout.operator("mesh.black_cube", text="Black Cube", icon="SNAP_VOLUME")

        layout.separator()

        layout.operator("mesh.def_eight", text="8 Cylinder", icon="MESH_CYLINDER")
        layout.operator("mesh.def_sixteen", text="16 Cylinder", icon="MESH_CYLINDER")
        layout.operator("mesh.def_thirty_two", text="32 Cylinder", icon="MESH_CYLINDER")

        layout.separator()

        layout.operator("mesh.def_sphere_two", text="2 Cube Sphere", icon="WIRE")
        layout.operator("mesh.def_sphere_four", text="4 Cube Sphere", icon="WIRE")
        layout.operator("mesh.def_sphere_eight", text="8 Cube Sphere", icon="WIRE")
#
#
# class BlackRemove(Operator):
#     bl_idname = "object.black_remove"
#     bl_label = "Black Remove"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[BlackModifierMenu.current_index] = False
#         bpy.ops.object.modifier_remove(modifier=BlackModifierMenu.current_mod)
#         return {"FINISHED"}
#
#
# class BlackArray(Operator):
#     bl_idname = "object.black_array"
#     bl_label = "Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     #tag = ""
#     #prop21 = bpy.props.BoolProperty()
#
#     is_on = False
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         #self.__class__.tag = "Array"
#         #self.report({"INFO"}, str(self.__class__.tag))
#         BlackModifierMenu.mod_bool_list[0] = True
#         #self.__class__.is_on = True
#         bpy.ops.object.modifier_add(type="ARRAY")
#         return {'FINISHED'}
#
#     #def invoke(self, context, event):
#     #    return context.window_manager.invoke_props_dialog(self)
#
#     #def draw(self, context):
#     #    layout = self.layout
#         #layout.label("Are you sure you want to add?")
#         #layout.prop(self, "prop21", "IT WORKED!")
#
#
# class BlackBevel(Operator):
#     bl_idname = "object.add_black_bevel"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     #prop21 = bpy.props.BoolProperty()
#     bevel_segments = 3
#     bevel_width = 0.1
#     bevel_clamp = False
#     bevel_limit = "2"
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#
#     def execute(self, context):
#         #BlackArray.tag = "Bevel"
#         BlackModifierMenu.mod_bool_list[1] = True
#         bpy.ops.object.modifier_add(type="BEVEL")
#         bpy.context.object.modifiers["Bevel"].segments = 3
#         self.__class__.bevel_segments = 3
#         bpy.context.object.modifiers["Bevel"].width = 0.05
#         self.__class__.bevel_width = 0.05
#         bpy.context.object.modifiers["Bevel"].use_clamp_overlap = True
#         self.__class__.bevel_clamp = True
#         bpy.context.object.modifiers["Bevel"].limit_method = 'ANGLE'
#         self.__class__.bevel_limit = "2"
#         return {"FINISHED"}
#     #def invoke(self, context, event):
#      #   return context.window_manager.invoke_props_dialog(self)
#
#     #def draw(self, context):
#      #   layout = self.layout
#      #   layout.prop(self, "prop21", "IT WORKED!")
#
#
# class BlackBoolean(Operator):
#     bl_idname = "object.add_black_boolean"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[2] = True
#         bpy.ops.object.modifier_add(type="BOOLEAN")
#         return {'FINISHED'}
#
#
# class BlackCurve(Operator):
#     bl_idname = "object.add_black_curve"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     prop21 = bpy.props.BoolProperty()
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[3] = True
#         bpy.ops.object.modifier_add(type="CURVE")
#         return {'FINISHED'}
#
#
# class BlackDecimate(Operator):
#     bl_idname = "object.add_black_decimate"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     prop21 = bpy.props.BoolProperty()
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[4] = True
#         bpy.ops.object.modifier_add(type="DECIMATE")
#         return {'FINISHED'}
#
#
# class BlackEdgeSplit(Operator):
#     bl_idname = "object.add_black_edge_split"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     prop21 = bpy.props.BoolProperty()
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[5] = True
#         bpy.ops.object.modifier_add(type="EDGE_SPLIT")
#         return {'FINISHED'}
#
#
# class BlackMirror(Operator):
#     bl_idname = "object.add_black_mirror"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     prop21 = bpy.props.BoolProperty()
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[6] = True
#         bpy.ops.object.modifier_add(type="MIRROR")
#         return {'FINISHED'}
#
#
# class BlackMultires(Operator):
#     bl_idname = "object.add_black_multi"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     prop21 = bpy.props.BoolProperty()
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[7] = True
#         bpy.ops.object.modifier_add(type="MULTIRES")
#         return {'FINISHED'}
#
#
# class BlackRemesh(Operator):
#     bl_idname = "object.add_black_remesh"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     prop21 = bpy.props.BoolProperty()
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[8] = True
#         bpy.ops.object.modifier_add(type="REMESH")
#         return {'FINISHED'}
#
#
# class BlackSolidify(Operator):
#     bl_idname = "object.add_black_solid"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     prop21 = bpy.props.BoolProperty()
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[9] = True
#         bpy.ops.object.modifier_add(type="SOLIDIFY")
#         return {'FINISHED'}
#
#
# class BlackSubsurf(Operator):
#     bl_idname = "object.add_black_sub_d"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     prop21 = bpy.props.BoolProperty()
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[10] = True
#         bpy.ops.object.modifier_add(type="SUBSURF")
#         return {'FINISHED'}
#
#
# class BlackShrinkwrap(Operator):
#     bl_idname = "object.add_black_shrink"
#     bl_label = "Add Black Array"
#     bl_options = {'REGISTER', 'INTERNAL'}
#
#     prop21 = bpy.props.BoolProperty()
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         BlackModifierMenu.mod_bool_list[11] = True
#         bpy.ops.object.modifier_add(type="SHRINKWRAP")
#         return {'FINISHED'}
#
#
# class BlackModifierMenu(Operator):
#     bl_idname = "view3d.black_modifier"
#     bl_label = "Add Black Modifier"
#     bl_options = {'REGISTER', 'INTERNAL'}
#     add_icon = "MOD_ARRAY"
#     current_mod = "Array"
#     current_index = 0
#     mod_enum_items = (("0", "", "", "MOD_ARRAY", 0), ("1", "", "", "MOD_BEVEL", 1), ("2", "", "", "MOD_BOOLEAN", 2),
#                       ("3", "", "", "MOD_CURVE", 3), ("4", "", "", "MOD_DECIM", 4), ("5", "", "", "MOD_EDGESPLIT", 5),
#                       ("6", "", "", "MOD_MIRROR", 6), ("7", "", "", "MOD_MULTIRES", 7), ("8", "", "", "MOD_REMESH", 8),
#                       ("9", "", "", "MOD_SOLIDIFY", 9), ("10", "", "", "MOD_SUBSURF", 10), ("11", "", "", "MOD_SHRINKWRAP", 11))
#     prop4 = bpy.props.EnumProperty(items = mod_enum_items)
#     prop_bevel_1 = bpy.props.FloatProperty(min=0, max=50, default=BlackBevel.bevel_width, precision = 4, step=1)
#     prop_bevel_2 = bpy.props.IntProperty(min=0, max=50, default=BlackBevel.bevel_segments)
#     prop_bevel_3 = bpy.props.BoolProperty(default=BlackBevel.bevel_clamp)
#     enum_items = (("0", "None", ""), ("1", "Angle (A)", ""), ("2", "Weight (W)", ""), ("3", "A + W", ""))
#     prop_bevel_4 = bpy.props.EnumProperty(items=enum_items, default=BlackBevel.bevel_limit)
#     prop6 = bpy.props.BoolProperty(default=True)
#     prop7 = bpy.props.BoolProperty(default=True)
#     prop8 = bpy.props.BoolProperty(default=True)
#     mod_bool_list = [False, False, False, False, False, False, False, False, False, False, False, False]
#     mod_change_list = [False, False, False, False, False, False, False, False, False, False, False, False]
#
#     @classmethod
#     def poll(cls, context):
#         return True
#
#     def execute(self, context):
#         #Update function
#         #
#         #Bevel
#         #
#         #bpy.context.object.modifiers["Bevel"].segments = BlackBevel.bevel_segments
#         #self.report({'INFO'}, "Black Modifier Menu")
#
#         return {'FINISHED'}
#
#     def check(self, context):
#         return True
#
#     def invoke(self, context, event):
#         return context.window_manager.invoke_props_dialog(self)
#
#     def draw(self, context):
#         layout = self.layout
#         self.__class__.mod_bool_list = [False, False, False, False, False, False, False, False, False, False, False, False]
#         col = layout.column(align=True)
#         col.label("Black Modifiers:")
#         # row.operator("object.black_array", text="", icon="MOD_ARRAY")
#         # row.operator("object.add_black_bevel", text="", icon="MOD_BEVEL")
#         # row.operator("mesh.primitive_cube_add", text="", icon="MOD_BOOLEAN")
#         # row.operator("mesh.primitive_cube_add", text="", icon="MOD_CURVE")
#         # row.operator("mesh.primitive_cylinder_add", text="", icon="MOD_DECIM")
#         # row.operator("mesh.primitive_cylinder_add", text="", icon="MOD_EDGESPLIT")
#         # row.operator("mesh.primitive_cube_add", text="", icon="MOD_MIRROR")
#         # row.operator("mesh.primitive_cube_add", text="", icon="MOD_MULTIRES")
#         # row.operator("mesh.primitive_cube_add", text="", icon="MOD_REMESH")
#         # row.operator("mesh.primitive_cube_add", text="", icon="MOD_SOLIDIFY")
#         # row.operator("mesh.primitive_cube_add", text="", icon="MOD_SUBSURF")
#         # row.operator("mesh.primitive_cube_add", text="", icon="MOD_SHRINKWRAP")
#         col.operator("object.origin_mirror", text="Origin Mirror", icon="MOD_MIRROR")
#         col.operator("edge.set_bevel_sharp", text="Sharp Bevel", icon="MOD_BEVEL")
#         col.operator("object.bevel_w_weight", text="Angle Bevel", icon="MOD_BEVEL")
#         col.operator("object.curve_array", text="Curve Array", icon="MOD_CURVE")
#         col.operator("object.circle_array", text="Circle Array", icon="GROUP_VERTEX")
#         #layout.prop(self, "test_bool")
#         #if self.test_bool:
#         #    layout.label("Tickbox is on")
#         #col.operator("object.add_black_array", text="Change name", icon="MOD_SUBSURF")
#         #layout.label(text=str(BlackArray.tag))
#         #layout.prop(self, "prop1", "Width")
#         #layout.prop(self, "prop2", "Segments")
#         #layout.prop(self, "prop3", "Clamp Overlap")
#         col.label(text="Stock Modifiers:")
#         col.row(align=True).prop(self, "prop4", expand=True)
#         if int(self.prop4) == 0:
#             #self.report({"INFO"}, "THERE IS A MODIFIER!")
#             self.__class__.add_icon = "MOD_ARRAY"
#             self.__class__.current_mod = "Array"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackArray.bl_idname
#         elif int(self.prop4) == 1:
#             self.__class__.add_icon = "MOD_BEVEL"
#             self.__class__.current_mod = "Bevel"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackBevel.bl_idname
#         elif int(self.prop4) == 2:
#             self.__class__.add_icon = "MOD_BOOLEAN"
#             self.__class__.current_mod = "Boolean"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackBoolean.bl_idname
#         elif int(self.prop4) == 3:
#             self.__class__.add_icon = "MOD_CURVE"
#             self.__class__.current_mod = "Curve"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackCurve.bl_idname
#         elif int(self.prop4) == 4:
#             self.__class__.add_icon = "MOD_DECIM"
#             self.__class__.current_mod = "Decimate"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackDecimate.bl_idname
#         elif int(self.prop4) == 5:
#             self.__class__.add_icon = "MOD_EDGESPLIT"
#             self.__class__.current_mod = "EdgeSplit"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackEdgeSplit.bl_idname
#         elif int(self.prop4) == 6:
#             self.__class__.add_icon = "MOD_MIRROR"
#             self.__class__.current_mod = "Mirror"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackMirror.bl_idname
#         elif int(self.prop4) == 7:
#             self.__class__.add_icon = "MOD_MULTIRES"
#             self.__class__.current_mod = "Multires"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackMultires.bl_idname
#         elif int(self.prop4) == 8:
#             self.__class__.add_icon = "MOD_REMESH"
#             self.__class__.current_mod = "Remesh"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackRemesh.bl_idname
#         elif int(self.prop4) == 9:
#             self.__class__.add_icon = "MOD_SOLIDIFY"
#             self.__class__.current_mod = "Solidify"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackSolidify.bl_idname
#         elif int(self.prop4) == 10:
#             self.__class__.add_icon = "MOD_SUBSURF"
#             self.__class__.current_mod = "Subsurf"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackSubsurf.bl_idname
#         elif int(self.prop4) == 11:
#             self.__class__.add_icon = "MOD_SHRINKWRAP"
#             self.__class__.current_mod = "Shrinkwrap"
#             self.__class__.current_index = int(self.prop4)
#             self.__class__.current_ob = BlackShrinkwrap.bl_idname
#         obj = bpy.context.object
#         for modifier in obj.modifiers:
#             #self.report({"INFO"}, "THERE IS A MODIFIER!")
#             if modifier.type == "ARRAY":
#                 self.__class__.mod_bool_list[0] = True
#             elif modifier.type == "BEVEL":
#                 self.__class__.mod_bool_list[1] = True
#             elif modifier.type == "BOOLEAN":
#                 self.__class__.mod_bool_list[2] = True
#             elif modifier.type == "CURVE":
#                 self.__class__.mod_bool_list[3] = True
#             elif modifier.type == "DECIMATE":
#                 self.__class__.mod_bool_list[4] = True
#             elif modifier.type == "EDGE_SPLIT":
#                 self.__class__.mod_bool_list[5] = True
#             elif modifier.type == "MIRROR":
#                 self.__class__.mod_bool_list[6] = True
#             elif modifier.type == "MULTIRES":
#                 self.__class__.mod_bool_list[7] = True
#             elif modifier.type == "REMESH":
#                 self.__class__.mod_bool_list[8] = True
#             elif modifier.type == "SOLIDIFY":
#                 self.__class__.mod_bool_list[9] = True
#             elif modifier.type == "SUBSURF":
#                 self.__class__.mod_bool_list[10] = True
#             elif modifier.type == "SHRINKWRAP":
#                 self.__class__.mod_bool_list[11] = True
#
#         if self.__class__.mod_bool_list[0] and int(self.prop4) == 0:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         elif self.__class__.mod_bool_list[1] and int(self.prop4) == 1:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#             # layout.prop(self, "prop_bevel_1", "Width")
#             # layout.prop(self, "prop_bevel_2", "Segments")
#             # layout.prop(self, "prop_bevel_3", "Clamp Overlap")
#             # layout.label("Limit Method:")
#             # layout.prop(self, "prop_bevel_4", expand=True)
#         elif self.__class__.mod_bool_list[2] and int(self.prop4) == 2:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         elif self.__class__.mod_bool_list[3] and int(self.prop4) == 3:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         elif self.__class__.mod_bool_list[4] and int(self.prop4) == 4:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         elif self.__class__.mod_bool_list[5] and int(self.prop4) == 5:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         elif self.__class__.mod_bool_list[6] and int(self.prop4) == 6:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         elif self.__class__.mod_bool_list[7] and int(self.prop4) == 7:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         elif self.__class__.mod_bool_list[8] and int(self.prop4) == 8:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         elif self.__class__.mod_bool_list[9] and int(self.prop4) == 9:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         elif self.__class__.mod_bool_list[10] and int(self.prop4) == 10:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         elif self.__class__.mod_bool_list[11] and int(self.prop4) == 11:
#             row = col.row(align=True)
#             row.label(self.__class__.current_mod)
#             row.operator("object.modifier_apply", text="Apply").modifier = self.__class__.current_mod
#             row.operator("object.black_remove", text="Remove")
#             # row.prop(self, "prop6", "", icon="SCENE", toggle=True)
#             # row.prop(self, "prop7", "", icon="RESTRICT_VIEW_OFF", toggle=True)
#             # row.prop(self, "prop8", "", icon="EDITMODE_HLT", toggle=True)
#         else:
#             layout.operator(self.__class__.current_ob, text="Add " + self.__class__.current_mod, icon=self.__class__.add_icon)
#         # if BlackArray.is_on:
#         #     layout.label("Array")
#         #     layout.operator("object.black_array", text="Remove", icon="MOD_SUBSURF")
#         # else:
#         #     layout.operator("object.black_array", text="Add", icon="MOD_SUBSURF")
#         #layout.row().prop(self, "limit_method", expand = True)
#         #layout.prop(self, "prop4", "Limit Method", "Des", items = [("FIRST", "First", "desc"), ("SECOND", "Second", 'Desc')]


#class BlackOpsBackgroundMenu(Menu):
    # bl_label = "Add Background Image"
    # bl_idname = "view3d.black_ops.sub_menu.two"
    #
    # def draw(self, context):
    #     layout = self.layout
    #     layout.operator("bg_image.top", text="Add Top Image", icon="AXIS_TOP")
    #     layout.operator("bg_image.side", text="Add Side Image", icon="AXIS_SIDE")
    #     layout.operator("bg_image.front", text="Add Front Image", icon="AXIS_FRONT")

#class BlackOpsModifierMenu(Menu):
    # bl_label = "Add Modifier"
    # bl_idname = "view3d.black_ops.sub_menu.three"
    #
    # def draw(self, context):
    #     layout = self.layout
    #     layout.operator("object.modifier_add(type='ARRAY')", text="Array", icon="MOD_ARRAY")
    #     layout.operator("bpy.ops.object.modifier_add(type='BEVEL')", text="Bevel", icon="MOD_BEVEL")
    #     layout.operator("add_black_modifier.decim", text="Decimate", icon="MOD_DECIM")
    #     layout.operator("add_black_modifier.edgesplit", text="Edge Split", icon="MOD_EDGESPLIT")
    #     layout.operator("add_black_modifier.", text="Mirror", icon="MOD_MIRROR")
    #     layout.operator("add_black_modifier.array", text="Multires", icon="MOD_MULTIRES")
    #     layout.operator("add_black_modifier.array", text="Solidify", icon="MOD_SOLIDIFY")
    #     layout.operator("add_black_modifier.array", text="Subsurf", icon="MOD_SUBSURF")
    #     layout.operator("add_black_modifier.array", text="Curve", icon="MOD_CURVE")
    #     layout.operator("add_black_modifier.array", text="Shrinkwrap", icon="MOD_SHRINKWRAP")


#class BlackBevel(Menu):
    # bl_label = "Black Ops Bevel"
    # bl_idname = "viwe3d.black_bevel"
    #
    # def draw(self, context):
    #     layout= self.layout
    #     layout.operator()

class BlackOps(Menu):
    bl_label = "Black Ops Menu"
    bl_idname = "view3d.black_ops"
    # Function that creates the dropdown menu
    def draw(self, context):
        layout = self.layout

        layout.menu(BlackOpsMeshMenu.bl_idname, icon="MESH_GRID")
        #layout.menu(BlackOpsBackgroundMenu.bl_idname, icon="FILE_IMAGE")

        layout.separator()
        
        layout.operator("object.shade_sharp", text="Sharp Shade", icon = "FACESEL")

        layout.separator()

        layout.label(text="Black Modifiers [Shift Ctrl Alt B]", icon="MODIFIER")
        layout.operator("object.origin_mirror", text="Origin Mirror", icon = "MOD_MIRROR")
        #layout.operator("object.remove_mirror", text="Unmirror Object", icon="GROUP")

        layout.operator("object.bevel_w_weight", text="Bevel", icon="MOD_BEVEL")
        layout.operator("edge.set_bevel_sharp", text="Bevel Sharp", icon = "SNAP_EDGE")
        layout.operator("object.black_slice", text="Split Boolean", icon = "ROTATECENTER")
        layout.operator("object.clear_not_sharp", text="Clear Not Sharp", icon = "SNAP_EDGE")
        layout.operator("object.curve_array", text="Curve Array", icon="MOD_CURVE")
        layout.operator("object.circle_array", text="Circle Array", icon="GROUP_VERTEX")
        #layout.operator("object.remove_bevel", text="Unbevel Object", icon = "SNAP_VOLUME")

        layout.separator()

        layout.operator("object.boolean_mode", text="Boolean Mode", icon = "MOD_BOOLEAN")
        layout.operator("object.exit_boolean_mode", text="Exit Boolean Mode", icon="X")

        layout.operator("object.mod_apply", text="Apply Modifiers", icon = "MODIFIER")
        layout.operator("object.mod_apply_all", text="Apply Modifiers to All", icon = "MODIFIER")
        
        layout.separator()

        layout.operator("object.pack_unwrap", text="Pack Unwrap", icon="UV_ISLANDSEL")
        layout.operator("object.sharp_unwrap", text="Sharp Unwrap", icon = "UV_EDGESEL")
        layout.operator("object.cube_unwrap", text="Cube Unwrap", icon = "UV_FACESEL")
        
        layout.separator()

        layout.operator("object.create_tex_set", text="Create Texture Set", icon = "POTATO")
        layout.operator("scene.create_mat_sets", text="Create Material Sets", icon="SMOOTH")
        layout.operator("scene.clear_mat_sets", text="Clear Material Sets", icon="SOLID")
        layout.operator("object.id_create", text="Create Scene ID Map", icon = "SEQ_CHROMA_SCOPE")

        layout.separator()

        layout.operator("object.sharpShade", text="Import Substance", icon = "IMPORT")
        layout.operator("scene.substance_export", text="Export Scene for Substance", icon = "EXPORT")
# boolean_mode = False
# initial_name = ""
# duplicate_name = ""


# def draw_item(self, context):
#     layout = self.layout
#     layout.menu(blackOps.bl_idname)
#     layout.menu(blackOpsDefined.bl_idname)

class SharpShading(Operator):
    """Shade smooth with auto smooth enabled"""
    bl_idname = "object.shade_sharp" 
    bl_label = "Sharp Shade"
    
    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    #Function section for sharp shading
    def execute(self, context):
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.610865
        return {'FINISHED'}

class OriginMirror(Operator):
    """Origin to 3D cursor, mirror on x axis with clipping"""
    bl_idname = "object.origin_mirror" 
    bl_label = "Origin Mirror"
    
    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        bpy.ops.object.modifier_add(type="MIRROR")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        return {'FINISHED'}

class BevelWeight(Operator):
    bl_idname = "object.bevel_w_weight"
    bl_label = "Bevel with weight"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Bevel"].limit_method = "ANGLE"
        return {'FINISHED'}

class SetBevelEdgeAll(Operator):
    """Adds bevel modifier with weight setting and all edge weights to 1 and all sharp edges marked"""
    bl_idname = "edge.set_bevel_sharp"
    bl_label = "Set All Bevel Edge"
    bl_context = "editmode"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    
    def execute(self, context):
        #Add bevel modifier with weight setting then set all sharp edge weights to 1 furthermore go into edit mode and make
        #all sharp edges marked sharp
        #Add modifier
        obj = bpy.context.object

        if not obj.modifiers:
            bpy.ops.object.modifier_add(type="BEVEL")
            bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
            bpy.context.object.modifiers["Bevel"].segments = 3
            bpy.context.object.modifiers["Bevel"].use_clamp_overlap = False
            bpy.context.object.modifiers["Bevel"].width = 0.05
            ob = bpy.context.object
            me = ob.data
            me.use_customdata_edge_bevel = True
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.mesh.edges_select_sharp()
            bpy.ops.mesh.mark_sharp()
            bpy.ops.object.editmode_toggle()
            for e in me.edges:
                if e.use_edge_sharp:
                    e.bevel_weight = 1
                else:
                    pass
            return {'FINISHED'}
        else:
            bevel = False
            for modifier in obj.modifiers:
                if modifier.type == "BEVEL":
                    bevel = True
                    me = obj.data
                    me.use_customdata_edge_bevel = True
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action="DESELECT")
                    bpy.ops.mesh.edges_select_sharp()
                    bpy.ops.mesh.mark_sharp()
                    bpy.ops.object.editmode_toggle()
                    for e in me.edges:
                        if e.use_edge_sharp:
                            e.bevel_weight = 1
            if bevel is True:
                pass
            else:
                bpy.ops.object.modifier_add(type="BEVEL")
                bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
                bpy.context.object.modifiers["Bevel"].segments = 3
                bpy.context.object.modifiers["Bevel"].use_clamp_overlap = False
                bpy.context.object.modifiers["Bevel"].width = 0.05
                ob = bpy.context.object
                me = ob.data
                me.use_customdata_edge_bevel = True
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.edges_select_sharp()
                bpy.ops.mesh.mark_sharp()
                bpy.ops.object.editmode_toggle()
                for e in me.edges:
                    if e.use_edge_sharp:
                        e.bevel_weight = 1
                    else:
                        pass
            return {"FINISHED"}
        #bpy.ops.object.modifier_add(type="BEVEL")
        #Set limit to weight
        #bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"

class BlackSlice(Operator):
    bl_idname = "object.black_slice"
    bl_label = "Black Split"

    cutter_object = ""
    cutter_duplicate_object = ""
    difference_object = ""
    intersect_object = ""


    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        #cutter_object = bpy.context.object.
        selection_names = [obj.name for obj in bpy.context.selected_objects]
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.modifier_apply(modifier="Auto Boolean")
        bpy.ops.object.modifier_apply(modifier="Auto Boolean")
        bpy.ops.btool.auto_slice(solver='BMESH')
        bpy.data.objects[selection_names[1]].select = True
        bpy.ops.object.join()
        return {"FINISHED"}

class ClearNotSharp(Operator):
    bl_idname = "object.clear_not_sharp"
    bl_label = "Clear Not Sharp"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        #Add bevel modifier with weight setting then set all sharp edge weights to 1 furthermore go into edit mode and make
        #all sharp edges marked sharp
        #Add modifier
        obj = bpy.context.object
        for modifier in obj.modifiers:
            if modifier.type == "BEVEL":
                ob = bpy.context.object
                me = ob.data
                me.use_customdata_edge_bevel = True
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                bpy.ops.mesh.edges_select_sharp()
                bpy.ops.mesh.select_all(action="INVERT")
                bpy.ops.mesh.mark_sharp(clear=True)
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.object.editmode_toggle()
                for e in me.edges:
                    if e.use_edge_sharp:
                        e.bevel_weight = 1
                    else:
                        e.bevel_weight = 0
                return {'FINISHED'}
            else:
                ob = bpy.context.object
                me = ob.data
                me.use_customdata_edge_bevel = True
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                bpy.ops.mesh.edges_select_sharp()
                bpy.ops.mesh.select_all(action="INVERT")
                bpy.ops.mesh.mark_sharp(clear=True)
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.object.editmode_toggle()
                for e in me.edges:
                    if e.use_edge_sharp:
                        e.bevel_weight = 1
                    else:
                        e.bevel_weight = 0
                return {"FINISHED"}

# class UnBevel(Operator):
#     bl_idname = "object.remove_bevel"
#     bl_label = "Unbevel"
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         obj = bpy.context.object
#         for modifier in obj.modifiers:
#             if modifier.type == "BEVEL":
#                 bpy.ops.object.modifier_remove(modifier="Bevel")
#             else:
#                 pass
#         bpy.ops.object.editmode_toggle()
#         bpy.ops.mesh.select_all(action="DESELECT")
#         bpy.ops.mesh.edges_select_sharp()
#         bpy.ops.mesh.mark_sharp(clear=True)
#         bpy.ops.object.editmode_toggle()
#         return {"FINISHED"}
#
# class UnMirror(Operator):
#     bl_idname = "object.remove_mirror"
#     bl_label = "Unmirror"
#
#     @classmethod
#     def poll(cls, context):
#         if bpy.context.object == None:
#             return False
#         else:
#             current_mode = bpy.context.object.mode
#             return current_mode == "OBJECT"
#
#     def execute(self, context):
#         obj = bpy.context.object
#         for modifier in obj.modifiers:
#             if modifier.type == "MIRROR":
#                 bpy.ops.object.modifier_remove(modifier="Mirror")
#             else:
#                 pass
#         bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
#         return {"FINISHED"}

class CircleArray(Operator):
    bl_idname = "object.circle_array"
    bl_label = "Circle Array"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.modifier_add(type="ARRAY")
        circle_array_object = bpy.context.object.name
        bpy.context.object.modifiers["Array"].count = 8
        bpy.context.object.modifiers["Array"].use_relative_offset = False
        bpy.context.object.modifiers["Array"].use_object_offset = True
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        bpy.ops.transform.rotate(value=0.7854, axis=(0, 0, 1), constraint_axis=(False, False, True),
                                 constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                                 proportional_edit_falloff='SMOOTH', proportional_size=1)
        empty_name = bpy.context.object.name
        bpy.data.objects[empty_name].select = False
        #bpy.data.objects[empty_name].select = True
        #bpy.context.scene.objects.active = bpy.data.objects[empty_name]
        bpy.data.objects[circle_array_object].select = True
        bpy.context.scene.objects.active = bpy.data.objects[circle_array_object]
        bpy.context.object.modifiers["Array"].offset_object = bpy.data.objects[empty_name]
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        # bpy.data.objects[empty_name].select = True
        # bpy.context.scene.objects.active = bpy.data.objects[empty_name]
        # bpy.ops.transform.rotate(value=1.5708, axis=(0, 0, 1), constraint_axis=(False, False, True),
        #                          constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
        #                          proportional_edit_falloff='SMOOTH', proportional_size=1)
        #bpy.context.object.modifiers["Array"].offset_object = bpy.data.object[empty_name]

        #empty_rotation = bpy.context.scene.objects.modifiers["Array"].count

        return {"FINISHED"}


class CurveArray(Operator):
    bl_idname = "object.curve_array"
    bl_label = "Curve Array"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.modifier_add(type="ARRAY")
        curve_array_object = bpy.context.object.name
        bpy.context.object.modifiers["Array"].count = 4
        bpy.context.object.modifiers["Array"].use_relative_offset = False
        bpy.context.object.modifiers["Array"].use_object_offset = True
        bpy.ops.curve.primitive_bezier_curve_add(view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
        True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
        False, False, False, False))
        curve_name = bpy.context.object.name
        bpy.data.objects[curve_name].select = False
        bpy.data.objects[curve_array_object].select = True
        bpy.context.scene.objects.active = bpy.data.objects[curve_array_object]
        bpy.context.object.modifiers["Array"].offset_object = bpy.data.objects[curve_name]
        bpy.ops.object.modifier_add(type='CURVE')
        bpy.context.object.modifiers["Curve"].object = bpy.data.objects[curve_name]
        return {"FINISHED"}


class BlackPlane(Operator):
    bl_idname = "mesh.black_plane"
    bl_label = "Black Plane Add"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        verts = [
            (0, 1, 0),
            (1, 1, 0),
            (1, -1, 0),
            (0, -1, 0)
        ]

        edges = []

        faces = [
            (3, 2, 1, 0)
        ]

        mesh_data = bpy.data.meshes.new("cube_mesh_data")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Black Plane", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].width = 0.025
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        return {"FINISHED"}


class BlackCube(Operator):
    bl_label = "Black Cube Add"
    bl_idname = "mesh.black_cube"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    def execute(self, context):
        verts = [
            (0, 1, -1),
            (1, 1, -1),
            (1, -1, -1),
            (0, -1, -1),
            (0, 1, 1),
            (1, 1, 1),
            (1, -1, 1),
            (0, -1, 1)
        ]

        edges = []

        faces = [
            (0, 1, 2, 3),
            (7, 6, 5, 4),
            (2, 6, 7, 3),
            (1, 5, 6, 2),
            (0, 4, 5, 1)
        ]

        mesh_data = bpy.data.meshes.new("cube_mesh_data")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Black Cube", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].width = 0.025
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        return {"FINISHED"}


class OneCylinder(Operator):
    bl_idname = "mesh.def_eight"
    bl_label = "Defined Cylinder Add"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    def execute(self, context):
        #bpy.ops.mesh.primitive_cylinder_add(vertices=8)
        verts = [
            (0,1,-1),
            (0.7071, 0.7071,-1),
            (1,0,-1),
            (0.7071, -0.7071, -1),
            (0,-1,-1),
            #separator
            (0, 1, 1),
            (0.7071, 0.7071, 1),
            (1, 0, 1),
            (0.7071, -0.7071, 1),
            (0,-1,1)
        ]

        edges = []

        faces = [
            (0,1,2,3,4),
            (9,8,7,6,5),
            (3,8,9,4),
            (2,7,8,3),
            (1,6,7,2),
            (0,5,6,1)
        ]

        mesh_data = bpy.data.meshes.new("cube_mesh_data")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Black 8 Cylinder", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].width = 0.025
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        for e in me.edges:
           if e.use_edge_sharp:
               e.bevel_weight = 1
           else:
               pass
        return {"FINISHED"}


class TwoCylinder(Operator):
    bl_idname = "mesh.def_sixteen"
    bl_label = "Defined Cylinder Add"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    def execute(self, context):
        #bpy.ops.mesh.primitive_cylinder_add(vertices=16)
        verts = [
            (0,1,-1),
            (0.3827, 0.9239,-1),
            (0.7071, 0.7071,-1),
            (0.9239, 0.3827,-1),
            (1,0,-1),
            (0.9239, -0.3927, -1),
            (0.7071, -0.7071, -1),
            (0.3827, -0.9239, -1),
            (0,-1,-1),
            #separator
            (0, 1, 1),
            (0.3827, 0.9239, 1),
            (0.7071, 0.7071, 1),
            (0.9239, 0.3827, 1),
            (1, 0, 1),
            (0.9239, -0.3927, 1),
            (0.7071, -0.7071, 1),
            (0.3827, -0.9239, 1),
            (0,-1,1)
        ]

        edges = []

        faces = [
            (0,1,2,3,4,5,6,7,8),
            (17,16,15,14,13,12,11,10,9),
            (7,16,17,8),
            (6,15,16,7),
            (5,14,15,6),
            (4,13,14,5),
            (3,12,13,4),
            (2,11,12,3),
            (1,10,11,2),
            (0,9,10,1)
        ]

        mesh_data = bpy.data.meshes.new("cube_mesh_data")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Black 16 Cylinder", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].width = 0.025
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        return {"FINISHED"}


class ThreeCylinder(Operator):
    bl_idname = "mesh.def_thirty_two"
    bl_label = "Defined Cylinder Add"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    def execute(self, context):
        #bpy.ops.mesh.primitive_cylinder_add(vertices=32)
        verts = [
            (0, 1, -1),
            (0.195, 0.981, -1),
            (0.383, 0.924, -1),
            (0.5555, 0.8315, -1),
            (0.7071, 0.7071, -1),
            (0.8315, 0.5556, -1),
            (0.924, 0.383, -1),
            (0.981, 0.195, -1),
            (1, 0, -1),
            (0.9808, -0.1951, -1),
            (0.9239, -0.3827, -1),
            (0.8315, -0.5556, -1),
            (0.7071, -0.7071, -1),
            (0.5556, -0.8315, -1),
            (0.383, -0.924, -1),
            (0.195, -0.981, -1),
            (0, -1, -1),
            # Separator
            (0, -1, 1),
            (0.195, -0.981, 1),
            (0.383, -0.924, 1),
            (0.5555, -0.8315, 1),
            (0.7071, -0.7071, 1),
            (0.8315, -0.5556, 1),
            (0.924, -0.383, 1),
            (0.981, -0.195, 1),
            (1, 0, 1),
            (0.9808, 0.1951, 1),
            (0.9239, 0.3827, 1),
            (0.8315, 0.5556, 1),
            (0.7071, 0.7071, 1),
            (0.5556, 0.8315, 1),
            (0.383, 0.924, 1),
            (0.195, 0.981, 1),
            (0, 1, 1)
        ]

        edges = []

        faces = [
            (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33),
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16),
            (15, 18, 17, 16),
            (14, 19, 18, 15),
            (13, 20, 19, 14),
            (12, 21, 20, 13),
            (11, 22, 21, 12),
            (10, 23, 22, 11),
            (9, 24, 23, 10),
            (8, 25, 24, 9),
            (7, 26, 25, 8),
            (6, 27, 26, 7),
            (5, 28, 27, 6),
            (4, 29, 28, 5),
            (3, 30, 29, 4),
            (2, 31, 30, 3),
            (1, 32, 31, 2),
            (0, 33, 32, 1)
        ]

        mesh_data = bpy.data.meshes.new("cube_mesh_data")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Black 32 Cylinder", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select = True
        bpy.context.scene.objects.active = obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type="BEVEL")
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Bevel"].limit_method = "WEIGHT"
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].width = 0.025
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        return {"FINISHED"}


class OneSphere(Operator):
    bl_idname = "mesh.def_sphere_two"
    bl_label = "Defined Sphere Add"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "Black 2 Sphere"
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.subdivide(number_cuts=1, smoothness=1)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.9
        return {"FINISHED"}


class TwoSphere(Operator):
    bl_idname = "mesh.def_sphere_four"
    bl_label = "Defined Cylinder Add"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "Black 4 Sphere"
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.subdivide(number_cuts=3, smoothness=1)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        return {"FINISHED"}


class ThreeSphere(Operator):
    bl_idname = "mesh.def_sphere_eight"
    bl_label = "Defined Cylinder Add"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return True
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "Black 8 Sphere"
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.subdivide(number_cuts=7, smoothness=1)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.628319
        return {"FINISHED"}

# class AddTop(Operator):
#     """Inserts a top view background image into the scene with full opacity"""
#     bl_idname = "bg_image.top"
#     bl_label = "Top Image"
#
#     def execute(self, context):
#         bpy.context.space_data.show_background_images = True
#         return {"FINISHED"}
#
# class AddSide(Operator):
#     #"""Inserts a side view background image into the scene with full opacity"""
#     bl_idname = "bg_image.side"
#     bl_label = "Side Image"
#
#     def invoke(self, context, event):
#         # Open file browser
#         context.window_manager.fileselect_add(self)
#         return {'RUNNING_MODAL'}
#
#     def execute(self, context):
#         bpy.ops.mesh.primitive_cube_add()
#         #bpy.context.space_data.show_background_images = True
#         #bpy.ops.view3d.background_image_add()
#         #bpy.data.screens["Addon Scripting"].() = 'FRONT'
#         #bpy.ops.image.open()
#         return {"FINISHED"}
#
# class AddFront(Operator):
#     """Inserts a front view background image into the scene with full opacity"""
#     bl_idname = "bg_image.front"
#     bl_label = "Front Image"
#
#     def execute(self, context):
#         bpy.context.space_data.show_background_images = True
#         return {"FINISHED"}

class BooleanMode(Operator):
    bl_idname = "object.boolean_mode"
    bl_label = "Enter Boolean Mode"

    boolean_mode = True
    initial_name = ""
    duplicate_name = ""

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        self.__class__.boolean_mode = True
        self.__class__.initial_name = bpy.context.object.name
        bpy.ops.object.duplicate_move()
        self.__class__.duplicate_name = bpy.context.object.name
        if bpy.context.object.layers[0]:
            bpy.ops.object.move_to_layer(layers=(
                        False, True, False, False, False, False, False, False, False, False, False, False, False, False,
                        False, False, False, False, False, False))
        else:
           bpy.ops.object.move_to_layer(layers=(
                        True, False, False, False, False, False, False, False, False, False, False, False, False, False,
                        False,False, False, False, False, False))
        bpy.data.objects[self.__class__.initial_name].select = True
        bpy.context.scene.objects.active = bpy.data.objects[self.__class__.initial_name]
        bpy.data.objects[self.__class__.initial_name].modifiers.clear()
        return {"FINISHED"}


class ExitBooleanMode(Operator):
    bl_idname = "object.exit_boolean_mode"
    bl_label = "Exit Boolean Mode"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        mode = BooleanMode.boolean_mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            if current_mode == "OBJECT":
                if mode == True:
                    return True
                else:
                    return False
            else:
                return False

    def execute(self, context):
        # global duplicate_name
        # global initial_name
        # global boolean_mode
        ob = bpy.context.object
        me = ob.data
        me.use_customdata_edge_bevel = True
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        for e in me.edges:
            if e.use_edge_sharp:
                e.bevel_weight = 1
            else:
                pass
        bpy.data.objects[BooleanMode.duplicate_name].select = True
        bpy.context.scene.objects.active = bpy.data.objects[BooleanMode.duplicate_name]
        bpy.data.objects[BooleanMode.initial_name].select = True
        bpy.ops.object.make_links_data(type="MODIFIERS")
        bpy.data.objects[BooleanMode.initial_name].select = False
        bpy.data.objects.remove(bpy.context.scene.objects[BooleanMode.duplicate_name])
        bpy.data.objects[BooleanMode.initial_name].select = True
        bpy.context.scene.objects.active = bpy.data.objects[BooleanMode.initial_name]
        BooleanMode.boolean_mode = False
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 0.610865
        return {"FINISHED"}


class ApplyMods(Operator):
    bl_idname = "object.mod_apply"
    bl_label = "Apply Modifiers"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.convert(target="MESH")
        return {"FINISHED"}


class ApplyModsAll(Operator):
    bl_idname = "object.mod_apply_all"
    bl_label = "Apply Modifiers to All"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.select_all(action="DESELECT")
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                obj.select = True
        bpy.ops.object.convert(target="MESH")
        #scene = bpy.context.scene
        #scene.objects.active = bpy.data.objects["template"]
        #for obj in scene.objects:
        #    if obj.type == "MESH":
        #        obj.select = True
        #bpy.ops.object.convert(target="MESH")
        #mat = bpy.data.materials.get("Material")
        #for ob in bpy.data.objects:
            #ob.data.object.convert(target="MESH")
            #self.report({"INFO"}, ob.name)
            #mat = bpy.data.materials.new(name=ob.name + " test material")
            #ob.data.materials.append(mat)
            #ob.data.materials.append(mat)
            #ob.data.materials.material_slot_remove()
            #ob.data.materials.new(name=ob.name + " TestMat")
            #self.report({"INFO"}, "Removed material from " + ob.name)
        #Converts object to mesh which has a side effect of applying all modifiers
        #bpy.ops.material.new()
        #for ob in bpy.data.objects:
        #    bpy.ops.ob.convert(target="MESH")
        return {"FINISHED"}


class PackUnwrap(Operator):
    bl_idname = "object.pack_unwrap"
    bl_label = "Pack Unwrap"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.uv.pack_islands(margin=0.001)
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}


class SharpUnwrap(Operator):
    bl_idname = "object.sharp_unwrap"
    bl_label = "Sharp Unwrap"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.uv.pack_islands(margin=0.001)
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}


class CubeUnwrap(Operator):
    bl_idname = "object.cube_unwrap"
    bl_label = "Cube Unwrap"

    @classmethod
    def poll(cls, context):
        # Variable for storing current mode
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.select_all(action="TOGGLE")
        bpy.ops.uv.cube_project()
        bpy.ops.uv.pack_islands(margin=0.001)
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}


class CreateId(Operator):
    """Creates unique ID color on each discrete object in scene (which will bake in Susbtance Painter). Use BEFORE joining for texture sets"""
    bl_idname = "object.id_create"
    bl_label = "Create ID"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        def random_color(obj):
            import random
            r = random.random
            mesh = obj.data
            scn = bpy.context.scene
            scn.objects.active = obj
            obj.select = True
            if mesh.vertex_colors:
                vcol_layer = mesh.vertex_colors.active
            else:
                vcol_layer = mesh.vertex_colors.new()
            random_color = [r(), r(), r()]
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    vcol_layer.data[loop_index].color = random_color

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                random_color(obj)
        bpy.ops.paint.vertex_paint_toggle()
        return {"FINISHED"}


class CreateTexSet(Operator):
    bl_idname = "object.create_tex_set"
    bl_label = "Create Texture Set"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        for ob in bpy.context.selected_editable_objects:
            bpy.ops.object.convert(target="MESH")
            bpy.ops.object.join()
            mat = bpy.data.materials.new(name=ob.name + " Texture Set")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            for node in nodes:
                nodes.remove(node)
            group = nodes.new("ShaderNodeGroup")
            group.node_tree = bpy.data.node_groups["NodeGroup"]
            node_output = nodes.new(type="ShaderNodeOutputMaterial")
            node_output.location = 400, 0
            links = mat.node_tree.links
            link = links.new(group.outputs[0], node_output.inputs[0])
            ob.data.materials.append(mat)
        return {"FINISHED"}


class CreateMaterialSets(Operator):
    bl_idname = "scene.create_mat_sets"
    bl_label = "Create Material Sets"

    @classmethod
    def poll(cls, context):
        if bpy.context.object is None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        bpy.ops.object.select_all(action="SELECT")
        for ob in bpy.context.selected_editable_objects:
            mat = bpy.data.materials.new(name=ob.name + " Texture Set")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            for node in nodes:
                nodes.remove(node)
            group = nodes.new("ShaderNodeGroup")
            group.node_tree = bpy.data.node_groups["NodeGroup"]
            node_output = nodes.new(type="ShaderNodeOutputMaterial")
            node_output.location = 400,0
            links = mat.node_tree.links
            link = links.new(group.outputs[0], node_output.inputs[0])
            ob.data.materials.append(mat)
        bpy.ops.object.select_all(action="DESELECT")
        return {"FINISHED"}


class ClearMaterials(Operator):
    bl_idname = "scene.clear_mat_sets"
    bl_label = "Clear Material Sets"

    @classmethod
    def poll(cls, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"
    def execute(self, context):
        bpy.ops.object.select_all(action="SELECT")
        for ob in bpy.context.selected_editable_objects:
            ob.active_material_index = 0
            for i in range(len(ob.material_slots)):
                bpy.ops.object.material_slot_remove({"object": ob})
        bpy.ops.object.select_all(action="DESELECT")
        return {"FINISHED"}


class SubstanceExport(Operator):
    bl_idname = "scene.substance_export"
    bl_label = "Substance Export"

    @classmethod
    def poll(self, context):
        if bpy.context.object == None:
            return False
        else:
            current_mode = bpy.context.object.mode
            return current_mode == "OBJECT"

    def execute(self, context):
        if bpy.data.is_saved:
            i = 0
            bpy.ops.object.select_all(action="DESELECT")
            for ob in bpy.data.objects:
                if ob.type == "MESH":
                    if len(ob.data.uv_layers) == 0:
                        def warning(self, context):
                            self.layout.label("Object in scene missing UV!")
                        bpy.context.window_manager.popup_menu(warning, title="Error", icon='ERROR')
                        i = 1
                    elif len(ob.material_slots) == 0:
                        def warning(self, context):
                            self.layout.label("Missing texture set! (Object without material)")
                        bpy.context.window_manager.popup_menu(warning, title="Error", icon='ERROR')
                        i = 1
            if i == 0:
                bpy.ops.object.select_all(action="SELECT")
                filename = bpy.path.basename(bpy.context.blend_data.filepath)
                blendpath = bpy.path.abspath("//")
                filename = os.path.splitext(filename)[0]
                bpy.ops.export_scene.fbx(filepath=blendpath + filename + ".fbx", use_selection=True, axis_forward='-Z',
                                                  axis_up='Y')
                def warning(self, context):
                    self.layout.label("Scene Exported.")
                bpy.context.window_manager.popup_menu(warning, title="Info", icon='INFO')
            bpy.ops.object.select_all(action="DESELECT")
        else:
            def warning(self, context):
                 self.layout.label("Blend file is not saved!")
            bpy.context.window_manager.popup_menu(warning, title="Error", icon='ERROR')
        return {"FINISHED"}


addon_keymaps = []


def register():
    bpy.utils.register_module(__name__)

    kcfg = bpy.context.window_manager.keyconfigs.addon

    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.call_menu", "Q", "PRESS")
        kmi.properties.name = BlackOps.bl_idname
        addon_keymaps.append((km, kmi))

    # # Icons
    # from bpy.utils import previews
    # pcoll = previews.new()
    #
    # icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    # icons_dir_files = os.listdir(icons_dir)
    #
    # all_icon_files = [icon for icon in icons_dir_files if icon.endswith(".png")]
    # all_icon_names = [icon[0:-4] for icon in all_icon_files]
    # all_icon_files_and_names = zip(all_icon_names, all_icon_files)
    #
    # for icon_name, icon_file in all_icon_files_and_names:
    #     pcoll.load(icon_name, os.path.join(icons_dir, icon_file), 'IMAGE')
    #
    # preview_collections["main"] = pcoll

    #icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    #icons_dir_files = os.listdir(icons_dir)

    # all_icon_files = [icon for icon in icons_dir_files if icon.endswith(".png")]
    # all_icon_names = [icon[0:-4] for icon in all_icon_files]
    # all_icon_files_and_names = zip(all_icon_names, all_icon_files)
    #
    # for icon_name, icon_file in all_icon_files_and_names:
    #     pcoll.load(icon_name, os.path.join(icons_dir, icon_file), 'IMAGE')
    #bpy.utils.register_module(__name__)
    #preview_collections["main"] = pcoll
    #kcfg = bpy.context.window_manager.keyconfigs.addon
    #if kcfg:
        # km = kcfg.keymaps.new(name="3D View", space_type="VIEW_3D")
        #
        # kmi = km.keymap_items.new("wm.call_menu", "Q", "PRESS")
        # kmi.properties.name = BlackOps.bl_idname
        #
        # kmimi = km.keymap_items.new("view3d.black_modifier", "B", "PRESS", shift=True, ctrl=True, alt=True)
        # #kmimi.properties.name = BlackModifierMenu.bl_idname
        #
        # addon_keymaps.append((km, kmi))
        # addon_keymaps.append((km, kmimi))


def unregister():
    # for pcoll in preview_collections.values():
    #     bpy.utils.previews.remove(pcoll)
    # preview_collections.clear()
    bpy.utils.unregister_module(__name__)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
