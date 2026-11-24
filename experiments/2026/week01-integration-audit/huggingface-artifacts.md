# Hugging Face artifact design

## Repository

Use one private Hugging Face dataset repository for the current project stage:

```text
<HF_OWNER>/sgd3dgs-artifacts
```

Code, experiment records and review history remain on GitHub. Hugging Face owns
large immutable inputs, method-native outputs, checkpoints, renders, logs and
validated app packages. Do not apply one repository-wide software license to
mixed third-party data; record origin and terms per artifact.

## Layout

```text
sgd3dgs-artifacts/
├── README.md
├── LICENSES.md
├── artifact-index.json
└── scenes/
    ├── lerf-mask-ramen/
    │   ├── source/
    │   │   ├── upstream-lock.yaml
    │   │   └── SHA256SUMS
    │   ├── reconstruction/
    │   │   ├── point_cloud.ply
    │   │   ├── classifier.pth
    │   │   ├── cfg_args
    │   │   └── SHA256SUMS
    │   ├── runs/gaussian-grouping/class-108-threshold-0.3/
    │   │   ├── native_id.npy
    │   │   ├── confidence.npy
    │   │   ├── mask.npy
    │   │   ├── report.json
    │   │   ├── metrics.json
    │   │   ├── logs/
    │   │   ├── renders/
    │   │   └── SHA256SUMS
    │   └── packages/0.1/
    │       ├── scene.json
    │       ├── object_id.npy
    │       ├── confidence.npy
    │       └── SHA256SUMS
    └── tandt-truck-windows-7000/
        ├── source/
        │   ├── upstream-lock.yaml
        │   └── SHA256SUMS
        ├── reconstruction/
        │   ├── scene_point_cloud.ply
        │   ├── cfg_args
        │   └── SHA256SUMS
        ├── features/
        │   ├── contrastive_feature_point_cloud.ply
        │   ├── scale_gate.pt
        │   └── SHA256SUMS
        ├── runs/saga/scale-0.5-threshold-0.8/
        │   ├── mask.bits.gz
        │   ├── mask.npy
        │   ├── object_id.npy
        │   ├── selection.json
        │   ├── environment.txt
        │   ├── logs/
        │   ├── renders/
        │   └── SHA256SUMS
        └── packages/0.1/
            ├── scene.json
            ├── object_id.npy
            └── SHA256SUMS
```

## Formats and integrity

- Keep Gaussian scenes as `.ply` and aligned arrays as uncompressed `.npy`.
- Retain `mask.bits.gz` as the compact, Git-friendly SAGA transfer artifact.
- Use JSON for receipts/metrics, YAML for provenance/configuration, text for
  logs/checksums, and PNG/WebP for renders.
- Every nontrivial directory has `SHA256SUMS`.
- `artifact-index.json` records path, byte size, SHA-256, producing Git commit,
  source PLY SHA-256, Gaussian count, method, license and redistribution state.
- Keep method-native outputs separate from schema-versioned app packages.

## Files still needed from contributors

Gaussian Grouping contributor:

- native ID, confidence and Boolean mask arrays;
- export receipt/logs and render outputs;
- exact source PLY and classifier only when redistribution is confirmed.

SAGA contributor:

- exact `scene_point_cloud.ply` with SHA-256
  `f7ac2043fa1654fe381eff7e4956b5ca25a6d15a85241a8ccad30509aa489a48`;
- `contrastive_feature_point_cloud.ply` with SHA-256
  `5c60328e4e848104380b1271551798b82aa2e6b8194fc86db05a04262aab0cc6`;
- `scale_gate.pt`, model configuration and training logs;
- complete model directory layout needed to rerun recorded click selection.

The SAGA `mask.npy` and `object_id.npy` can be reconstructed from GitHub and
need not be treated as irreplaceable uploads, but storing them improves
convenience for app consumers.

## Publication rules

Start private. For upstream archives, images, checkpoints or derived renders
whose redistribution terms are unclear, store a pinned URL, revision, size and
checksum instead of copying the bytes. Public visibility requires a separate
license/provenance review. Uploading to private storage does not remove the need
to respect upstream terms.
