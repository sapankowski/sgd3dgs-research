# Week 1 exporter validation

Validated on 2026-11-20 by the Person 5 implementation task.

## Question and result

Can the raw Gaussian Grouping identity classifier be exported in PLY vertex
order using the published checkpoint and a CPU environment?

The official ramen iteration 30000 checkpoint exported successfully. The source
contains 1,266,122 Gaussians and the classifier has 256 classes. The exporter
reported 2.965 seconds on CPU with OMP_NUM_THREADS=4 and MKL_NUM_THREADS=4.
This measures export after loading the Python process, including result-array writes.
It does not measure training or GPU inference performance.

Class 1 was selected as a mechanical mask-export check at threshold 0.3.
It selected 229,945 Gaussians (18.1614%). Its semantic identity has not been
confirmed against images. Segmentation quality, three-view inspection,
connected-component statistics and comparison against Person 3's SAGA run
remain pending.

## Inputs and provenance

- Published checkpoint [ramen.zip](https://huggingface.co/mqye/Gaussian-Grouping/blob/34cbf65561144792d7a1861b38274bd7be18c8bc/checkpoint/lerf_mask/ramen.zip).
- Source PLY SHA-256 `d2fee173a0ec2e98e72fa45483f816ccbec86ab66825d00dc8213220a2a5866a`.
- Classifier SHA-256 `523b9238cc45f443ec1d4c610aa2e759e402e0d7b71251d52e1c6cc88faedbbd`.
- Both files came from `ramen/point_cloud/iteration_30000/` in that archive.
- The reference code commit is `0ab60afed3385b717c985af1d30a20f7b0884c89`.
  The published checkpoint's actual training commit remains unverified.
- Checkpoint redistribution and dataset terms remain to be verified before sharing
  those assets. The PR contains the exporter, tests and text records.

## Reproduction

Use Python 3.12.3, PyTorch 2.6.0+cpu, NumPy 2.5.5 and plyfile 1.1.5.
The run used WSL2 Linux x86_64 on Intel Core Ultra 7 251HX. Substitute paths to the two extracted files
and choose a new result directory.

```bash
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 python scripts/gaussian_grouping/export_labels.py \
  --ply "$INPUT/point_cloud.ply" \
  --classifier "$INPUT/classifier.pth" \
  --select-id 1 --threshold 0.3 --output "$RESULT"
```

Inspect `report.json` for classification statistics and environment details.
Source and result arrays are held outside the repository in the XR data/results
directories.

## Checks

- Standalone exporter regression suite passed 3 result-correctness tests.
- Repository `make verify` passed Ruff, formatting, mypy, 4 existing tests,
  sample experiment validation and repository integrity checks.
- Exporter Ruff checks and formatting passed separately, since its PyTorch
  dependencies are installed in a dedicated environment.

The evidence supports using this exporter to inspect method-native outputs.
A canonical app package still requires reviewed native-ID mapping and source
identity validation. The next research run needs the team's scene/target,
a reviewer, a completed experiment record and visual evidence.


## Output identity

Checksums were calculated separately for the recorded files after export.

| File | SHA-256 |
| --- | --- |
| native_id.npy | d72fbb85e9f9b5704c06e23eb82d244acd4c57910fde6ed9f90b0d7058e9abdf |
| confidence.npy | 4b068b5512bc5259c424102f4030e641876d65bf45d7182239727cb5a3359a1d |
| mask.npy | 11576073c726a0d212ae663fcfe157ae4c68dc130d9c8f70b7b3f0a1f1062caa |

Artifacts are retained by Person 5 under the XR workspace at
`04_results/week01-person5/ramen-native-export-review-001/`.
The arrays match the previous implementation's outputs byte for byte.
Shared-storage placement and full Week 1 research evidence remain pending.
