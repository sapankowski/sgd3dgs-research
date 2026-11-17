# Research adapters

Adapters convert a method's native output into the canonical contract owned by
`sgd3dgs-app`. They do not patch the app or redefine its schema.

Future adapters use this layout:

```text
adapters/<method>/
├── README.md        # Supported upstream commit and native assumptions
├── config/          # Small tracked conversion defaults
├── fixtures/        # Metadata-only or tiny synthetic fixtures
└── tests/           # Ordering, dtype, checksum, and failure tests
```

An adapter must:

- accept explicit input/output paths—no personal absolute paths;
- preserve Gaussian order or emit an old-to-new index map;
- output `uint16[N]` object IDs and optional `float32[N]` confidence;
- record source checksum/count and method/config provenance;
- reject mismatches rather than truncate or guess;
- never overwrite source Gaussians or a prior run;
- validate the completed `scene.json` with the sibling app CLI.

Method-specific runtime code stays in `.external/<method>` or its isolated
container. Only conversion logic that the team owns belongs here.
