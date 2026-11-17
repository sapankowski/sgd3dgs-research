# Legacy research environments

Gaussian Grouping and SAGA depend on old Python, PyTorch, CUDA extensions, and
nested repositories. They must remain isolated from the lightweight research
environment and from `sgd3dgs-app`.

During week 1, the segmentation pair reproduces each upstream installation and
records the commands, GPU, compiler, runtime, and exact failure modes. Only the
environment that successfully reproduces a useful result is promoted into a
pinned Dockerfile here. This avoids shipping an untested container recipe that
looks official but does not build.

Promotion requirements:

- Builds from an exact base-image digest.
- Checks out an exact upstream commit.
- Records nested dependency commits.
- Runs a smoke test in CI or on the documented GPU worker.
- Includes license notes for source and model weights.
- Does not place downloaded weights inside the image.
