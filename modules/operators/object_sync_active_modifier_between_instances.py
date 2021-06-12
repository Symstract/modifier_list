import bpy
from bpy.types import Operator

from ..utils import get_editable_bpy_object_props, get_ml_active_object, sync_bpy_object_props


class OBJECT_OT_ml_sync_active_modifier_between_instances(Operator):
    bl_idname = "object.ml_sync_active_modifier_between_instances"
    bl_label = "Synchronize Active Modifier Between Instances"
    bl_description = ("Synchronize the active modifier between instances based on the active "
                      "object and the modifier name and type")
    bl_options = {'INTERNAL'}

    def __init__(self):
        self.obs_already_in_sync_count = 0
        self.obs_synced_count = 0
        self.obs_without_syncable_modifier_count = 0

    @classmethod
    def poll(cls, context):
        ob = get_ml_active_object()
        return ob.data.users > 1 and ob.modifiers

    def execute(self, context):
        source_ob = get_ml_active_object()
        source_mod = source_ob.modifiers[source_ob.ml_modifier_active_index]

        dest_obs = list(bpy.data.user_map(subset=[source_ob.data]).values()).pop()
        dest_obs.remove(source_ob)

        self.sync_modifiers(source_mod, dest_obs)

        synced_some_modifiers = self.check_if_modifiers_were_synced_and_report(dest_obs)

        if not synced_some_modifiers:
            return {'CANCELLED'}

        return {'FINISHED'}

    def sync_modifiers(self, source_modifier, dest_objects):
        props_to_sync_separately = {"show_render"}
        source_mod_geom_updating_props = get_editable_bpy_object_props(source_modifier,
                                                                       props_to_sync_separately)

        for dest_ob in dest_objects:
            dest_ob_mod_names = [mod.name for mod in dest_ob.modifiers]

            if source_modifier.name not in dest_ob_mod_names:
                self.obs_without_syncable_modifier_count += 1
                continue

            dest_mod = dest_ob.modifiers[source_modifier.name]

            if source_modifier.type != dest_mod.type:
                self.obs_without_syncable_modifier_count += 1
                continue

            dest_mod_geom_updating_props = get_editable_bpy_object_props(
                dest_mod, props_to_sync_separately)

            synced = False

            # Check name and show_render and other properties
            # separately to avoid updating geometry unnecessarily.
            if source_mod_geom_updating_props != dest_mod_geom_updating_props:
                sync_bpy_object_props(source_modifier, dest_mod)
                synced = True
            if dest_mod.show_render is not source_modifier.show_render:
                dest_mod.show_render = source_modifier.show_render
                synced = True

            if synced:
                self.obs_synced_count += 1
            else:
                self.obs_already_in_sync_count += 1

    def check_if_modifiers_were_synced_and_report(self, dest_objects):
        # No modifier synced
        if self.obs_already_in_sync_count == len(dest_objects):
            self.report({'INFO'}, "Modifer already in sync on all instances")
            return False
        elif self.obs_without_syncable_modifier_count == len(dest_objects):
            self.report({'ERROR'}, "No instance has a synchronizable modifier")
            return False
        elif self.obs_without_syncable_modifier_count and self.obs_already_in_sync_count:
            self.report({'INFO'},
                        "Modifer already in sync on all instances that have a synchronizable one")
            return False

        # Modifier synced
        if self.obs_synced_count == len(dest_objects):
            self.report({'INFO'}, "Synchronized a modifier on all instances")
        else:
            self.report({'INFO'}, "Synchronized a modifier on some instances")

        return True
