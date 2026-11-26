# Gaussian Grouping native label export

Export per-Gaussian identities from a trained Gaussian Grouping PLY and its
matching `classifier.pth`. The tool follows the checkpoint layout at reference
commit `0ab60afed3385b717c985af1d30a20f7b0884c89`.

## Setup

Create a dedicated Python 3.12 environment. These versions were used for the CPU
validation on Linux/WSL2.

```bash
python3.12 -m venv /path/to/gg-export-env
source /path/to/gg-export-env/bin/activate
python -m pip install numpy==2.5.5 plyfile==1.1.5
python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
```

## Run

Use the PLY and classifier from the same trained iteration. The PLY must contain
`obj_dc_0` through `obj_dc_15`. Choose target IDs by inspecting the scene's
segmentation renders. IDs must be valid classifier indices, threshold must be
between 0 and 1, and chunk size must be positive.

```bash
python scripts/gaussian_grouping/export_labels.py \
  --ply /shared/gg/point_cloud.ply \
  --classifier /shared/gg/classifier.pth \
  --select-id 34 --threshold 0.3 \
  --output /shared/results/gg-export-001
```

Repeat `--select-id` to select multiple IDs, or omit it to export every native
identity. Use a new output directory for each run. `report.json` is written last
and indicates that the export finished. If a run is interrupted during output,
retry with a new directory.

## Files and meaning

| File | Meaning |
| --- | --- |
| `native_id.npy` | int64[N], highest-probability native class per vertex |
| `confidence.npy` | float32[N], maximum softmax probability |
| `mask.npy` | bool[N], present when target IDs were specified |
| `report.json` | Input filenames, count, histogram, selection bounds, runtime and environment |

The mask selects vertices where any requested class has probability strictly
greater than the threshold. Its selected class can differ from the argmax class.
This follows upstream's raw selection before convex-hull expansion.

Rows retain the original PLY vertex order. Classification runs in float32 chunks.
The output IDs are method-native. The app's canonical `uint16[N]` format requires
a reviewed mapping of background, movable objects and unknown IDs. Person 4 owns
that conversion. Training can change Gaussian count and ordering through
densification and pruning, so these labels belong to this trained PLY.

## Verify

Install pytest in the dedicated environment, then run from the repository root.

```bash
python -m pytest -o addopts= scripts/gaussian_grouping/test_export_labels.py
```

Three tests check the normal CLI against upstream-style Conv2d classification,
chunk-size consistency, and export without a target mask. The repository's base
environment separately runs `make verify`.

## Provenance

The reference algorithm is in upstream
[edit_object_removal.py](https://github.com/lkeab/gaussian-grouping/blob/0ab60afed3385b717c985af1d30a20f7b0884c89/edit_object_removal.py).
The exporter is new project code under the repository MIT license. It imports
NumPy, PyTorch and plyfile. The original rasterizer and method source are external.
Checkpoint and dataset terms must be recorded for each research run.
See [THIRD_PARTY.md](../../THIRD_PARTY.md) and the actual
[validation record](VALIDATION.md).
