import subprocess
from pathlib import Path
from importlib.util import find_spec


def ensure_pytest():
    if find_spec("pytest"):
        return True

    import sys
    from pathlib import Path

    import bpy

    print("Modifier List: installing Pytest...")

    py_exec = str(Path(sys.exec_prefix, "bin", "python.exe"))
    target_dir = str(Path(bpy.utils.script_path_user(), "modules"))

    subprocess.run([py_exec, "-m", "pip", "install", "--target=" + target_dir, "pytest"])

    if find_spec("pytest"):
        print("Modifier List: succesfully installed Pytest")
        return True
    else:
        print("Modifier List: Failed to install Pytest")
        return False


def main():
    if not ensure_pytest():
        print("Modifier List: Couldn't run tests, Pytest not installed")
        return

    import pytest
    pytest.main([str(Path(__file__).resolve().parents[0])])


if __name__ == "__main__":
    main()
