# Research architecture

## 1. Purpose

This repository turns external methods into reproducible evidence and
versioned artifacts. It is deliberately not a server, viewer, or second product.

```text
immutable scene + cameras
          │
          ├── isolated method environment
          │       └── native output
          │
          ├── owned adapter + integrity checks
          │       └── canonical scene package
          │
          ├── metrics + multi-view evidence
          │
          └── app validator ──▶ sgd3dgs-app import
```

## 2. Isolation boundary

External research repositories are executable pipelines under `.external/`, not
libraries imported into the base package. Each method has its own environment,
because old PyTorch/CUDA extensions and nested rasterizers conflict.

The base `sgd3dgs_research` package remains CPU-only and owns experiment records,
validation, and future method-neutral metrics. It must stay installable on a
normal contributor laptop.

## 3. Data layers

1. **Source:** immutable images, poses, and Gaussians.
2. **Native run:** exact method output, configuration, log, environment, and
   upstream commit.
3. **Canonical package:** adapter output satisfying an app schema version.
4. **Evaluation:** metrics, view grids, failure annotations, and decision.

Never overwrite a layer. Every derived artifact points backward by checksum.

## 4. Adapter boundary

An adapter is the only method-specific code allowed to interpret a native mask
or feature representation. It emits explicit dtype/shape/order, provenance, and
failure messages. The app schema is authoritative; a research adapter cannot
add an undocumented field and assume the editor will understand it.

## 5. Baseline sequence

1. Reproduce SAGA and Gaussian Grouping on one prepared example.
2. Select the simplest usable per-Gaussian mask path.
3. Build one tested canonical adapter.
4. Measure/correct dominant segmentation failures.
5. Only then consider a clean gsplat implementation.
6. After app transforms are correct, compare observed-data repair before one
   bounded generative experiment.

This prevents environment work, segmentation research, and generation from all
expanding simultaneously.

## 6. Completion rules

Background disocclusion, incomplete object geometry, and lighting inconsistency
are separate problems. Prefer real observations from other views. Generated
content remains marked, removable, and evaluated against a simple baseline.

## 7. Promotion rule

An experiment becomes a supported workflow only when it has:

- exact source/method/environment identifiers;
- a clean smoke test;
- an owned adapter with integrity tests;
- representative success and failure evidence;
- reviewed code and weight licenses;
- a bounded runtime/hardware statement;
- a linked app integration issue.

Otherwise it remains an experiment record, including negative results.
