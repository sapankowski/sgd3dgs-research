# Current integration readiness

This checklist records present facts. It is not an implementation handoff.

## Available in GitHub

- [x] Exact reference-scene and target names
- [x] Source archive provenance and reported checksums
- [x] Source PLY checksum and Gaussian count in two independent records
- [x] Schema 0.1 manifest without labels or objects
- [x] Gaussian Grouping CPU exporter
- [x] Exporter synthetic tests
- [x] Reported mask counts, spatial statistics and three-view metrics
- [x] Visualization preparation and camera-track procedure
- [x] Dependency and licensing notes
- [x] SAGA fallback experiment record and exact environment
- [x] SAGA compressed per-Gaussian mask
- [x] SAGA selection receipt, clicks, hashes and spatial statistics
- [x] SAGA three-view render files and comparison sheet
- [x] Scripts for SAGA training adaptations, selection and mask unpacking

## Reconstructed locally but intentionally ignored by Git

- [x] SAGA Boolean `mask.npy` — 693,896 entries, 74,617 selected
- [x] SAGA uint16 `object_id.npy` — values 0 and 1
- [x] Local verification receipt with matching NumPy hashes

These files are under
`data/scenes/tandt-truck-windows-7000/runs/saga/person3-week1/`.

## Not yet available through shared storage

- [ ] Extracted reference PLY
- [ ] Matching classifier checkpoint
- [ ] `native_id.npy`
- [ ] `confidence.npy`
- [ ] Boolean `mask.npy`
- [ ] Export `report.json` and logs
- [ ] Source, mask and overlay renders
- [ ] Artifact checksum inventory
- [ ] Exact SAGA truck source PLY
- [ ] SAGA feature PLY and `scale_gate.pt`
- [ ] SAGA training and feature checkpoints/logs

## Not yet implemented or demonstrated

- [ ] Canonical `uint16[N] object_id.npy`
- [ ] Manifest label entry and yellow-bowl object record
- [ ] Complete package validation against real files
- [ ] App label import
- [ ] Whole-object selection in the editor
- [ ] Translation, rotation and undo of the masked bowl
- [ ] Matched second-method comparison
- [ ] Supported segmentation-baseline decision
- [ ] SAGA mask alignment verified against its exact source PLY
- [ ] Coordinator visual inspection of SAGA comparison and held-out renders

The next claim that can be independently strengthened is artifact availability:
publish the immutable reference and run outputs with checksums, obtain the exact
SAGA source PLY, and rerun the pending checks in `acceptance-checks.json`.
