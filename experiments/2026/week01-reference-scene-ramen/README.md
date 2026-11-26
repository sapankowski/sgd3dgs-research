# Week 1: ramen reference scene

## Question

Which scene is the shared week-1 reference, and is it bound to an exact source PLY?

## Hypothesis

The official Gaussian Grouping ramen checkpoint can be described by a valid schema 0.1 manifest whose source checksum and Gaussian count match the PLY used for the week-1 Gaussian Grouping export.

## Inputs

- Scene: LERF-Mask ramen. The PLY is `ramen/point_cloud/iteration_30000/point_cloud.ply` from `checkpoint/lerf_mask/ramen.zip`; images, COLMAP `sparse/0` and `test_mask/` come from `data/lerf_mask/ramen.zip`. Both are in `mqye/Gaussian-Grouping` on Hugging Face, revision `34cbf65561144792d7a1861b38274bd7be18c8bc`.
- Object: yellow bowl (not yet in the manifest, see below).
- Archive sizes and checksums: [data-card.md](data-card.md).

## Procedure

1. Download both archives and compare their SHA-256 with the values Hugging Face reports.
2. Unpack into the `data/README.md` layout: `data/scenes/lerf-mask-ramen/{reconstruction,source}/`. Make both read-only.
3. Place [scene.json](scene.json) and [data-card.md](data-card.md) in `data/scenes/lerf-mask-ramen/`.
4. Run, from the app repository:

   ```bash
   ./scripts/uv.sh run sgd3dgs validate --check-files <research>/data/scenes/lerf-mask-ramen/scene.json
   ```

5. From the scene directory, read the PLY header and estimate the up axis:

   ```bash
   python -I <experiment>/inspect_scene.py reconstruction/point_cloud.ply source/ramen/sparse/0/images.bin
   ```

## Measurements

- Source PLY SHA-256: `d2fee173a0ec2e98e72fa45483f816ccbec86ab66825d00dc8213220a2a5866a`, the same source checksum as the week-1 Gaussian Grouping export (#1).
- Gaussian count: 1,266,122 (`element vertex` in the PLY header); 78 vertex properties, including 16 Gaussian Grouping identity features `obj_dc_0..15`.
- Validation: `Valid scene=lerf-mask-ramen gaussians=1,266,122 objects=0`.
- Mean camera up over 135 COLMAP cameras: `[-0.168, -0.550, -0.818]`; closest axis `-Z`.
- Hardware: Windows 11 laptop, no GPU.

## Results

The manifest validates against the real files, and its source checksum matches the PLY that the Gaussian Grouping labels were exported from. `objects` is empty because schema 0.1 rejects objects without a label set.

Findings for the team:

1. `validate --check-files` compares checksums but never checks `source.gaussian_count` against the PLY header.
2. `up_axis: -Z` is provisional: the scene is tilted about 35° from that axis.
3. The editor may drop the 16 extra `obj_dc_*` properties or reorder Gaussians; this is a week-3 check.
4. `cameras` is `null` because the schema expects one file and COLMAP poses span `cameras.bin` and `images.bin`.

## Decision

Proposed: adopt `lerf-mask-ramen` as the reference scene. Next: the week-2 converter maps Gaussian Grouping native IDs to `object_id.npy`, after which the yellow bowl is added as `object_id` 1.
