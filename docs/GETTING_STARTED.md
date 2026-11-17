# Getting started with SGD3DGS Research

## 1. Expected time

Weeks run Wednesday–Tuesday. A normal task is 5–8 hours: one focused day or a
few evenings. Method installation is explicitly time-boxed; failure logs are a
valid result.

## 2. Workspace and prerequisites

Recommended sibling layout:

```text
SGD3DGS/
├── sgd3dgs-app/
└── sgd3dgs-research/
```

Laptop requirements: Git, uv, Python 3.12 (managed by uv), and enough disk for
metadata/tests. GPU execution additionally requires a shared Ubuntu NVIDIA
worker, Docker/NVIDIA Container Toolkit, and approved shared storage.

```bash
./scripts/check_system.sh
make sync
make check
make validate-sample
```

## 3. Read before GPU setup

- [Research architecture](ARCHITECTURE.md)
- [Experiment protocol](EXPERIMENTS.md)
- [Third-party inventory](../THIRD_PARTY.md)
- App [scene contract](https://github.com/sapankowski/sgd3dgs-app/blob/main/docs/DATA_FORMAT.md)

Understand Gaussian order, source checksums, 2D-to-3D mask evidence, and the
difference between captured and generated content.

## 4. Fetch—not install—baselines

```bash
make fetch-upstreams
```

This creates `.external/gaussian-grouping` and `.external/saga` at pinned
commits. Inspect upstream instructions and licenses before creating separate
environments. Do not install them into `venv/`.

For each method, stop setup after roughly half the weekly budget if there is no
smoke test. Record commands, logs, GPU/driver/compiler versions, and the exact
failure instead of continuing indefinitely.

## 5. Reference scene

Use one public scene and one clearly named object. Store immutable inputs on
shared storage and create a data card. Everyone uses the exact same source PLY
checksum; derived runs get separate directories.

Do not begin with a private phone capture. Public input makes upstream
comparison and collaboration safer.

## 6. Experiment record

Copy the templates and fill every field before running:

```bash
mkdir -p experiments/2026/my-experiment
cp experiments/templates/experiment.yaml experiments/2026/my-experiment/
cp experiments/templates/README.md experiments/2026/my-experiment/
```

Then validate:

```bash
./scripts/uv.sh run sgd3dgs-research validate-experiment \
  experiments/2026/my-experiment/experiment.yaml
```

Large outputs go in the ignored `artifacts/` folder or shared storage.

## 7. Export to the app

Method-native output is not automatically an app artifact. Use or build an
adapter satisfying `adapters/README.md`, then validate the complete scene
package through the sibling repository:

```bash
./scripts/validate_with_app.sh /shared/scenes/example/packages/0.1/scene.json
```

Never fix a mismatch by truncating arrays or editing the source PLY.

## 8. First pull request

Good first PRs are a reproducible setup report, corrected license note, one
experiment record, a tiny adapter fixture/test, or an onboarding correction.

```bash
make verify
```

Do not include method source, weights, scenes, masks, or renders.
