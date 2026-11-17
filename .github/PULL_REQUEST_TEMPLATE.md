## Decision and outcome

Which issue/experiment does this address, and what decision or artifact results?

## Scope

- [ ] Research record or report
- [ ] Adapter or method-neutral utility
- [ ] Environment/container recipe
- [ ] Documentation/infrastructure

## Reproduction and evidence

List the exact commands, source scene checksum, upstream commit, environment,
hardware, runtime, metrics, and artifact location. Large artifacts must not be
attached to Git.

```text
make verify
```

## App contract

- Which `sgd3dgs-app` schema version is targeted?
- Does Gaussian ordering change or require an index map?
- Did `scripts/validate_with_app.sh` pass for any exported package?
- Is a linked app integration issue required?

## Licensing and provenance

- Are code, nested dependency, model-weight, and dataset terms recorded?
- Is redistribution of each output allowed?
- Is observed content distinguishable from generated content?

## Checklist

- [ ] The work stayed within its agreed time box or documents why it stopped.
- [ ] The experiment record validates.
- [ ] Commands and failure cases are documented.
- [ ] Reviewer is not the owner.
- [ ] No scene, mask, render, checkpoint, token, or private URL is committed.
- [ ] Documentation and `THIRD_PARTY.md` are updated when applicable.
