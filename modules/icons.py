import os

from bpy.utils import previews


preview_collections = {}

pcoll = previews.new()

icons_dir = os.path.join(os.path.dirname(__file__), os.path.pardir, "icons")
icons_dir_files = os.listdir(icons_dir)

all_icon_files = [icon for icon in icons_dir_files if icon.endswith(".png")]
all_icon_names = [icon[0:-4] for icon in all_icon_files]
all_icon_files_and_names = zip(all_icon_names, all_icon_files)

for icon_name, icon_file in all_icon_files_and_names:
    pcoll.load(icon_name, os.path.join(icons_dir, icon_file), 'IMAGE')

preview_collections["main"] = pcoll


def unregister():
    for pcoll in preview_collections.values():
        previews.remove(pcoll)
    preview_collections.clear()
