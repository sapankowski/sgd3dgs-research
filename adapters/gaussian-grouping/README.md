# Gaussian Grouping adapter

Converts the Boolean `mask.npy` written by
`scripts/gaussian_grouping/export_labels.py` into a schema 0.1 package with
`sgd3dgs-research convert-mask`.

## Native assumptions

- `mask.npy`: `bool[N]` in source PLY vertex order; `True` where the selected
  class probability is strictly greater than the threshold.
- `confidence.npy` is the maximum softmax probability over all classes, not
  membership evidence for the selected object, so it is not carried into the
  package (`confidence_path: null`).

## Output

`uint16[N]`: `0` background, `object_id` for selected Gaussians. The package
directory contains `scene.json`, `object_id.npy`, `provenance.json`,
`SHA256SUMS` and the source PLY at the manifest's `source.path` (hard link or
copy).

## Ramen yellow bowl

```bash
./scripts/uv.sh run sgd3dgs-research convert-mask \
  --mask "$RUN/mask.npy" --run-report "$RUN/report.json" \
  --source "$SCENE/reconstruction/point_cloud.ply" \
  --manifest experiments/2026/week01-reference-scene-ramen/scene.json \
  --output "$SCENE/packages/0.1" \
  --object-id 1 --object-name "yellow bowl" \
  --method gaussian-grouping --method-version class-108-threshold-0.3
./scripts/validate_with_app.sh "$SCENE/packages/0.1/scene.json"
```

`RUN` is `runs/gaussian-grouping/class-108-threshold-0.3/` and `SCENE` is
`scenes/lerf-mask-ramen/` in the artifact repository.
