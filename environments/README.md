# Environment strategy

There are three environment classes:

1. **Base research environment** — Python 3.12, Pydantic, CLI, lint, and tests.
   Created by `make sync`; never gains CUDA frameworks.
2. **Legacy baselines** — one isolated Conda/container environment per pinned
   Gaussian Grouping or SAGA snapshot. They may not share an environment.
3. **Modern experiments** — a separately pinned gsplat/PyTorch/CUDA environment
   introduced only when the first clean implementation begins.

An environment is promoted into a documented recipe only after it runs a smoke
test on the shared worker. Record OS, GPU, driver, CUDA toolkit/runtime, compiler,
Python, framework versions, nested repository commits, weights, and the exact
smoke command.

Do not commit environment exports containing personal paths or credentials. Do
not bake model weights into images.
