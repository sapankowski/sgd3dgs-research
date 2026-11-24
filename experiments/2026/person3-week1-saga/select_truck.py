"""Apply the pinned SAGA GUI click scoring to recorded camera pixels."""

import argparse
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageDraw
from plyfile import PlyData
from scipy import ndimage


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def to_image(tensor: torch.Tensor) -> Image.Image:
    return Image.fromarray(
        tensor.clamp(0, 1).mul(255).round().byte().permute(1, 2, 0).cpu().numpy()
    )


def components(xyz: np.ndarray) -> dict:
    # Use isotropic voxels, 128 along the longest selected bounding-box axis.
    low = xyz.min(axis=0)
    spacing = float(np.ptp(xyz, axis=0).max()) / 128
    if not spacing:
        return {"voxel_size": 0.0, "count": 1, "largest_points": len(xyz)}
    indices = np.floor((xyz - low) / spacing).astype(np.int32).T
    grid = np.zeros(tuple(indices.max(axis=1) + 1), dtype=bool)
    cells = tuple(indices)
    grid[cells] = True
    labeled, number = ndimage.label(grid, structure=np.ones((3, 3, 3), dtype=bool))
    counts = np.bincount(labeled[cells])
    return {
        "voxel_size": spacing,
        "count": number,
        "largest_points": int(counts[1:].max()),
        "outside_largest_points": int(len(xyz) - counts[1:].max()),
    }


