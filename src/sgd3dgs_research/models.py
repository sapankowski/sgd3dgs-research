"""Versioned, method-neutral experiment records."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def validate_sha256(value: str) -> str:
    normalized = value.lower()
    if len(normalized) != 64 or any(char not in "0123456789abcdef" for char in normalized):
        raise ValueError("SHA-256 must contain exactly 64 hexadecimal characters")
    return normalized


class SceneInput(StrictModel):
    id: str = Field(min_length=1)
    manifest: str = Field(min_length=1)
    source_sha256: str

    @field_validator("source_sha256")
    @classmethod
    def source_checksum_is_valid(cls, value: str) -> str:
        return validate_sha256(value)


class MethodRecord(StrictModel):
    name: str = Field(min_length=1)
    repository: str = Field(min_length=1)
    commit: str = Field(pattern=r"^[0-9a-fA-F]{40}$")
    code_license: str = Field(min_length=1)
    weights: str | None = None
    weights_license: str | None = None


class EnvironmentRecord(StrictModel):
    operating_system: str = Field(min_length=1)
    gpu: str = Field(min_length=1)
    container_or_lock: str = Field(min_length=1)


class MetricsPlan(StrictModel):
    planned: list[str] = Field(min_length=1)


class ArtifactPlan(StrictModel):
    output_directory: str = Field(min_length=1)


class ExperimentRecord(StrictModel):
    schema_version: Literal[1]
    experiment_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    title: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    reviewer: str = Field(min_length=1)
    status: Literal["planned", "running", "completed", "failed", "stopped"]
    time_budget_hours: float = Field(gt=0, le=8)
    decision: str = Field(min_length=10)
    hypothesis: str = Field(min_length=20)
    scene: SceneInput
    method: MethodRecord
    environment: EnvironmentRecord
    command: str = Field(min_length=1)
    metrics: MetricsPlan
    artifacts: ArtifactPlan
    stopping_condition: str = Field(min_length=10)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def owner_and_reviewer_are_distinct(self) -> ExperimentRecord:
        if self.owner == self.reviewer:
            raise ValueError("owner and reviewer must be different people")
        return self
