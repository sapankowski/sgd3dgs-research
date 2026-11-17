# SGD3DGS Research

**Reproducible segmentation, artifact analysis, and completion experiments for
object-level Gaussian Splatting editing.**

This repository produces versioned scene artifacts for the separate
[`sgd3dgs-app`](https://github.com/sapankowski/sgd3dgs-app) repository. It is the place
for legacy CUDA baselines, modern gsplat experiments, adapters, metrics, and
honest negative results. It is not an interactive application.

In the recommended local workspace, the app is available at
`../sgd3dgs-app`.

> Status: research scaffold. Gaussian Grouping and SAGA are pinned as external
> week-1 baselines. No baseline is yet designated “supported,” and no untested
> legacy container is presented as production-ready.

## Goals

- Reproduce and compare existing per-Gaussian segmentation approaches.
- Convert method-specific output into the app's canonical scene contract.
- Preserve source checksums, Gaussian ordering, method commits, and licenses.
- Measure leakage, coverage, click effort, runtime, and GPU requirements.
- Analyze background disocclusion and incomplete-object artifacts.
- Compare simple observed-data repair before one bounded generative experiment.
- Promote only evidence-backed workflows; keep failed experiments reproducible.

## Non-goals

- Building another interactive viewer or duplicating app UI code.
- Making one legacy research repository the project architecture.
- Committing scenes, masks, renders, weights, checkpoints, or generated assets.
- Treating a pleasing single view as evidence of 3D consistency.
- Hiding research-only or non-commercial license constraints.

## Two-repository project

```text
SGD3DGS/                         # Local workspace; not a Git repository
├── sgd3dgs-app/                 # Editor and authoritative schema
└── sgd3dgs-research/            # This repository
    ├── adapters/                # Method-output boundary and adapter notes
    ├── containers/legacy/       # Promoted legacy recipes only after reproduction
    ├── data/                    # Ignored raw/shared research data layout
    ├── environments/            # Environment ownership rules
    ├── experiments/             # Small configs, metrics, and reports
    ├── src/sgd3dgs_research/    # Method-neutral research utilities
    ├── tests/                   # Fast CPU-only tests
    ├── scripts/                 # Setup, pins, and app-contract validation
    └── docs/                    # Research workflow and landscape
```

The app owns scene schema `0.1`. Research outputs a derived package and validates
it with the app CLI. Schema changes begin in the app repository and are adopted
here only after review.

## Quick start

### Laptop/CPU environment

```bash
./scripts/check_system.sh
make sync
make check
make validate-sample
```

This environment validates experiment records and runs method-neutral tests. It
does not install PyTorch, CUDA, SAM, Gaussian Grouping, or SAGA.

### Fetch pinned baselines

```bash
make fetch-upstreams
```

This checks out Gaussian Grouping and SAGA into ignored `.external/`
directories. Each requires its own environment. Never install both—or either—
into the base research environment.

### Start an experiment

1. Copy `experiments/templates/` to `experiments/<year>/<experiment-id>/`.
2. State the decision, falsifiable hypothesis, owner/reviewer, and stopping
   condition before running.
3. Keep large outputs in `artifacts/` or shared storage.
4. Validate the record:

```bash
./scripts/uv.sh run sgd3dgs-research validate-experiment \
  experiments/<year>/<experiment-id>/experiment.yaml
```

5. Validate an exported app scene package:

```bash
./scripts/validate_with_app.sh /shared/scenes/<scene-id>/scene.json
```

## GPU expectations

The initial shared worker should run Ubuntu 22.04/24.04 with an NVIDIA GPU,
preferably 24 GB VRAM or more, 64 GB RAM, Docker/NVIDIA Container Toolkit, and
sufficient SSD space for source scenes and checkpoints. Use SSH forwarding;
never expose Jupyter or a model service publicly.

Legacy setup work is time-boxed. If installation consumes half of a person's
5–8 hour weekly allocation without a smoke test, preserve the log and switch to
a prepared example or fixture.

## Repository boundary

Research may hand the app only explicit artifacts:

- source scene checksum and Gaussian count;
- `object_id.npy` (`uint16[N]`);
- optional confidence and index-map arrays;
- object metadata and coordinate system;
- method/config/environment provenance;
- observed/generated distinction for completion variants.

It must not ask the app to import a training framework or execute arbitrary
method code.

## Team workflow

Work weeks run Wednesday–Tuesday. Each person has one 5–8 hour core outcome,
not daily assignments. Tuesday evening is for evidence, decisions, and next-week
scope. The authoritative cross-repository plan is in
[`sgd3dgs-app/docs/WORK_PLAN.md`](https://github.com/sapankowski/sgd3dgs-app/blob/main/docs/WORK_PLAN.md).

Use this issue tracker for method reproduction, adapters, experiment records,
metrics, data cards, and completion work. Link an app issue only when a validated
artifact needs product integration.

## Documentation

- [Research getting started](docs/GETTING_STARTED.md)
- [Research architecture](docs/ARCHITECTURE.md)
- [Experiment protocol](docs/EXPERIMENTS.md)
- [Open-source landscape](docs/RESEARCH_LANDSCAPE.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Third-party and model licensing](THIRD_PARTY.md)

## Initial milestone

> On one public reference scene, reproduce at least one real segmentation
> method, export a checksum-bound per-Gaussian object mask, validate it through
> the app contract, and document leakage, runtime, environment, and licensing.

Generative completion starts only after this artifact can be selected and moved
correctly in the app.
