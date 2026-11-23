# Week 1: Gaussian Grouping on the ramen scene

A CPU export from the official Gaussian Grouping checkpoint selected 63,202
of 1,266,122 Gaussians (4.99%) for the yellow bowl. The rendered selection had
a mean mask IoU of 93.5% across the three annotated LERF-Mask views. It covered
the bowl in each view, with some leakage near the rim and onto the table.
Keep this checkpoint as a reproducible fallback for label export. Defer the
choice of a team segmentation baseline until there is a matched comparison.

## Inputs

- Scene: the authors' [LERF-Mask ramen archive](https://huggingface.co/mqye/Gaussian-Grouping/blob/34cbf65561144792d7a1861b38274bd7be18c8bc/data/lerf_mask/ramen.zip).
  Use the COLMAP cameras for `test_0.jpg` through `test_2.jpg` and the
  `test_mask/{0,1,2}/yellow bowl.png` annotations.
- Model: the authors' [ramen checkpoint](https://huggingface.co/mqye/Gaussian-Grouping/blob/34cbf65561144792d7a1861b38274bd7be18c8bc/checkpoint/lerf_mask/ramen.zip).
  Both `point_cloud.ply` and `classifier.pth` come from
  `ramen/point_cloud/iteration_30000/`. The [experiment record](experiment.yaml)
  identifies the source PLY and reference code revision. The commit that
  trained the published checkpoint is unknown.
- Target: the visible yellow bowl, excluding the food. Class 108 was the
  most frequent native ID among projected Gaussian centers inside the bowl
  annotation in each of the three views. Those views were also used for the
  measurements below, so the scores describe this example rather than
  performance on independent evaluation data.

## Reproduce

Use the [export environment](../../../scripts/gaussian_grouping/README.md) with
Python 3.12.3, PyTorch 2.6.0+cpu, NumPy 2.5.5, and plyfile 1.1.5. Set
`CHECKPOINT` to the extracted iteration directory and `RESULT` to an unused
output directory. Run from the repository root:

```bash
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 python scripts/gaussian_grouping/export_labels.py \
  --ply "$CHECKPOINT/point_cloud.ply" --classifier "$CHECKPOINT/classifier.pth" \
  --select-id 108 --threshold 0.3 --output "$RESULT"

python experiments/2026/week01-gaussian-grouping-ramen/prepare_mask.py \
  "$CHECKPOINT/point_cloud.ply" "$RESULT/mask.npy" "$RESULT/mask-render.ply"
```

The exporter writes `native_id.npy` (int64 argmax class), `confidence.npy`
(float32 maximum softmax probability), `mask.npy` (boolean, class 108 softmax
probability strictly greater than 0.3), and `report.json`. All arrays follow the
original PLY vertex order. Class IDs apply to this trained PLY and classifier.

Install [SplatTransform](https://developer.playcanvas.com/user-manual/splat-transform/cli-reference/)
with Node.js 22 or later (`npm install -g @playcanvas/splat-transform@3.12.0`).
Render the source and the visualization PLY at the same camera poses:

```bash
TRACK=experiments/2026/week01-gaussian-grouping-ramen/camera-track.json
splat-transform "$CHECKPOINT/point_cloud.ply" "$RESULT/scene.webp" \
  --camera-track "$TRACK" --resolution 989x731
splat-transform "$RESULT/mask-render.ply" "$RESULT/mask.webp" \
  --camera-track "$TRACK" --resolution 989x731
```

The visualization PLY gives selected Gaussians white color and the rest black,
while preserving their opacity, geometry, and occlusion. The checked-in
camera track uses the COLMAP views in test order, with the PLY-to-PlayCanvas
coordinate rotation. For each `mask.000N.webp`, threshold grayscale at
128 and compare with the annotation at the same threshold. IoU is intersection
over union. Precision and recall divide the intersection by the predicted
and annotated areas respectively.

## Measurements

| Camera | IoU | Precision | Recall |
| --- | ---: | ---: | ---: |
| test_0 | 94.08% | 95.21% | 98.75% |
| test_1 | 94.33% | 94.99% | 99.27% |
| test_2 | 92.13% | 94.06% | 97.82% |

- Export took 2.407 s on WSL2 with an Intel Core Ultra 7 251HX and four
  CPU threads, including file reads and writes. It used no GPU.
- Rendering used an RTX 5060 Laptop GPU on Windows. SplatTransform reported
  338.4 MB peak GPU allocation for the three mask views and 555.8 MB for the
  three source views. These are visualization measurements.
- The selected centers span `[-6.117, -1.860, -6.372]` to
  `[7.594, 19.192, 7.672]` in PLY units. At 0.02-unit voxel size with
  face-connected neighbors, the mask has 3,953 occupied components, and
  the largest contains 55,396 Gaussians (87.65% of the mask). The large
  bounding box and small components show why visible agreement alone is
  insufficient for moving the object. No components were removed.
- Full values are in [metrics.json](metrics.json). Arrays, render logs and
  all three overlays are retained in the local run directory. The input
  archives, camera track and commands above let reviewers regenerate them.

## Comparison with SAGA

[Gaussian Grouping](https://arxiv.org/abs/2312.00732) assigns identities using
features and a classifier trained with the scene. A selected ID and threshold
give a repeatable mask on that checkpoint. [SAGA](https://arxiv.org/abs/2312.00860)
uses learned affinities and visual prompts, so a user can select an object or
part at a chosen scale. For either method the exported mask must match the
Gaussian ordering of the exact PLY it was produced from. The Gaussian
Grouping result here measures CPU export from a prepared checkpoint.
A matched SAGA result is unavailable, so there is no measured comparison of
quality, elapsed time, or GPU memory.

## Licensing

The root Gaussian Grouping project is Apache-2.0. The legacy CUDA rasterizer
and nearest-neighbor extension have separate upstream notices, and DEVA has
its own terms. See the [dependency inventory](../../../THIRD_PARTY.md).
The authors' Hugging Face repository declares Apache-2.0. Its metadata does
not separately explain redistribution of the underlying LERF images or
derived previews. This contribution publishes the procedure, camera
configuration and numeric measurements.
