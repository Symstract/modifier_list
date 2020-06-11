from pathlib import Path

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import *
from bpy.types import Operator

from ..preferences import read_prefs


class WM_OT_ml_preferences_import(Operator, ImportHelper):
    bl_idname = "wm.ml_preferences_import"
    bl_label = "Import Preferences"
    bl_description = "Import Modifier List preferences from another Blender version"
    bl_options = {'INTERNAL'}

    filename_ext = ".json"

    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        read_prefs(self.filepath)

        return {'FINISHED'}
