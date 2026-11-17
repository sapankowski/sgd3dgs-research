# Experiments

Research results belong here as small, reviewable records. Large artifacts live
under the ignored `artifacts/` or on shared storage.

Each experiment directory contains:

```text
experiments/<year>/<experiment-id>/
├── experiment.yaml
├── README.md
├── metrics.json          # when quantitative results exist
└── artifacts/            # ignored; may be a symlink to shared storage
```

Copy `experiments/templates/experiment.yaml` and
`experiments/templates/README.md` when starting a run. The report must state a
decision, hypothesis, time budget, and stopping condition before execution. See
`docs/EXPERIMENTS.md` and validate it with:

```bash
./scripts/uv.sh run sgd3dgs-research validate-experiment \
  experiments/<year>/<experiment-id>/experiment.yaml
```
