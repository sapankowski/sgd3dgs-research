"""Paint a native mask for occlusion-aware rendering of a Gaussian scene."""

import argparse
from pathlib import Path

import numpy as np
from plyfile import PlyData, PlyElement

SH_DC = 0.28209479177387814


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("mask", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    mask = np.load(args.mask)
    vertices = PlyData.read(args.source)["vertex"].data
    fields = [name for name in vertices.dtype.names if not name.startswith(("f_rest_", "obj_dc_"))]
    painted = np.empty(len(vertices), dtype=[(name, vertices.dtype[name]) for name in fields])
    for name in fields:
        painted[name] = vertices[name]

    dc = (mask.astype(np.float32) - 0.5) / SH_DC
    for channel in range(3):
        painted[f"f_dc_{channel}"] = dc
    PlyData([PlyElement.describe(painted, "vertex")]).write(args.output)


if __name__ == "__main__":
    main()
