# Contributing to SGD3DGS Research

## Scope

This repository accepts method reproduction, isolated environments, owned
adapters, experiment records, metrics, data cards, and completion research.
Editor UI, picking, transforms, app persistence, and schema authority belong in
`sgd3dgs-app`.

## Weekly rhythm

Work runs Wednesday–Tuesday with one 5–8 hour outcome per person. There is no
daily stand-up. Tuesday evidence should answer a decision, not merely list time
spent.

## Branches and PRs

- Use `exp/saga-chair`, `adapter/gaussian-grouping`, or `docs/gpu-setup`.
- One experiment/question per PR.
- Separate environment recipes from scientific conclusions.
- Link the app issue only when an artifact is ready for integration.
- Include source checksum, method commit, commands, hardware, runtime, and
  license effects.
- Keep large artifacts on shared storage.

Before review:

```bash
make verify
```

## Experiment outcomes

Every reviewed experiment ends as adopt, repeat with one specified change,
reject with evidence, or defer for a named prerequisite. Failed setup is useful
when its time box and logs are preserved.

## Environment promotion

Do not commit a speculative Dockerfile that has never completed a smoke test.
Promoted recipes pin base image, upstream/nested commits, compiler/CUDA stack,
and external weight identifiers without embedding weights.

## Cross-repository changes

The app owns schema changes. Open an app issue/ADR first, merge the new contract
and migration tests there, then update adapters here in a linked PR.
