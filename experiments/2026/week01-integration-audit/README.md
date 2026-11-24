# Week 1 integration evidence audit

## Purpose

This Person 6 record consolidates what the repository proves about the accepted
`lerf-mask-ramen` reference scene and yellow-bowl target as of 2026-11-24. It
reviews three Week 1 research contributions without replacing their reports:

- [reference-scene PR #2](https://github.com/sapankowski/sgd3dgs-research/pull/2);
- [Gaussian Grouping PR #1](https://github.com/sapankowski/sgd3dgs-research/pull/1);
- [SAGA truck PR #8](https://github.com/sapankowski/sgd3dgs-research/pull/8).

The audit deliberately does not define a SAGA procedure, prepare a meeting
script, implement the Week 2 converter, or claim that unavailable large
artifacts were independently inspected.

## Accepted reference

- Scene: `lerf-mask-ramen`.
- Target: yellow bowl, excluding the food.
- Source PLY Gaussian count: `1,266,122`.
- Source PLY SHA-256:
  `d2fee173a0ec2e98e72fa45483f816ccbec86ab66825d00dc8213220a2a5866a`.
- Current measured method: Gaussian Grouping class 108 at threshold 0.3.

Both Week 1 records name the same PLY checksum and count. This establishes a
consistent source identity for the reported mask. It does not replace an
artifact-level checksum check after the PLY and mask are published.

## Repository-contained verification

| Check | Result | Evidence |
|---|---|---|
| PR #1 research CI | Pass | GitHub `check` and `structure` jobs |
| PR #2 research CI | Pass | GitHub `check` and `structure` jobs |
| Gaussian Grouping exporter tests | 3 passed | Isolated Python 3.12, PyTorch 2.6.0, NumPy 2.5.5, plyfile 1.1.5 |
| Person 5 experiment record | Valid | `sgd3dgs-research validate-experiment` |
| Person 4 experiment record | Valid | `sgd3dgs-research validate-experiment` |
| Reference `scene.json` structure | Valid | App schema 0.1 validation without external file checks |
| PLY identity across reports | Consistent | Same SHA-256 and Gaussian count in both records |
| SAGA experiment record | Valid | `sgd3dgs-research validate-experiment` |
| SAGA scripts | Pass | Python compile plus Ruff lint and format checks |
| SAGA packed mask | Verified | 693,896 entries, 74,617 selected, recorded packed checksum |
| SAGA NumPy reconstruction | Verified | Boolean mask and uint16 object-ID hashes match the record |
| PR reviews | Complete | PRs #1/#2 approved; PR #8 has no blocking findings but cannot be self-approved; no contribution merged |

The ramen full-file check, Gaussian Grouping measurements, and exact SAGA
source-PLY alignment depend on large files that are not yet available from
shared storage. The committed SAGA packed mask is independently verified, but
its spatial relationship to the truck cannot be proven until the exact source
PLY is available. See [acceptance-checks.json](acceptance-checks.json).

## Current result

Gaussian Grouping reports a real method-native mask selecting 63,202 Gaussians
(4.99%) with 93.5% mean IoU over three annotated views. It is a useful
reproducible fallback, not yet a supported app artifact. The same report finds
3,953 occupied spatial components, with 87.65% of selected Gaussians in the
largest component. The mask therefore needs inspection before object movement;
strong rendered overlap does not prove a spatially clean object.

SAGA reports a truck mask selecting 74,617 of 693,896 Gaussians (10.75%) from
13 positive clicks in four views. Selection/export took 4.48 seconds with
626 MiB peak PyTorch allocation. Its compressed mask, exact reconstructed-array
hashes, environment and three held-out render sets are committed. The source
PLY remains external, and the coordinator's visual review is still pending.

The baseline decision remains deferred because SAGA used a different scene and
object. Cross-scene percentages, component counts and image quality are not a
matched comparison. Missing values remain explicit in
[comparison.yaml](comparison.yaml).

## Mask-inspection tool decision

No additional inspection tool is added in this branch.

PRs #1 and #8 already contain:

- selected count, fraction, bounds and component measurements;
- three-view IoU, precision and recall;
- `prepare_mask.py`, which creates a black/white visualization PLY;
- a documented SplatTransform camera track and rendering procedure;
- SAGA's checksum-checked `unpack_mask.py` and committed packed mask;
- committed SAGA held-out render evidence.

A second utility would duplicate these functions and still could not display or
verify the Gaussian Grouping result without its external PLY and mask.
Reconsider a method-neutral command only after that mask is published and
duplicated inspection steps become a demonstrated maintenance problem.

## Week 1 completion assessment

| Plan item | Status |
|---|---|
| Fix one reference scene and target object | Accepted: ramen / yellow bowl |
| Bind research output to an exact PLY | Complete in repository metadata |
| Produce one real per-Gaussian mask | Reported complete; artifact publication pending |
| Record Gaussian Grouping environment, runtime and licensing | Complete |
| Measure visible and spatial failure modes | Complete for Gaussian Grouping |
| Reproduce SAGA on a public fallback | Complete on the truck scene |
| Verify a committed SAGA mask | Complete except source-Ply alignment |
| Produce a matched second-method result | Pending; current scenes differ |
| Convert to canonical `object_id.npy` | Pending |
| Validate a complete package with real files | Pending shared artifacts |
| Select and move the object in the app | Pending |
| Choose the supported segmentation baseline | Deferred |

## Tracked follow-up work

Research:

- [#3 Publish the ramen reference and Week 1 outputs on Hugging Face](https://github.com/sapankowski/sgd3dgs-research/issues/3)
- [#4 Convert the bowl mask to canonical `object_id.npy`](https://github.com/sapankowski/sgd3dgs-research/issues/4)
- [#5 Report conservative cleanup candidates](https://github.com/sapankowski/sgd3dgs-research/issues/5)
- [#6 Complete the matched segmentation comparison](https://github.com/sapankowski/sgd3dgs-research/issues/6)

App:

- [#1 Validate Gaussian count against the PLY header](https://github.com/sapankowski/sgd3dgs-app/issues/1)
- [#2 Verify PLY ordering and extra-property preservation](https://github.com/sapankowski/sgd3dgs-app/issues/2)
- [#3 Load labels and select the yellow bowl](https://github.com/sapankowski/sgd3dgs-app/issues/3)

## Artifact storage design

The two-scene Hugging Face layout, required checksums, publication rules and
files still needed from contributors are in
[huggingface-artifacts.md](huggingface-artifacts.md).
