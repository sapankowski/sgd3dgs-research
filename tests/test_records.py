from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from sgd3dgs_research.cli import app
from sgd3dgs_research.models import ExperimentRecord
from sgd3dgs_research.records import load_experiment

REPOSITORY_ROOT = Path(__file__).parents[1]
RUNNER = CliRunner()


def test_example_experiment_is_valid() -> None:
    record = load_experiment(REPOSITORY_ROOT / "examples/minimal-experiment.yaml")

    assert record.experiment_id == "fixture-saga-chair"
    assert record.method.name == "saga-v2"
    assert record.time_budget_hours == 6


def test_cli_validates_example_experiment() -> None:
    result = RUNNER.invoke(
        app,
        ["validate-experiment", str(REPOSITORY_ROOT / "examples/minimal-experiment.yaml")],
    )

    assert result.exit_code == 0
    assert "fixture-saga-chair" in result.stdout


def test_weekly_time_budget_is_bounded() -> None:
    record = load_experiment(REPOSITORY_ROOT / "examples/minimal-experiment.yaml")
    payload = record.model_dump()
    payload["time_budget_hours"] = 20

    with pytest.raises(ValidationError, match="less than or equal to 8"):
        ExperimentRecord.model_validate(payload)


def test_owner_and_reviewer_must_differ() -> None:
    record = load_experiment(REPOSITORY_ROOT / "examples/minimal-experiment.yaml")
    payload = record.model_dump()
    payload["reviewer"] = payload["owner"]

    with pytest.raises(ValidationError, match="owner and reviewer must be different"):
        ExperimentRecord.model_validate(payload)
