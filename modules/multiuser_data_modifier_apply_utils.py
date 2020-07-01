import bpy
from bpy.props import *
from bpy.types import Operator

from .utils import get_ml_active_object


class OBJECT_OT_ml_modifier_apply_multi_user_data_dialog(Operator):
    bl_idname = "object.ml_modifier_apply_multi_user_data_dialog"
    bl_label = "Apply Modifier Dialog"
    bl_options = {'INTERNAL'}

    modifier: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    op_name: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=360)

    def draw(self, context):
        ml_active_ob = get_ml_active_object()

        layout = self.layout

        # Popups can't be closed manually, so just show a label after
        # the modifier has been applied.
        try:
            ml_active_ob.modifiers[self.modifier]
        except KeyError:
            layout.label(text="Done")
            return

        layout.label(text="Object's data is used by multiple objects. What would you like to do?")

        layout.separator()

        op = layout.operator(self.op_name, text="Apply To Active Object Only (Break Link)")
        op.modifier = self.modifier
        op.multi_user_data_apply_method = 'APPLY_TO_SINGLE'

        op = layout.operator(self.op_name, text="Apply To All Objects")
        op.modifier = self.modifier
        op.multi_user_data_apply_method = 'APPLY_TO_ALL'


class LinkedObjectDataChanger:

    """
    Helper class to be used when applying a modifier to one or all
    objects with multi-user data.
    
    Usage:
    
    Use make_active_instance_data_unique to create a copy of the 
    current data and to assing it to the active instance.

    Use assign_new_data_to_other_instances to assign the new data to the
    other instances.

    reassign_old_data_to_active_instance can be used to reassign the old
    data to the active instance and to delete the new data (used when
    a modifier can't be applied).
    """

    def __init__(self, object):
        self._object = object

    def get_correct_data_collection(self):
        if self._object.type == 'MESH':
            return bpy.data.meshes
        elif self._object.type in {'CURVE', 'SURFACE', 'FONT'}:
            return bpy.data.curves
        elif self._object.type == 'LATTICE':
            return bpy.data.lattices

    def make_active_instance_data_unique(self):
        new_data = self._object.data.copy()
        self._old_data_name = self._object.data.name
        self._new_data_name = new_data.name
        self._object.data = new_data

    def assign_new_data_to_other_instances(self):
        obs = bpy.data.objects
        obs_with_same_data = [ob for ob in obs if ob.data and ob.data.name == self._old_data_name]
        data_collection = self.get_correct_data_collection()

        for ob in obs_with_same_data:
            ob.data = data_collection[self._new_data_name]

        data_collection.remove(data_collection[self._old_data_name])

    def reassign_old_data_to_active_instance(self):
        data_collection = self.get_correct_data_collection()
        self._object.data = data_collection[self._old_data_name]

        data_collection.remove(data_collection[self._new_data_name])
