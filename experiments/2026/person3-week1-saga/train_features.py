"""Train pinned SAGA after excluding mask/scale pairs without usable scale."""

import argparse
import runpy
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--saga", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    options = parser.parse_args()
    saga = options.saga.resolve()
    sys.path.insert(0, str(saga))
    from scene import dataset_readers

    read_cameras = dataset_readers.readColmapCameras

    def read_valid_scales(*args, **kwargs):
        cameras = read_cameras(*args, **kwargs)
        filtered = []
        dropped = 0
        for camera in cameras:
            if camera.mask_scales is None or camera.masks is None:
                raise ValueError(f"Missing masks or scales for {camera.image_name}")
            scales = camera.mask_scales
            valid = scales.isfinite() & (scales > 0)
            if int(valid.sum()) < 2:
                raise ValueError(f"Fewer than two usable scales for {camera.image_name}")
            dropped += len(scales) - int(valid.sum())
            filtered.append(
                camera._replace(
                    masks=camera.masks[valid.to(camera.masks.device)],
                    mask_scales=scales[valid],
                )
            )
        print(f"Filtered {dropped} invalid mask/scale pairs across {len(cameras)} views.")
        return filtered

    dataset_readers.readColmapCameras = read_valid_scales
    sys.argv = [
        "train_contrastive_feature.py",
        "-m",
        str(options.model.resolve()),
        "--iteration",
        "7000",
        "--iterations",
        str(options.iterations),
        "--num_sampled_rays",
        "1000",
        "--save_iterations",
        str(options.iterations),
    ]
    runpy.run_path(str(saga / "train_contrastive_feature.py"), run_name="__main__")


if __name__ == "__main__":
    main()
