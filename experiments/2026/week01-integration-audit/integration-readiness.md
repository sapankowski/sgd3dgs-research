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

## Not yet available through shared storage

- [ ] Extracted reference PLY
- [ ] Matching classifier checkpoint
- [ ] `native_id.npy`
- [ ] `confidence.npy`
- [ ] Boolean `mask.npy`
- [ ] Export `report.json` and logs
- [ ] Source, mask and overlay renders
- [ ] Artifact checksum inventory

## Not yet implemented or demonstrated

- [ ] Canonical `uint16[N] object_id.npy`
- [ ] Manifest label entry and yellow-bowl object record
- [ ] Complete package validation against real files
- [ ] App label import
- [ ] Whole-object selection in the editor
- [ ] Translation, rotation and undo of the masked bowl
- [ ] Matched second-method comparison
- [ ] Supported segmentation-baseline decision

The next claim that can be independently strengthened is artifact availability:
publish the immutable reference and run outputs with checksums, then rerun the
pending checks listed in `acceptance-checks.json`.
