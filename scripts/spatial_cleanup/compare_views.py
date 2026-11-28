"""Compare three matching occlusion-aware mask renders against LERF annotations."""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def scores(predicted, expected):
    intersection = np.count_nonzero(predicted & expected)
    union = np.count_nonzero(predicted | expected)
    return {
        "iou": intersection / union if union else 1.0,
        "precision": intersection / predicted.sum() if predicted.any() else 0.0,
        "recall": intersection / expected.sum() if expected.any() else 1.0,
    }


def overlay(scene, intensity, color):
    alpha = Image.fromarray((intensity.astype(float) * 0.65).astype(np.uint8))
    return Image.composite(Image.new("RGB", scene.size, color), scene, alpha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True, help="Week 1 render directory")
    parser.add_argument("--run", type=Path, required=True, help="Candidate report and new renders")
    parser.add_argument("--annotations", type=Path, required=True, help="LERF test_mask directory")
    args = parser.parse_args()
    report = json.loads((args.run / "report.json").read_text())
    summary = {
        k: v for k, v in report.items() if k not in ("components", "source_ply", "source_mask")
    }
    summary["views"] = []
    sheet = Image.new("RGB", (1600, 944), "#20242b")
    draw = ImageDraw.Draw(sheet)
    for col, title in enumerate(
        (
            "Before: original selection",
            "Proposed: candidates excluded",
            "Candidates only (red)",
            "LERF yellow-bowl annotation",
        )
    ):
        draw.text((col * 400 + 10, 12), title, fill="white")
    for view in range(3):
        scene = Image.open(args.before / f"scene.{view:04}.webp").convert("RGB")
        before = np.asarray(Image.open(args.before / f"mask.{view:04}.webp").convert("L"))
        after = np.asarray(Image.open(args.run / f"preview.{view:04}.webp").convert("L"))
        candidate = np.asarray(Image.open(args.run / f"candidates.{view:04}.webp").convert("L"))
        expected = (
            np.asarray(Image.open(args.annotations / str(view) / "yellow bowl.png").convert("L"))
            >= 128
        )
        summary["views"].append(
            {
                "view": f"test_{view}",
                "before": scores(before >= 128, expected),
                "preview": scores(after >= 128, expected),
                "changed_pixels": int(np.count_nonzero((before >= 128) != (after >= 128))),
                "candidate_pixels": int(np.count_nonzero(candidate >= 128)),
            }
        )
        pictures = [
            overlay(scene, before, (20, 225, 250)),
            overlay(scene, after, (20, 225, 250)),
            overlay(scene, candidate, (255, 60, 60)),
            overlay(scene, expected.astype(np.uint8) * 255, (20, 225, 250)),
        ]
        row = Image.new("RGB", (scene.width * 4, scene.height))
        for col, picture in enumerate(pictures):
            row.paste(picture, (scene.width * col, 0))
            sheet.paste(picture.resize((396, 293)), (col * 400 + 2, 35 + view * 303))
        row.save(args.run / f"comparison-{view}.png")
    sheet.save(args.run / "three-views.png")
    (args.run / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["views"], indent=2))


if __name__ == "__main__":
    main()
