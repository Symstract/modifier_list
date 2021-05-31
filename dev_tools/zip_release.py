import argparse
import shutil
from pathlib import Path


ADDON_DIR_NAME = "modifier_list"
ITEMS_TO_INCLUDE = (
    "icons",
    "modules",
    "__init__.py",
    "addon_registration.py",
    "LICENSE"
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("version", help="version number to append to the name of the .zip")
    return parser.parse_args()


def main():
    root = Path(__file__).resolve().parents[2]
    all_releases_dir = root / f"{ADDON_DIR_NAME}_RELEASES"
    all_releases_dir.mkdir(exist_ok=True)

    addon_version = parse_args().version
    zip_name = f"{ADDON_DIR_NAME}_{addon_version}"

    if (all_releases_dir / f"{zip_name}.zip").exists():
        raise FileExistsError(".zip with the given version already exists")

    release_dir = all_releases_dir / ADDON_DIR_NAME

    if release_dir.exists():
        shutil.rmtree(release_dir)

    release_dir.mkdir()

    for item in ITEMS_TO_INCLUDE:
        source = root / ADDON_DIR_NAME / item
        dest = release_dir / item
        if source.is_dir():
            shutil.copytree(source, dest)
        else:
            shutil.copy(source, dest)

    shutil.make_archive(all_releases_dir / zip_name, "zip", release_dir)

    print(f"{zip_name}.zip succesfully created")

    shutil.rmtree(release_dir)


if __name__ == "__main__":
    main()
