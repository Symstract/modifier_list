import importlib
import inspect
import os


addon_modules = []
addon_classes = []


# Finding and importing modules and finding classes
# ======================================================================

def _find_addon_modules(root_dir, dirs_ignore=None):
    """Finds all modules in a given directory and returns a set of them"""
    current_directory = os.path.dirname(__file__)
    root_directory = os.path.join(current_directory, root_dir)
    if not os.path.exists(root_directory):
        raise FileNotFoundError("root_dir doesn't exist")

    addon_module_names = set()

    for root, dirs, files in os.walk(root_directory):
        if dirs_ignore:
            dirs[:] = [d for d in dirs if d not in dirs_ignore]

        relative_root = os.path.relpath(root, current_directory)

        for f in files:
            if f.endswith(".py") and "__" not in f:
                joined = os.path.join(relative_root, f[:-3])
                addon_module_names.add(joined.replace("\\", "."))

    # print("FOUND MODULES:")
    # print(addon_module_names)

    return addon_module_names


first_call = True

def _import_addon_modules(root_dir, dirs_ignore=None):
    """Imports or reloads all add-on modules and stores them in a global
    list.
    """
    global first_call
    global addon_modules

    addon_modules = []

    for mod in _find_addon_modules(root_dir, dirs_ignore):
        if first_call:
            module = importlib.import_module("." + mod, package=__package__)
        else:
            module = importlib.import_module("." + mod, package=__package__)
            module = importlib.reload(module)
        addon_modules.append(module)

    first_call = False


def _find_bl_classes(root_dir, dirs_ignore=None):
    """Finds all add-on classes from modules in the global
    addon module list and stores them in a global list.
    """
    from bpy.types import bpy_struct

    global addon_classes

    addon_classes = []

    _import_addon_modules(root_dir, dirs_ignore)

    for mod, modname in zip(addon_modules, _find_addon_modules(root_dir, dirs_ignore)): # Confusing!!!
        module_path = os.path.basename(os.path.dirname(__file__)) + "." + modname
        classmembers = [m[1] for m in inspect.getmembers(mod, inspect.isclass)
                        if m[1].__module__ == module_path]
        bpy_subclasses = [cm for cm in classmembers if issubclass(cm, bpy_struct)]
        addon_classes.extend(bpy_subclasses)

    # print("ADDON CLASSES:")
    # for cls in addon_classes:
    #     print(cls)
    #     print(cls.__bases__)
    #     print(cls.__subclasses__())
    #     print(cls.__module__)
    #     print("")


def _sort_classes_topologically(classes):
    """Sorts classes based on their hierarchy"""
    # TODO: Handle circular dependencies
    unsorted_classes = classes[:]
    sorted_classes = []

    while unsorted_classes:
        for cls in unsorted_classes:
            if not [c for c in cls.__subclasses__() if c in unsorted_classes]:
                sorted_classes.append(cls)
                unsorted_classes.remove(cls)

    reversed_classes = list(reversed(sorted_classes))
    return reversed_classes


# Registering classes
# ======================================================================

def register_bl_classes(root_dir, dirs_ignore=None, addon_name_for_counter=None):
    """Register all add-on classes that inherit from bpy_struct from all
    modules.

    root_dir: root directory to search in
    dirs_ignore: an iteratable of directories to be ignored from search
    unregister: unregister classes
    addon_name_for_counter: specify this if you want to print out the
                            number of registered classes

    Modules that have "__" in their name are ignored.
    """
    _find_bl_classes(root_dir, dirs_ignore)

    from bpy.utils import register_class

    class_count = 0
    for cls in _sort_classes_topologically(addon_classes):
        register_class(cls)
        class_count += 1
    if addon_name_for_counter:
        print(f"Registered {str(class_count)} classes for {addon_name_for_counter}")


def unregister_bl_classes(addon_name_for_counter=None):
    """Unregister all add-on classes.

    addon_name_for_counter: specify this if you want to print out the
                            number of unregistered classes
    """
    from bpy.utils import unregister_class

    class_count = 0
    for cls in _sort_classes_topologically(addon_classes):
        unregister_class(cls)
        class_count += 1
    if addon_name_for_counter:
        print(f"Unregistered {str(class_count)} classes for {addon_name_for_counter}")


# Calling register
# ======================================================================

def call_register(root_dir, dirs_ignore=None):
    """Call register from all add-on modules"""
    for mod in addon_modules:
        if hasattr(mod, "register"):
            mod.register()


def call_unregister(root_dir, dirs_ignore=None):
    """Call unregister from all add-on modules"""
    for mod in addon_modules:
        if hasattr(mod, "unregister"):
            mod.unregister()




