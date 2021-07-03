import argparse
from pathlib import Path
import subprocess


ADDON_MODULE_NAME = "modifier_list"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("blender_path", help="Path to a Blender executable.")
    return parser.parse_args()


def run_tests_in_blender():
    blender_path = parse_args().blender_path

    if not blender_path.endswith("blender.exe"):
        raise ValueError("blender_path doesn't end with 'blender.exe'")

    test_dir = Path(__file__).resolve().parents[1] / "source" / "tests"
    empty_scene_blend = test_dir / "blend_files" / "empty_scene.blend"
    test_script = test_dir / "main.py"

    subprocess.run([blender_path, empty_scene_blend, "--background", "--python", test_script])


if __name__ == "__main__":
    run_tests_in_blender()
