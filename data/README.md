# Research data workspace

Only this documentation is committed. Real contents of `data/scenes`,
`data/models`, `data/cache`, and `data/outputs` are ignored.

```text
data/
├── scenes/<scene-id>/
│   ├── source/                 # Immutable images/video and camera data
│   ├── reconstruction/         # Immutable source PLY/SOG
│   ├── runs/<method>/<run-id>/ # Method-native outputs
│   ├── packages/<version>/     # App-contract exports
│   └── data-card.md
├── models/<method>/            # External weights; record license/checksum
├── cache/                      # Re-creatable downloads/features
└── outputs/                    # Temporary comparisons/renders
```

Rules:

1. Never alter captures, camera solutions, or source Gaussians in place.
2. Every run has a unique folder and experiment record.
3. Every per-Gaussian output binds source checksum, Gaussian count, and order.
4. Method-native files stay separate from exported app packages.
5. Weights and datasets have separate provenance/license records.
6. Private captures remain on approved storage.
7. Add DVC/object storage only after a stable artifact justifies it.

The first reference scene should be public and shared read-only. Validate an
exported package with `scripts/validate_with_app.sh` before handing it to the app
team.
