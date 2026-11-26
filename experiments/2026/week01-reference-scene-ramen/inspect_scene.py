"""Inspect a 3DGS PLY header and estimate the scene up axis from COLMAP poses.

Usage: python -I inspect_scene.py <point_cloud.ply> <sparse/0/images.bin>
Pure standard library, so it runs without the research environments.
"""

import struct
import sys
from pathlib import Path


def read_ply_header(path: Path) -> tuple[str, list[tuple[str, int, list[str]]]]:
    """Return the PLY format line and a list of (element, count, properties)."""
    elements: list[tuple[str, int, list[str]]] = []
    fmt = ""
    with path.open("rb") as handle:
        if handle.readline().strip() != b"ply":
            raise ValueError(f"{path} is not a PLY file")
        for raw in handle:
            line = raw.decode("ascii").strip()
            if line == "end_header":
                break
            parts = line.split()
            if parts[0] == "format":
                fmt = " ".join(parts[1:])
            elif parts[0] == "element":
                elements.append((parts[1], int(parts[2]), []))
            elif parts[0] == "property":
                elements[-1][2].append(parts[-1])
    return fmt, elements


def quat_to_rot(w: float, x: float, y: float, z: float) -> list[list[float]]:
    """COLMAP quaternion (world-to-camera rotation) as a 3x3 row-major matrix."""
    return [
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
    ]


def camera_up_vectors(images_bin: Path) -> list[tuple[float, float, float]]:
    """World-frame 'up' of every camera: R^T @ (0, -1, 0), since COLMAP's y axis points down."""
    ups = []
    with images_bin.open("rb") as handle:
        (num_images,) = struct.unpack("<Q", handle.read(8))
        for _ in range(num_images):
            _image_id, qw, qx, qy, qz, _tx, _ty, _tz, _camera_id = struct.unpack(
                "<i7di", handle.read(64)
            )
            while handle.read(1) != b"\x00":  # image name, null-terminated
                pass
            (num_points,) = struct.unpack("<Q", handle.read(8))
            handle.seek(24 * num_points, 1)  # (x, y, point3D_id) per keypoint
            r = quat_to_rot(qw, qx, qy, qz)
            # Row 1 of R is the camera y axis in world coordinates; up is its negative.
            ups.append((-r[1][0], -r[1][1], -r[1][2]))
    return ups


def main() -> None:
    ply_path, images_bin = Path(sys.argv[1]), Path(sys.argv[2])
    fmt, elements = read_ply_header(ply_path)
    print(f"PLY format: {fmt}")
    for name, count, props in elements:
        print(f"element {name}: {count} ({len(props)} properties)")
        print("  " + ", ".join(props))

    ups = camera_up_vectors(images_bin)
    mean = [sum(u[i] for u in ups) / len(ups) for i in range(3)]
    norm = sum(c * c for c in mean) ** 0.5
    mean = [c / norm for c in mean]
    axis = max(range(3), key=lambda i: abs(mean[i]))
    sign = "+" if mean[axis] > 0 else "-"
    print(f"cameras: {len(ups)}")
    print(f"mean camera up (unit): [{mean[0]:.3f}, {mean[1]:.3f}, {mean[2]:.3f}]")
    print(f"closest axis: {sign}{'XYZ'[axis]} (|component| = {abs(mean[axis]):.3f})")


if __name__ == "__main__":
    main()
