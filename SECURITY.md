# Security policy

This repository handles GPU code, model weights, third-party repositories, and
potentially sensitive captures. Run it only on trusted laptops/workers.

- Do not expose Jupyter, tensorboard, development APIs, or model services to the
  public internet. Use SSH forwarding.
- Do not commit tokens, private URLs, captured interiors, faces, license plates,
  source scenes, weights, or generated artifacts.
- Treat third-party setup scripts and checkpoints as untrusted until reviewed.
- Pin downloaded code and record weight sources/checksums.
- Use least-privilege storage access and separate personal captures from public
  benchmark data.

Report a suspected vulnerability privately through the repository owner's
GitHub profile. Replace this paragraph with a dedicated contact after publishing.
