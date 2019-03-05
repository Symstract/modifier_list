import importlib
import inspect
import os


def _get_bl_modules(root_dir, dirs_ignore=None):
    current_directory = os.path.dirname(__file__)
    root_directory = os.path.join(current_directory, root_dir)
    if not os.path.exists(root_directory):
        raise FileNotFoundError("root_dir doesn't exist")

    addon_module_names = set()

    for root, dirs, files in os.walk(root_directory):
        if dirs_ignore:
            dirs[:] = [d for d in dirs if d not in dirs_ignore]
        rel_root = os.path.relpath(root, current_directory)
        for f in files:
            if f.endswith(".py") and "__" not in f:
                joined = os.path.join(rel_root, f[:-3])
                addon_module_names.add(joined.replace("\\", "."))

    # print("FOUND MODULES:")
    # print(addon_module_names)

    return addon_module_names


first_call = True

addon_classes = []

def _get_bl_classes(root_dir, dirs_ignore=None):
    global first_call

    global addon_classes

    from bpy.types import bpy_struct

    addon_classes = []
    for mod in _get_bl_modules(root_dir, dirs_ignore):
        if first_call:
            module = importlib.import_module("." + mod, package=__package__)
        else:
            module = importlib.import_module("." + mod, package=__package__)
            module = importlib.reload(module)
        module_path = os.path.basename(os.path.dirname(__file__)) + "." + mod
        classmembers = [m[1] for m in inspect.getmembers(module, inspect.isclass)
                        if m[1].__module__ == module_path]
        bpy_subclasses = [cm for cm in classmembers if issubclass(cm, bpy_struct)]
        addon_classes.extend(bpy_subclasses)

    first_call = False

    # print("ADDON CLASSES:")
    # for cls in addon_classes:
    #     print(cls)
    #     print(cls.__bases__)
    #     print(cls.__subclasses__())
    #     print(cls.__module__)
    #     print("")


def register_bl_classes(root_dir, dirs_ignore=None, addon_name=None):
    """Register all add-on classes that inherit from bpy_struct from all
    modules.

    root_dir: root directory to search in
    dirs_ignore: an iteratable of directories to be ignored from search
    unregister: unregister classes
    addon_name: specify this if you want to print out the number of registered classes

    Modules that have "__" in their name are ignored.
    """
    _get_bl_classes(root_dir, dirs_ignore)
    from bpy.utils import register_class
    class_count = 0
    for cls in addon_classes:
        register_class(cls)
        class_count += 1
    if addon_name:
        print(f"Registered {str(class_count)} classes for {addon_name}")


def unregister_bl_classes(addon_name=None):
    """Unregister all add-on classes.

    addon_name: specify this if you want to print out the number of unregistered classes
    """
    from bpy.utils import unregister_class
    class_count = 0
    for cls in addon_classes[::-1]:
        unregister_class(cls)
        class_count += 1
    if addon_name:
        print(f"Unregistered {str(class_count)} classes for {addon_name}")



