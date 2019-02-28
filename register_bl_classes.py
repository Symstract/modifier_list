import importlib
import inspect
import os


def _get_bl_modules(root_dir, dirs_ignore):
    current_directory = os.path.dirname(__file__)
    root_directory = os.path.join(current_directory, root_dir)
    if not os.path.exists(root_directory):
        raise FileNotFoundError("root_dir doesn't exist")

    bl_modules = set()

    for root, dirs, files in os.walk(root_directory):
        if dirs_ignore:
            dirs[:] = [d for d in dirs if d not in dirs_ignore]
        rel_root = os.path.relpath(root, current_directory)
        for f in files:
            if f.endswith(".py") and "__" not in f:
                joined = os.path.join(rel_root, f[:-3])
                bl_modules.add(joined.replace("\\", "."))

    return bl_modules


first_call = True # support reloading

def register_bl_classes(root_dir, dirs_ignore=None, unregister=False):
    """Import all add-on modules and register all classes from them
    that inherit from bpy.types.

    root_dir: root directory to search in
    dirs_ignore: an iteratable of directories to be ignored from search

    Modules that have "__" in their name are ignored.
    """
    from bpy import types

    bl_classes = []

    global first_call
    for mod in _get_bl_modules(root_dir, dirs_ignore):
        if first_call:
            module = importlib.import_module(mod)
        else:
            module = importlib.reload(mod)
        classmembers = [m[1] for m in inspect.getmembers(module, inspect.isclass) if m[1].__module__ == mod]
        bpy_subclasses = [i for i in classmembers if issubclass(i, types)]
        bl_classes.extend(bpy_subclasses)

    print(bl_classes)


    # if not unregister:
    #     from bpy.utils import register_class
    #     for cls in bl_classes:
    #         register_class(cls)
    # else:
    #     from bpy.utils import unregister_class
    #     for cls in bl_classes:
    #         unregister_class(cls)

    first_call = False


dirs_ignore = ("ignore_this")

register_bl_classes("modules", dirs_ignore)