@torch.no_grad()
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saga", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--scene", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--click", nargs=3, action="append", required=True, metavar=("CAMERA", "X", "Y")
    )
    parser.add_argument("--views", nargs=3, default=["000001", "000065", "000193"])
    parser.add_argument("--scale", type=float, default=0.5)
    parser.add_argument("--threshold", nargs="+", type=float, default=[0.9, 0.94, 0.97])
    parser.add_argument("--export", action="store_true")
    options = parser.parse_args()
    if options.export and len(options.threshold) != 1:
        parser.error("--export requires one reviewed threshold")
    started = time.perf_counter()
    sys.path.insert(0, str(options.saga.resolve()))
    from arguments import ModelParams, PipelineParams
    from gaussian_renderer import render, render_contrastive_feature
    from scene import FeatureGaussianModel, GaussianModel, Scene

    model_path = options.model.resolve()
    cloud = model_path / "point_cloud/iteration_7000/scene_point_cloud.ply"
    feature_path = model_path / "point_cloud/iteration_2000/contrastive_feature_point_cloud.ply"
    cloud_xyz = PlyData.read(cloud)["vertex"].data
    feature_xyz = PlyData.read(feature_path)["vertex"].data
    if len(cloud_xyz) != len(feature_xyz) or any(
        not np.array_equal(cloud_xyz[axis], feature_xyz[axis]) for axis in "xyz"
    ):
        raise ValueError("Feature PLY does not match source PLY row order")
    setup = argparse.ArgumentParser()
    model_params, pipe_params = ModelParams(setup), PipelineParams(setup)
    config = setup.parse_args(
        [
            "-s",
            str(options.scene.resolve()),
            "-m",
            str(model_path),
            "-r",
            "4",
            "--data_device",
            "cpu",
            "--eval",
        ]
    )
    dataset, pipeline = model_params.extract(config), pipe_params.extract(config)
    gaussians = GaussianModel(dataset.sh_degree)
    features = FeatureGaussianModel(dataset.feature_dim)
    scene = Scene(
        dataset, gaussians, None, load_iteration=7000, shuffle=False, mode="eval", target="scene"
    )
    features.load_ply(str(feature_path))
    camera_map = {
        camera.image_name: camera for camera in scene.getTrainCameras() + scene.getTestCameras()
    }
    heldout = {camera.image_name for camera in scene.getTestCameras()}
    if not set(options.views) <= heldout:
        raise ValueError("All visual checks must use held-out cameras")
    scale_gate = torch.nn.Sequential(torch.nn.Linear(1, 32), torch.nn.Sigmoid()).cuda()
    scale_gate.load_state_dict(
        torch.load(feature_path.with_name("scale_gate.pt"), weights_only=True)
    )
    gate = scale_gate(torch.tensor([options.scale], device="cuda"))
    black = torch.zeros(3, device="cuda")
    feature_background = torch.zeros(32, device="cuda")
    prompts = []
    feature_maps = {}
    for name, x_text, y_text in options.click:
        x, y = int(x_text), int(y_text)
        if name not in feature_maps:
            camera = camera_map[name]
            camera.feature_width = camera.image_width
            camera.feature_height = camera.image_height
            feature_maps[name] = render_contrastive_feature(
                camera, features, pipeline, feature_background
            )["render"]
        feature_map = feature_maps[name]
        if not (0 <= y < feature_map.shape[1] and 0 <= x < feature_map.shape[2]):
            raise ValueError(f"Click {(name, x, y)} falls outside the feature image")
        prompts.append(torch.nn.functional.normalize(feature_map[:, y, x] * gate, dim=0))
    point_features = torch.nn.functional.normalize(features.get_point_features * gate, dim=1)
    scores = ((point_features @ torch.stack(prompts, dim=1) + 1) / 2).amax(dim=1)
    if tuple(scores.shape) != (len(cloud_xyz),) or not torch.isfinite(scores).all():
        raise ValueError("Invalid SAGA scores")

    options.out.mkdir(parents=True, exist_ok=True)
    rows = len(options.threshold) + 1
    sheet = Image.new("RGB", (3 * 245, rows * 155), "white")
    labels = ImageDraw.Draw(sheet)
    for col, name in enumerate(options.views):
        sheet.paste(
            to_image(render(camera_map[name], gaussians, pipeline, black)["render"]), (col * 245, 0)
        )
        labels.text((col * 245 + 3, 137), f"{name} full scene", fill="black")
    for row, threshold in enumerate(options.threshold, 1):
        mask = scores > threshold
        count = int(mask.sum())
        print(f"threshold={threshold} selected={count}/{len(mask)}", flush=True)
        if options.export and not 0 < count < len(mask):
            raise ValueError("Reviewed mask must select a nonempty proper subset")
        for col, name in enumerate(options.views):
            rgb = to_image(
                render(camera_map[name], gaussians, pipeline, black, filtered_mask=~mask)["render"]
            )
            sheet.paste(rgb, (col * 245, row * 155))
            labels.text(
                (col * 245 + 3, row * 155 + 137), f"{threshold:.3f} N={count}", fill="black"
            )
            if options.export:
                rgb.save(options.out / f"truck-{name}.png")
        if not options.export:
            continue
        kept = mask.cpu().numpy()
        mask_path = options.out / "mask.npy"
        ids_path = options.out / "object_id.npy"
        np.save(mask_path, kept, allow_pickle=False)
        np.save(ids_path, kept.astype(np.uint16), allow_pickle=False)
        packed = options.out / "mask.bits.gz"
        packed.write_bytes(gzip.compress(np.packbits(kept, bitorder="little").tobytes(), mtime=0))
        xyz = np.column_stack([cloud_xyz[axis][kept] for axis in "xyz"])
        receipt = {
            "source_sha256": sha256(cloud),
            "feature_sha256": sha256(feature_path),
            "mask_sha256": sha256(mask_path),
            "object_id_sha256": sha256(ids_path),
            "packed_mask_sha256": sha256(packed),
            "vertices": len(mask),
            "selected": count,
            "fraction": count / len(mask),
            "bounds_min": xyz.min(axis=0).tolist(),
            "bounds_max": xyz.max(axis=0).tolist(),
            "voxel_components": components(xyz),
            "clicks": options.click,
            "held_out_views": options.views,
            "scale": options.scale,
            "threshold": threshold,
            "elapsed_seconds": time.perf_counter() - started,
            "peak_torch_vram_bytes": torch.cuda.max_memory_allocated(),
        }
        (options.out / "selection.json").write_text(json.dumps(receipt, indent=2) + "\n")
    sheet.save(options.out / "comparison.png")


if __name__ == "__main__":
    main()
