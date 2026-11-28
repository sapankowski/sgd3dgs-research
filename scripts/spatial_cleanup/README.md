# Spatial cleanup candidates

This CPU experiment reports small label islands far from the largest selected
component. It never changes the input PLY or mask. Arrays retain source PLY order.
The input is a boolean selection, not native class IDs or canonical object IDs.

Use a dedicated Python 3.12 environment with NumPy, SciPy, plyfile and Pillow.
Install the tested versions with `pip install -r scripts/spatial_cleanup/requirements.txt`.
No training
framework or CUDA extension is needed for analysis.

```bash
python scripts/spatial_cleanup/analyze.py \
  --ply "$CHECKPOINT/point_cloud.ply" --mask "$WEEK1/mask.npy" \
  --voxel-size 0.02 --min-distance 0.1 --max-fraction 0.01 \
  --output "$RUN"
```

`RUN` must be a new directory. Inputs must be finite XYZ positions and a matching
`bool[N]` selection from that exact PLY ordering. Voxel size must be positive,
minimum distance nonnegative, and maximum fraction between 0 and 1. Distances are
in source units; the ramen scene has no known metric scale.

The algorithm groups occupied voxels using six face neighbors, chooses the
component with the most Gaussians as its anchor, and measures each component's
closest center-to-center distance to that anchor. A component is a candidate only
when its gap is at least `min-distance` AND its count is at most `max-fraction`
times the anchor count. The anchor is always retained. Ties for the anchor use
lexicographic voxel order. Near fragments and large separate components remain
unmodified. There is no universal semantic guarantee: a small legitimate detached
part can also qualify, and connected leakage will remain.

Outputs:

- `report.json`: all component counts, gaps, bounds and candidate decisions.
- `candidate_mask.npy`: `bool[N]`, true only at candidate rows of the input mask.
- `preview_mask.npy`: only with `--write-preview`, a separate proposed selection
  equal to the input mask minus candidates. This is not an accepted app label file.

For three-view inspection, rerun with `--write-preview` into a new directory.
Paint both arrays with the existing Week 1 visualization script and render them
with the same camera track, resolution and scene geometry as Week 1:

```bash
PAINT=experiments/2026/week01-gaussian-grouping-ramen/prepare_mask.py
TRACK=experiments/2026/week01-gaussian-grouping-ramen/camera-track.json
python "$PAINT" "$CHECKPOINT/point_cloud.ply" "$RUN/preview_mask.npy" "$RUN/preview-render.ply"
python "$PAINT" "$CHECKPOINT/point_cloud.ply" "$RUN/candidate_mask.npy" "$RUN/candidates-render.ply"
splat-transform "$RUN/preview-render.ply" "$RUN/preview.webp" --camera-track "$TRACK" --resolution 989x731
splat-transform "$RUN/candidates-render.ply" "$RUN/candidates.webp" --camera-track "$TRACK" --resolution 989x731
python scripts/spatial_cleanup/compare_views.py \
  --before "$WEEK1" --run "$RUN" --annotations "$DATASET/test_mask"
```

Use SplatTransform 3.12.0 as in Week 1. Each painted PLY keeps every Gaussian's
geometry and opacity: white denotes the requested selection, black the rest.
The proposed-mask images visualize a changed selection; they do not render a
scene with geometry deleted. `compare_views.py` writes three full-resolution
comparison rows, an overview and IoU/precision/recall at grayscale threshold 128.
The candidate-only rendering includes scene occlusion, so off-camera or occluded
candidates may be invisible in all three views.

Behavior tests cover near/far and large/small components, face adjacency,
negative coordinates, minimum gap, empty selections, original row order and
unchanged inputs. Install pytest, then run:

```bash
python -m pytest -o addopts= scripts/spatial_cleanup/test_analyze.py
```
