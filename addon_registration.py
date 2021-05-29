"""Utility module for registering classes and properties"""

import importlib
import inspect
import os
import sys

from bpy.types import bpy_struct, WorkSpaceTool
from bpy.utils import register_class, unregister_class


imported_modules = []
sorted_classes = []


# Finding and importing modules
# ======================================================================

def _find_modules(root_dir):
    """Finds all modules in the given directory and returns them in a
    set.

    The form of the returned modules is 'relative.path.module'.

    Directories whose name contains "__" are ignored.
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


def _import_modules(modules):
    """Imports or reloads the given modules and returns them in a list.

    Modules must contain their relative paths.
    """
    if imported_modules:
        for mod in imported_modules:
            try:
                sys.modules.pop(mod.__name__)
            except KeyError:
                pass

    return [importlib.import_module("." + mod, package=__package__) for mod in modules]


def _store_modules(modules):
    """Puts the given modules into a global 'imported_modules' list"""
    global imported_modules
    imported_modules.clear()
    imported_modules = modules


# Finding and sorting classes
# ======================================================================

def _find_bl_classes(modules):
    """Finds all add-on classes (excluding subclasses of WorkSpaceTool)
    in the given modules and returns them in a list.

    Modules must contain their relative paths.
    """
    bl_classes = []

    cur_dir_path = os.path.dirname(__file__)
    cur_dir_basename = os.path.basename(cur_dir_path)

    for mod in modules:
        full_module_path = mod.__file__
        module_path_from_cur_dir = full_module_path.replace(cur_dir_path, cur_dir_basename)
        formatted_module_path = module_path_from_cur_dir.replace(os.path.sep, ".")[:-3]
        class_members = [m[1] for m in inspect.getmembers(mod, inspect.isclass)
                        if m[1].__module__ == formatted_module_path]
        bpy_subclasses = [cm for cm in class_members if issubclass(cm, bpy_struct) and
                          not issubclass(cm, WorkSpaceTool)]
        bl_classes.extend(bpy_subclasses)

    return bl_classes


def _sort_classes_topologically(classes):
    """Sorts classes based on their hierarchy."""
    unsorted_classes = classes[:]
    sorted_classes_from_bottom = []

    safety_counter = 0

    while unsorted_classes:
        for cls in unsorted_classes:
            if not [c for c in cls.__subclasses__() if c in unsorted_classes]:
                sorted_classes_from_bottom.append(cls)
                unsorted_classes.remove(cls)

        safety_counter += 1
        assert safety_counter < 10000, "Infinite loop in_sort_classes_topologically"

    return list(reversed(sorted_classes_from_bottom))


def _sort_panel_classes(classes, panel_order):
    """Sorts the panel classes in the given classes iteratable and
    returns a new list in which they are at the end.

    classes: an iteratable of classes
    panel_order: an iteratable of panel class names
    """
    other_classes = [cls for cls in classes if cls.__name__ not in panel_order]
    panel_classes = [cls for panel in panel_order for cls in classes if cls.__name__ == panel]
    return other_classes + panel_classes


def _store_classes(modules):
    global sorted_classes
    sorted_classes.clear()
    sorted_classes = modules


# Registering classes
# ======================================================================

def _register_classes(classes, addon_name_for_counter=None):
    """Registers all add-on classes that inherit from bpy_struct from
    all modules."""
    for cls in classes:
        register_class(cls)

    if addon_name_for_counter:
        print(f"{addon_name_for_counter}: Registered {str(len(classes))} classes")


# Public functions
# ======================================================================

def import_modules(root_dir):
    """Imports all modules in the given directory in order to make them
    available for other functions in addon_registration.
    """
    modules = _find_modules(root_dir)
    modules = _import_modules(modules)
    _store_modules(modules)


def register_bl_classes(modules_to_ignore=None, classes_to_ignore=None, panel_order=None,
                        addon_name_for_counter=None):
    """Registers all add-on classes that inherit from bpy_struct from
    all modules.

    import_modules needs to be called before this.

    Args:
        modules_to_ignore: an iteratable of the names of the
            moduless that should be ignored
        classes_to_ignore: an iteratable of the names of the
            classes that should be ignored
        panel_order: an iteratable of panel class names
        addon_name_for_counter: The name of the addon. If given, the
            number of the registered classes is printed out.

    Modules and packages that have "__" in their name are ignored.

    If you have panel classes, panel_order is needed because the order
    of panels in Blender's UI is defined by the order they are
    registered in.
    """
    if modules_to_ignore:
        modules = [m for m in imported_modules
                   if m.__name__.split(".")[-1] not in modules_to_ignore]
    else:
        modules = imported_modules

    classes = _find_bl_classes(modules)
    classes = _sort_classes_topologically(classes)

    if classes_to_ignore:
        classes = [cls for cls in classes if cls.__name__.split(".")[-1] not in classes_to_ignore]

    if panel_order:
        classes = _sort_panel_classes(classes, panel_order)

    _store_classes(classes)
    _register_classes(classes, addon_name_for_counter)


def unregister_bl_classes(addon_name_for_counter=None):
    """Unregisters all add-on classes.

    Args:
        addon_name_for_counter: The name of the addon. If given, the
            number of the unregistered classes is printed out.
    """
    classes = list(reversed(sorted_classes))

    for cls in classes:
        unregister_class(cls)

    if addon_name_for_counter:
        print(f"{addon_name_for_counter}: Unregistered {str(len(classes))} classes")


# Calling (un)register

def call_register():
    """Calls register of all add-on modules.

    import_modules must have been called before this.
    """
    for mod in imported_modules:
        if hasattr(mod, "register"):
            mod.register()


def call_unregister():
    """Calls unregister of all add-on modules."""
    for mod in imported_modules:
        if hasattr(mod, "unregister"):
            mod.unregister()
