"""Experiment-record loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from sgd3dgs_research.models import ExperimentRecord


def load_experiment(path: Path) -> ExperimentRecord:
    with path.open(encoding="utf-8") as stream:
        payload: Any = yaml.safe_load(stream)
    return ExperimentRecord.model_validate(payload)
