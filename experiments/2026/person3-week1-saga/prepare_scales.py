"""Run pinned SAGA's scale extraction for every COLMAP view."""

import argparse
import runpy
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--saga", required=True, type=Path)
    parser.add_argument("--scene", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    options = parser.parse_args()
    saga = options.saga.resolve()
    sys.path.insert(0, str(saga))
    from scene import Scene

    original = Scene.getTrainCameras

    def all_cameras(scene, scale=1.0):
        return original(scene, scale) + scene.getTestCameras(scale)

    # get_scale iterates only train cameras. Feature training reads masks and
    # scales on both splits before selecting which cameras to optimize on.
    Scene.getTrainCameras = all_cameras
    sys.argv = [
        "get_scale.py",
        "--model_path",
        str(options.model.resolve()),
        "--source_path",
        str(options.scene.resolve()),
        "--image_root",
        str(options.scene.resolve()),
    ]
    runpy.run_path(str(saga / "get_scale.py"), run_name="__main__")


if __name__ == "__main__":
    main()
