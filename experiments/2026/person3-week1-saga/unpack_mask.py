"""Verify the source PLY and unpack the committed mask into canonical object IDs."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
from plyfile import PlyData


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    options = parser.parse_args()
    record = json.loads((options.results / "selection.json").read_text())
    if digest(options.source) != record["source_sha256"]:
        raise ValueError("Source PLY SHA-256 mismatch")
    if len(PlyData.read(options.source)["vertex"]) != record["vertices"]:
        raise ValueError("Source PLY vertex count mismatch")
    packed = options.results / "mask.bits.gz"
    if digest(packed) != record["packed_mask_sha256"]:
        raise ValueError("Packed mask SHA-256 mismatch")
    data = np.frombuffer(gzip.decompress(packed.read_bytes()), dtype=np.uint8)
    if data.size != (record["vertices"] + 7) // 8:
        raise ValueError("Invalid mask byte count")
    mask = np.unpackbits(data, bitorder="little", count=record["vertices"])
    if int(mask.sum()) != record["selected"]:
        raise ValueError("Selected count mismatch")
    options.out.mkdir(parents=True, exist_ok=True)
    mask_path = options.out / "mask.npy"
    ids_path = options.out / "object_id.npy"
    if mask_path.exists() or ids_path.exists():
        raise FileExistsError("Choose an output directory without existing mask files")
    np.save(mask_path, mask.astype(np.bool_), allow_pickle=False)
    np.save(ids_path, mask.astype(np.uint16), allow_pickle=False)
    if digest(mask_path) != record["mask_sha256"] or digest(ids_path) != record["object_id_sha256"]:
        raise ValueError("Unpacked mask SHA-256 mismatch")


if __name__ == "__main__":
    main()
