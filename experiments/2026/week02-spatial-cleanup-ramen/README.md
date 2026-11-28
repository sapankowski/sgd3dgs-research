# Week 2: conservative spatial cleanup of the ramen yellow bowl

## Decision

Keep cleanup **report-only and default-off**. The spike identifies 4,293 distant
candidate Gaussians in 2,501 islands, but excluding them lowers bowl recall in all
three inspected views. Candidates require review; this is not an accepted cleanup
of the canonical labels. Original PLY geometry and selection remain unchanged.

Owner: Person 5. Review: request a reviewer outside the Person 5/6 pair.
Scope: spatial label cleanup only; no inpainting, canonical converter or editor
changes. Budget: one 5–8 hour task, stopping after CPU analysis and three matched
views. Hypothesis: small distant islands can be flagged while retaining the main
bowl component; whether the proposed exclusion preserves visible bowl coverage
must be measured rather than assumed.

## Inputs and source alignment

Code starts from the latest merged Research `main` retrieved for this task,
including Week 1 PRs #1 and #2. The authoritative task is Person 5 in
[Week 2 of the app work plan](https://github.com/sapankowski/sgd3dgs-app/blob/main/docs/WORK_PLAN.md).

The scene is the team's
[ramen reconstruction](https://huggingface.co/datasets/SGD3DGS/sgd3dgs-artifacts/tree/main/scenes/lerf-mask-ramen/reconstruction),
with 1,266,122 Gaussians. Both `point_cloud.ply` and `classifier.pth` were downloaded
from that location and compared directly, byte for byte, against the Week 1
inputs: both matched. Thus the retained Week 1 arrays use this exact PLY order.

The raw boolean mask is the [Week 1 Gaussian Grouping export](../week01-gaussian-grouping-ramen/README.md):
native class 108, softmax probability strictly greater than 0.3, 63,202 selected
Gaussians. It is not an argmax mask or a canonical `object_id.npy`.
The three camera poses and LERF yellow-bowl annotations are also those of Week 1.
Input arrays and rendered views were reused after checking source alignment.
No shared-storage app-ready package is claimed here.

## Method and measurements

Use 0.02-unit voxels with six face neighbors. The largest component by Gaussian
count is the anchor: 55,396 Gaussians, 87.65% of the original selection, among
3,953 occupied components. A component is a candidate only if its closest center
is at least 0.1 source units from the anchor AND its Gaussian count is at most 1%
of the anchor. This retains nearby fragments and larger disconnected structures.
The source's physical scale is unknown.

| Quantity | Result |
| --- | ---: |
| Original selection | 63,202 |
| Candidate islands | 2,501 |
| Candidate Gaussians | 4,293 (6.79% of selection) |
| Proposed retained selection | 58,909 |
| CPU analysis, including reads and array writes | 2.256 s |
| Render peak GPU allocation | 338.4 MB |

The source selection bounds are `[-6.117, -1.860, -6.372]` to
`[7.594, 19.192, 7.672]`. The proposed selection bounds are
`[-1.860, 0.609, 0.993]` to `[0.956, 2.740, 3.074]`.

Distance sensitivity, keeping voxel size and size limit fixed:

| Minimum gap | Candidate islands | Candidate Gaussians |
| ---: | ---: | ---: |
| 0.05 | 2,902 | 4,967 |
| 0.10 | 2,501 | 4,293 |
| 0.20 | 2,114 | 3,696 |

These are candidate-count comparisons, not visual validation of the alternate
thresholds. Voxel origin is the source coordinate origin; resolution and grid
phase can change connected components. Parameters are scene-specific.

## Three-view evidence

Each before/after mask is rendered with every source Gaussian present, preserving
geometry, opacity and occlusion. Only selection colors change. These are proposed
selection comparisons, not renders after deleting geometry or moving the bowl.

| View | IoU before → proposed | Precision before → proposed | Recall before → proposed |
| --- | --- | --- | --- |
| test_0 | 94.08% → 94.09% | 95.21% → 95.51% | 98.75% → 98.45% |
| test_1 | 94.33% → 94.26% | 94.99% → 95.26% | 99.27% → 98.90% |
| test_2 | 92.13% → 92.45% | 94.06% → 95.42% | 97.82% → 96.74% |

Mean IoU changes from 93.51% to 93.60%. Precision improves in every view, but recall
falls by 0.30, 0.37 and 1.08 percentage points respectively. The side view has the
largest tradeoff. Visual inspection confirms that the broad bowl selection stays
intact; some weak selection around the table and bowl boundary disappears.
Neither this inspection nor IoU establishes that every distant component is noise.
Candidates outside these views or behind other surfaces are not visually audited.
The three views were already used to choose class 108 in Week 1, so they are not
held-out evaluation data.

The local run contains `three-views.png` and full-resolution `comparison-0.png`
through `comparison-2.png`, with columns: original selection, proposed selection,
candidates in red, and the LERF annotation. [metrics.json](metrics.json) contains
full precision values; per-component decisions are in the run's `report.json`.

## Reproduction

Python 3.12.3 on WSL2, Intel Core Ultra 7 251HX; rendering on Windows with an
RTX 5060 Laptop GPU and SplatTransform 3.12.0. Python package versions are in
[scripts/spatial_cleanup/requirements.txt](../../../scripts/spatial_cleanup/requirements.txt).
Analysis does not use a GPU. Visualization preserves Week 1's 989×731 resolution
and camera track.

Set `CHECKPOINT` to the team's reconstruction directory, `WEEK1` to the raw export
and source/mask render directory, `DATASET` to extracted LERF ramen, and `RUN` to
an unused directory. If Week 1 arrays are unavailable, regenerate them using the
linked Week 1 export instructions; do not substitute a different checkpoint.

```bash
python -m pip install -r scripts/spatial_cleanup/requirements.txt
python scripts/spatial_cleanup/analyze.py \
  --ply "$CHECKPOINT/point_cloud.ply" --mask "$WEEK1/mask.npy" \
  --voxel-size 0.02 --min-distance 0.1 --max-fraction 0.01 \
  --output "$RUN" --write-preview
```

Then follow the [three-view rendering commands](../../../scripts/spatial_cleanup/README.md).
For the distance sensitivity runs, change only `--min-distance` to 0.05 or 0.2,
choose separate output directories and omit `--write-preview`.

## Validation and handoff

- Five targeted tests cover connectivity, distance/size decisions, source order,
  input preservation and opt-in preview behavior.
- New Python scripts pass Ruff lint and formatting checks.
- A fresh CPU environment reproduces identical candidate and preview arrays from
  the PLY downloaded from team storage, using only the declared dependencies.
- The repository's `make verify` passes: lint, strict mypy, four existing tests,
  sample experiment validation and repository structure checks.
- A separate CI job runs the spatial-cleanup tests with their own CPU dependencies.
- No source data is removed, relabeled in place or reordered.

Prepared upload layout:
`scenes/lerf-mask-ramen/runs/spatial-cleanup/week02-yellow-bowl-001/`.
It contains real Week 1 native arrays, original selection, candidate and proposed
masks, three-view renders, comparison PNGs, reports, camera track and render logs.
Large files remain outside Git tracking. Shared-storage upload is pending an
authenticated Hugging Face account with write access; no remote artifact URL is
claimed to exist. The repository API currently reports `private: false`, despite
the README describing private storage; confirm intended visibility before
publishing the image bundle there.

The analysis code is MIT, with NumPy/SciPy/plyfile/Pillow dependencies. Model and
scene terms remain those documented in Week 1 and the repository's
[third-party inventory](../../../THIRD_PARTY.md). This spike does not change them.
For Week 3, review difficult boundaries and detached true parts before considering
an automatic cleanup policy. Connected leakage and semantic mistakes are outside
what this spatial rule can solve.
