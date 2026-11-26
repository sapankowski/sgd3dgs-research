# Data card: lerf-mask-ramen

Reference scene for SGD3DGS week 1. Manifest: `scene.json` (schema 0.1).

## Files and provenance

| Path | Origin | SHA-256 |
|---|---|---|
| `reconstruction/point_cloud.ply` | `ramen/point_cloud/iteration_30000/` in the checkpoint archive below | `d2fee173a0ec2e98e72fa45483f816ccbec86ab66825d00dc8213220a2a5866a` |
| `reconstruction/classifier.pth` | same directory; Gaussian Grouping identity classifier | `523b9238cc45f443ec1d4c610aa2e759e402e0d7b71251d52e1c6cc88faedbbd` |
| `reconstruction/cfg_args` | `ramen/cfg_args` in the checkpoint archive (training arguments) | `dad99c02e593ce232589463f0d67628f3ee274357eae797c432b139461f02033` |
| `source/ramen/` | full LERF-Mask ramen data archive below: 135 images, COLMAP `sparse/0`, `test_mask/` annotations | archive checksum below |

Archives, from the authors' Hugging Face repository `mqye/Gaussian-Grouping`, revision `34cbf65561144792d7a1861b38274bd7be18c8bc`:

| Archive | Size | SHA-256 |
|---|---:|---|
| `checkpoint/lerf_mask/ramen.zip` | 336,125,370 B | `6b9fbc8e71e5af91e721a8436940f6349d0dd33244d1c3115d6d949b401d66ef` |
| `data/lerf_mask/ramen.zip` | 196,846,820 B | `0f1914280216c111eb924d5f6a8caf6a13122e3a64a5a7b3ffb8615926966b1a` |

Both match the size and SHA-256 that Hugging Face reports for these files. The PLY checksum matches the source checksum in Person 5's Gaussian Grouping experiment (research PR #1), so labels exported there refer to this exact file.

## Contents

- 1,266,122 Gaussians, `binary_little_endian` PLY, 78 vertex properties: position, normal, SH degree 3 (`f_dc_*`, 45 `f_rest_*`), opacity, scale, rotation, plus 16 Gaussian Grouping identity features `obj_dc_0..15`.
- Training arguments (`cfg_args`): SH degree 3, 256 identity classes, `train_split=True`, source `data/lerf_mask/ramen`. The commit that trained the checkpoint is unknown.

## Coordinate system

- Right-handed COLMAP/3DGS world frame; scale arbitrary (`unit: unknown`).
- `up_axis: -Z` is provisional. It is the closest axis to the mean camera up vector over all 135 COLMAP cameras, `[-0.168, -0.550, -0.818]`, so the scene is tilted roughly 35° from that axis. Confirm visually in the editor before relying on it for rotation or floor contact.

## Target object

Yellow bowl, matching Person 5's week-1 target and the `test_mask/{0,1,2}/yellow bowl.png` annotations. It is not yet listed in `scene.json`: schema 0.1 rejects objects without a label set, and no canonical `object_id.npy` exists yet. It becomes `object_id` 1 once the week-2 converter produces labels.

## License and use

The checkpoint host repository declares Apache-2.0. The underlying LERF images come from the LERF dataset; redistribution terms for the images and derived renders are not stated there. Keep these files on team storage; do not commit them or publish renders without checking.

## Handling

Source and reconstruction files are read-only. Derived outputs go under `runs/` and `packages/`, never next to the source files.
