import bpy
from bpy.types import Operator

from ..utils import get_editable_bpy_object_props, get_ml_active_object, sync_bpy_object_props


class OBJECT_OT_ml_sync_all_modifiers_between_instances(Operator):
    bl_idname = "object.ml_sync_all_modifiers_between_instances"
    bl_label = "Synchronize All Modifiers Between Instances"
    bl_description = ("Synchronize all modifiers between instances "
                      "based on the active object")
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return get_ml_active_object().data.users > 1

    def execute(self, context):
        props_to_sync_separately = {"name", "show_render"}
        source_ob = get_ml_active_object()
        source_mods = source_ob.modifiers
        source_mod_names_types = [mod.type for mod in source_mods]
        source_geom_updating_props_per_mod = [
            get_editable_bpy_object_props(mod, props_to_sync_separately) for mod in source_mods]

        dest_obs = list(bpy.data.user_map(subset=[source_ob.data]).values()).pop()
        dest_obs.remove(source_ob)
        
        needed_syncing = False

        for ob in dest_obs:
            dest_mod_names_types = [mod.type for mod in ob.modifiers]
           
            if source_mod_names_types == dest_mod_names_types:
                for i, source_mod in enumerate(source_mods):
                    dest_mod = ob.modifiers[i]
                    dest_mod_geom_updating_props = get_editable_bpy_object_props(
                        dest_mod, props_to_sync_separately)
                    # Check name and show_render and other properties
                    # separately to avoid updating geometry
                    # unnecessarily.
                    if source_geom_updating_props_per_mod[i] != dest_mod_geom_updating_props:
                        sync_bpy_object_props(source_mod, dest_mod)
                        needed_syncing = True
                    for p in props_to_sync_separately:
                        if getattr(dest_mod, p) != getattr(source_mod, p):
                            setattr(dest_mod, p, getattr(source_mod, p))
                            needed_syncing = True
            else:
                ob.modifiers.clear()
                for source_mod in source_mods:
                    new_mod = ob.modifiers.new(source_mod.name, source_mod.type)
                    sync_bpy_object_props(source_mod, new_mod)
                needed_syncing = True

        if not needed_syncing:
            self.report({'INFO'}, "Already in sync")
            return {'CANCELLED'}

        return {'FINISHED'}
