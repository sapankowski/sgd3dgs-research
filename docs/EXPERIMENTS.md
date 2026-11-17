# Experiment protocol

## 1. Why a protocol is necessary

Gaussian Splatting research often produces visually compelling demos that are
difficult to reproduce or compare. SGD3DGS treats an experiment as a decision
record, not a folder of screenshots.

This repository owns research evidence. The app repository owns product
behavior and the canonical scene schema.

## 2. Before running

Create an experiment directory from `experiments/templates/` and specify:

- the decision this run will inform;
- a falsifiable hypothesis;
- scene ID and source checksum;
- target object/region;
- upstream repository and exact commit;
- environment/container lock;
- command and configuration;
- planned measurements;
- a stopping condition that fits the contributor's weekly time budget.

Validate the record before execution:

```bash
./scripts/uv.sh run sgd3dgs-research validate-experiment \
  experiments/<year>/<experiment-id>/experiment.yaml
```

Examples of useful hypotheses:

- “SAGA multi-click will reduce visible chair-boundary leakage compared with one
  click without selecting more than 5% additional Gaussians.”
- “A 5×5 weighted click vote will choose the correct object in at least 18 of 20
  annotated clicks where single-pixel picking fails at boundaries.”

“Try Gaussian Grouping” is not a hypothesis.

## 3. Minimum measurements

Every method run records:

- runtime;
- GPU model and peak VRAM if available;
- source and output checksums;
- selected Gaussian count and percentage;
- spatial bounding box and outlier/component statistics;
- at least three views of the result;
- commands and manual corrections;
- failure conditions.

Later quantitative work adds rendered-mask IoU, boundary F1, click latency,
transform frame rate, PSNR, SSIM, LPIPS, and controlled disocclusion metrics.

## 4. Artifact handling

Large outputs go to shared storage or the ignored `artifacts/` directory. Commit
small configuration, metrics, and reports. An artifact link without an input
checksum and generating command is insufficient provenance.

## 5. Review

At the Tuesday meeting, the owner presents the question, evidence, and proposed
decision in five minutes. The reviewer confirms reproducibility or records what
is missing. The outcome is one of:

- adopt into the main path;
- repeat with one specified change;
- reject with evidence;
- defer because a prerequisite is missing.

Only adopted experiments become product backlog items.

An adopted artifact still must pass `scripts/validate_with_app.sh`; visual
quality does not override the app contract.

## 6. Time-boxing

An experiment should consume no more than the person's normal weekly allocation
unless the team explicitly trades away another task. If an installation consumes
half the budget without producing a smoke test, preserve logs and switch to a
prepared output or simpler fixture. This is especially important for legacy CUDA
code.
