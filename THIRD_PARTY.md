# Third-party software, models, and research baselines

This is an engineering inventory, not legal advice. Verify exact code, nested
dependency, dataset, and model-weight terms before every promoted workflow.

External repositories are fetched into ignored `.external/` directories and
are not part of this repository's MIT-licensed source distribution.

## Pinned week-1 baselines

### Gaussian Grouping

- Upstream: <https://github.com/lkeab/gaussian-grouping>
- Commit: `0ab60afed3385b717c985af1d30a20f7b0884c89`
- Root license: Apache-2.0
- Purpose: identity grouping, removal, and inpainting reference
- Warning: bundled `diff-gaussian-rasterization` derives from the original
  Inria/MPII research-only/non-commercial Gaussian Splatting license.

### SAGA / Segment Any 3D Gaussians

- Upstream: <https://github.com/Jumpat/SegAnyGAussians>
- Commit: `2d4c5d77c857c956d747e4775d3d72c4ec5dfe16` (`v2`)
- Root license: Apache-2.0
- Purpose: click/multi-click per-Gaussian segmentation baseline
- Warning: audit nested rasterizers and checkpoint terms before redistribution.

## Planned comparisons

### gsplat

- Upstream: <https://github.com/nerfstudio-project/gsplat>
- License: Apache-2.0
- Purpose: future modern rasterization/feature backend
- Rule: pin an exact release/commit when its first adapter lands.

### SAM 2

- Upstream: <https://github.com/facebookresearch/sam2>
- Reported upstream licenses: Apache-2.0 and BSD-3-Clause components
- Purpose: 2D mask generation/propagation experiments
- Rule: code and checkpoint licenses are recorded separately.

### Inpaint360GS

- Upstream: <https://github.com/dfki-av/Inpaint360GS>
- License: Apache-2.0
- Purpose: later background-disocclusion comparison

### TRELLIS

- Upstream: <https://github.com/microsoft/TRELLIS>
- Repository license: MIT; weights require separate verification
- Purpose: optional image-conditioned complete-object hypothesis

## Reference-only projects

Code with absent, unclear, restrictive, gated, or incompatible terms may be
studied but not copied without a recorded decision. Current examples include
iSegMan (no usable implementation at review), GaussianCut (no visible license),
InstaScene (no visible repository license), GaussianEditor (custom
non-commercial terms), and Carveout (GPL plus gated/custom dependencies).

## Artifact rule

Every experiment record states code license, weight/checkpoint source and
license, dataset terms, and whether redistribution is allowed. An app-compatible
artifact is not automatically redistributable merely because the adapter is MIT.
