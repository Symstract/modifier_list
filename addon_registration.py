"""Utility module for registering classes and properties"""

import importlib
import inspect
import os


imported_modules = []
sorted_classes = []


# Finding and importing modules
# ======================================================================

def _find_modules(root_dir):
    """Finds all modules in a given directory and returns them in a set.

    Form of returned modules is 'relative.path.module'.

    Directories that have "__" in their name are ignored.
    """
    current_directory = os.path.dirname(__file__)
    root_directory = os.path.join(current_directory, root_dir)

    if not os.path.exists(root_directory):
        raise FileNotFoundError("root_dir doesn't exist")

    modules = set()

    for root, dirs, files in os.walk(root_directory):
        dirs[:] = [d for d in dirs if "__" not in d]

        relative_root = os.path.relpath(root, current_directory)

        for f in files:
            if f.endswith(".py") and "__" not in f:
                joined = os.path.join(relative_root, f[:-3])
                modules.add(joined.replace(os.path.sep, "."))

    return modules


first_call = True

def _import_modules(modules):
    """Imports or reloads given modules and returns them in a list.

    Modules must include relative path.
    """

    # Tried importing with absolute path but for some reason it didn't
    # work. Anyway, using relative path works...

    global first_call

    imported_modules = []
    for mod in modules:
        if first_call:
            module = importlib.import_module("." + mod, package=__package__)
        else:
            module = importlib.import_module("." + mod, package=__package__)
            # Clear everything else than builtins to get rid of
            # renamed and removed stuff
            module_dict = dict(module.__dict__)
            for i in module_dict:
                if "__" not in i:
                    module.__dict__.pop(i)

            module = importlib.reload(module)

        imported_modules.append(module)

    first_call = False

    return imported_modules


def _store_modules_globally(modules):
    """Puts given modules into a global 'imported_modules' list"""
    global imported_modules

    imported_modules.clear()

    imported_modules = modules


# Finding and sorting classes
# ======================================================================

def _find_bl_classes(modules):
    """Finds all add-on classes from given modules and returns them in
    a list.

    Modules must include a relative path.
    """
    from bpy.types import bpy_struct

    bl_classes = []

    cur_dir_path = os.path.dirname(__file__)
    cur_dir_basename = os.path.basename(cur_dir_path)

    for mod in modules:
        full_module_path = mod.__file__
        module_path_from_cur_dir = full_module_path.replace(cur_dir_path, cur_dir_basename)
        formatted_module_path = module_path_from_cur_dir.replace(os.path.sep, ".")[:-3]

        classmembers = [m[1] for m in inspect.getmembers(mod, inspect.isclass)
                        if m[1].__module__ == formatted_module_path]
        bpy_subclasses = [cm for cm in classmembers if issubclass(cm, bpy_struct)]
        bl_classes.extend(bpy_subclasses)

    return bl_classes


def _sort_classes_topologically(classes):
    """Sorts classes based on their hierarchy."""
    # TODO: Handle circular dependencies
    unsorted_classes = classes[:]
    sorted_classes_from_bottom = []

    while unsorted_classes:
        for cls in unsorted_classes:
            if not [c for c in cls.__subclasses__() if c in unsorted_classes]:
                sorted_classes_from_bottom.append(cls)
                unsorted_classes.remove(cls)

    sorted_classes = list(reversed(sorted_classes_from_bottom))
    return sorted_classes


def _sort_panel_classes(classes, panel_order):
    """Sorts panel classes.

    Args:
        classes: an iteratable of classes
        panel_order: an iteratable of panel class names

    Returns:
        sorted_classes: a list of sorted classes

    Panel classes in classes (if there are any) are sorted according to
    panel_order and put at the end of sorted_classes. This is needed
    because the order of panels in Blender's UI is defined by the order
    they are registered.
    """
    all_classes = classes[:]
    panel_classes = []

    for panel in all_classes:
        if panel.__name__ in panel_order:
            panel_classes.append(panel)
            all_classes.remove(panel)

    for panel in panel_order:
        for cls in panel_classes:
            if cls.__name__ == panel:
                all_classes.append(cls)

    sorted_classes = all_classes
    return sorted_classes


def _store_classes_globally(modules):
    global sorted_classes

    sorted_classes.clear()

    sorted_classes = modules


# Registering classes
# ======================================================================

def _register_classes(classes, addon_name_for_counter=None):
    """Register all add-on classes that inherit from bpy_struct from all
    modules."""

    from bpy.utils import register_class

    class_count = 0
    for cls in classes:
        register_class(cls)
        class_count += 1
    if addon_name_for_counter:
        print(f"{addon_name_for_counter}: Registered {str(class_count)} classes")


def _unregister_classes(classes, addon_name_for_counter=None):
    """Unregister all add-on classes."""

    from bpy.utils import unregister_class

    class_count = 0
    for cls in classes:
        unregister_class(cls)
        class_count += 1
    if addon_name_for_counter:
        print(f"{addon_name_for_counter}: Unregistered {str(class_count)} classes")


# Public functions
# ======================================================================

def register_bl_classes(root_dir, panel_order=None, addon_name_for_counter=None):
    """Register all add-on classes that inherit from bpy_struct from all
    modules.

    Args:
        root_dir: root directory to search in
        panel_order: an iteratable of panel class names
        addon_name_for_counter: specify this if you want to print out
            the number of registered classes

    Modules and packages that have "__" in their name are ignored.

    If you have panel classes, panel_order is needed because the order
    of panels in Blender's UI is defined by the order they are
    registered.
    """
    modules = _find_modules(root_dir)
    modules = _import_modules(modules)
    _store_modules_globally(modules)

    classes = _find_bl_classes(modules)
    classes = _sort_classes_topologically(classes)
    if panel_order:
        classes = _sort_panel_classes(classes, panel_order)
    _store_classes_globally(classes)

    _register_classes(classes, addon_name_for_counter)


def unregister_bl_classes(addon_name_for_counter=None):
    """Unregister all add-on classes.

    Args:
        addon_name_for_counter: specify this if you want to print out
        the number of unregistered classes
    """
    _unregister_classes(reversed(sorted_classes), addon_name_for_counter)


# Calling (un)register

def call_register(root_dir):
    """Call register from all add-on modules"""
    for mod in imported_modules:
        if hasattr(mod, "register"):
            mod.register()


def call_unregister(root_dir):
    """Call unregister from all add-on modules"""
    for mod in imported_modules:
        if hasattr(mod, "unregister"):
            mod.unregister()




