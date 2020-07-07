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

    if first_call:
        for mod in modules:
            module = importlib.import_module("." + mod, package=__package__)
            imported_modules.append(module)
    else:
        # Reload modules twice so modules that import from other modules
        # always get stuff that's up to date.
        for _ in range(2):
            imported_modules.clear()

            for mod in modules:
                module = importlib.import_module("." + mod, package=__package__)

                # Clear everything else than builtins to get rid of
                # renamed and removed stuff.
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
    """Finds all add-on classes (excluding subclasses of WorkSpaceTool)
    from given modules and returns them in a list.

    Modules must include a relative path.
    """
    from bpy.types import bpy_struct, WorkSpaceTool

    bl_classes = []

    cur_dir_path = os.path.dirname(__file__)
    cur_dir_basename = os.path.basename(cur_dir_path)

    for mod in modules:
        full_module_path = mod.__file__
        module_path_from_cur_dir = full_module_path.replace(cur_dir_path, cur_dir_basename)
        formatted_module_path = module_path_from_cur_dir.replace(os.path.sep, ".")[:-3]

        classmembers = [m[1] for m in inspect.getmembers(mod, inspect.isclass)
                        if m[1].__module__ == formatted_module_path]
        bpy_subclasses = [cm for cm in classmembers if issubclass(cm, bpy_struct) and
                          not issubclass(cm, WorkSpaceTool)]
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

    return list(reversed(sorted_classes_from_bottom))


def _sort_panel_classes(classes, panel_order):
    """Sorts panel classes and returns a list in which they are at the end.

    classes: an iteratable of classes
    panel_order: an iteratable of panel class names
    """
    other_classes = [cls for cls in classes if cls.__name__ not in panel_order]
    panel_classes = [cls for panel in panel_order for cls in classes if cls.__name__ == panel]

    return other_classes + panel_classes


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

    for cls in classes:
        register_class(cls)

    if addon_name_for_counter:
        print(f"{addon_name_for_counter}: Registered {str(len(classes))} classes")


# Public functions
# ======================================================================

def register_bl_classes(root_dir, classes_to_ignore=None, panel_order=None,
                        addon_name_for_counter=None):
    """Register all add-on classes that inherit from bpy_struct from all
    modules.

    Args:
        root_dir: root directory to search in
        classes_to_ignore: an iteratable of the names of the
            classes that should be ignored
        panel_order: an iteratable of panel class names
        addon_name_for_counter: specify this if you want to print out
            the number of registered classes

    Modules and packages that have "__" in their name are ignored.

    If you have panel classes, panel_order is needed because the order
    of panels in Blender's UI is defined by the order they are
    registered in.
    """
    modules = _find_modules(root_dir)
    modules = _import_modules(modules)
    _store_modules_globally(modules)

    classes = _find_bl_classes(modules)
    classes = _sort_classes_topologically(classes)

    if classes_to_ignore:
        classes = [cls for cls in classes if cls.__name__ not in classes_to_ignore]

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
    from bpy.utils import unregister_class

    classes = list(reversed(sorted_classes))

    for cls in classes:
        unregister_class(cls)

    if addon_name_for_counter:
        print(f"{addon_name_for_counter}: Unregistered {str(len(classes))} classes")


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
