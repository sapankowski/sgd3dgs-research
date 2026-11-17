# Open-source research landscape

Last reviewed: 2026-11-17. Re-check upstream state and licenses before adoption.

## Foundations

### SuperSplat

- Repository: <https://github.com/playcanvas/supersplat>
- Role: interactive browser editor and product foundation
- Strengths: mature WebGPU editor, picking, selection, transform tools, command
  history, import/export, active development
- License: MIT
- Project decision: application foundation, bundled only in `sgd3dgs-app`

### gsplat

- Repository: <https://github.com/nerfstudio-project/gsplat>
- Role: modern research rasterizer/backend
- Strengths: Apache-2.0, N-dimensional feature and depth rendering, active tests
- Project decision: future primary CUDA backend here; pin when integrated

## Segmentation baselines

### Gaussian Grouping

- Repository: <https://github.com/lkeab/gaussian-grouping>
- Method: joint reconstruction and identity encoding supervised by 2D masks
- Strengths: open-world instance grouping, removal, and an inpainting baseline
- Limitations: old PyTorch/CUDA stack and batch/config-oriented workflow
- License warning: Apache-2.0 root but nested original rasterizer is
  research/non-commercial
- Project decision: reproduce as a baseline, then implement supported concepts
  against gsplat rather than making it the application skeleton

### SAGA / Segment Any 3D Gaussians

- Repository: <https://github.com/Jumpat/SegAnyGAussians>
- Method: learned per-Gaussian affinity features and click-driven segmentation
- Strengths: click/multi-click GUI and exported per-Gaussian binary masks
- Limitations: Python 3.7/PyTorch 1.12-era environment; no object manipulation
- Project decision: second week-1 baseline and likely source of the fastest first
  mask-to-editor bridge

### GaussianCut

- Repository: <https://github.com/umangi-jain/gaussiancut>
- Strengths: graph-cut boundary refinement from sparse interaction
- Limitations: small repository and no visible license
- Project decision: research reference only unless licensing is clarified

### iSegMan

- Repository: <https://github.com/Zhao-Yian/iSegMan>
- Strengths: directly targets interactive segment-and-manipulate behavior
- Limitation: current repository contains a README but no implementation
- Project decision: watch for code; do not plan around an unavailable release

## Product/prototype references

### Gaussian Interior Editor

- Repository: <https://github.com/al-fayed1998/gaussian-interior-editor>
- Strengths: browser selection, movement, rotation, hiding, replacement, and a
  practical Gaussian Grouping pipeline
- Limitations: one-commit thesis release, monolithic viewer, bounding-box based
  object picking, and little maintenance history
- Project decision: study interaction and repair ideas, not the primary fork

### Carveout

- Repository: <https://github.com/smallfly/Carveout>
- Strengths: no scene-specific training, browser-guided workflow, per-object PLY
  export and metadata
- Limitations: GPL, gated/custom SAM 3 dependency, explicitly not maintained
- Project decision: optional external benchmark only

## Completion and repair

### Inpaint360GS

- Repository: <https://github.com/dfki-av/Inpaint360GS>
- Role: first serious background-disocclusion comparison
- License: Apache-2.0
- Project decision: evaluate after the interaction MVP and simple reprojection
  baseline are complete

### TRELLIS

- Repository: <https://github.com/microsoft/TRELLIS>
- Role: optional image-conditioned complete-object hypothesis
- License: MIT for code; verify weights separately
- Limitation: generated unseen geometry is plausible, not ground truth
- Project decision: one controlled week-8 spike, with observed Gaussians locked

### InstaScene

- Repository: <https://github.com/zju3dv/InstaScene>
- Strengths: combines instance decomposition with in-situ generative completion
- Limitation: no visible repository license at review time
- Project decision: conceptual reference only

## Evaluation rule

Source availability is not sufficient. A supported dependency must have a usable
license, reproducible environment, maintained or understandable code, compatible
data contracts, and evidence that it improves the project's controlled scenes.
