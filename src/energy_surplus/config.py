"""Explicit units and strict, versioned configuration for the initial PoC."""

import tomllib
from datetime import date, time
from pathlib import Path
from typing import Annotated, Literal, Self
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Nonnegative = Annotated[float, Field(ge=0)]
Positive = Annotated[float, Field(gt=0)]
Name = Annotated[str, Field(min_length=1, pattern=r"\S")]


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False, frozen=True)


class Power(Schema):
    value: Nonnegative
    unit: Literal["MW"]


class TemperatureDelta(Schema):
    value: float
    unit: Literal["degC"]


class Dataset(Schema):
    source: Literal["bdg2"]
    meter: Literal["electricity"]
    customer_count: Annotated[int, Field(ge=20, le=50)]
    selection: Literal["development_only_single_site"]
    meter_energy_unit: Literal["kWh"]
    minimum_completeness: Annotated[float, Field(gt=0, le=1)]
    development_start: date
    calibration_start: date
    holdout_start: date
    holdout_end_exclusive: date

    @model_validator(mode="after")
    def ordered_splits(self) -> Self:
        if not (
            self.development_start
            < self.calibration_start
            < self.holdout_start
            < self.holdout_end_exclusive
        ):
            raise ValueError("dataset split boundaries must be strictly increasing")
        return self


class Forecast(Schema):
    delivery: Literal["next_local_day"]
    interval_minutes: Literal[60]
    issue_time_local: time
    timezone: Name
    baseline: Literal["seasonal_naive_weekly"]
    candidate: Literal["lightgbm"]
    quantiles: list[Annotated[float, Field(gt=0, lt=1)]]
    weather_mode: Literal["disabled"]
    feature_schema_version: Name

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError("timezone must be an IANA timezone") from exc
        return value

    @field_validator("issue_time_local")
    @classmethod
    def local_clock(cls, value: time) -> time:
        if value.tzinfo is not None or value.second or value.microsecond:
            raise ValueError("issue time must be a local clock time at minute precision")
        return value

    @field_validator("quantiles")
    @classmethod
    def ordered_quantiles(cls, value: list[float]) -> list[float]:
        if value != sorted(set(value)) or not {0.1, 0.5, 0.9}.issubset(value):
            raise ValueError("quantiles must be unique, increasing, and include 0.1, 0.5, 0.9")
        return value


class Supply(Schema):
    provenance: Literal["synthetic"]
    deliverable_generation: Power
    committed_grid_import: Power
    grid_import_limit: Power
    export_limit: Power
    transformer_limit: Power

    @model_validator(mode="after")
    def physical_limits(self) -> Self:
        if self.committed_grid_import.value > self.grid_import_limit.value:
            raise ValueError("committed grid import exceeds grid import limit")
        if (
            max(self.grid_import_limit.value, self.export_limit.value)
            > self.transformer_limit.value
        ):
            raise ValueError("grid import/export limit exceeds grid-interface transformer limit")
        return self


class Risk(Schema):
    demand_quantile: Annotated[float, Field(gt=0.5, lt=1)]
    operational_reserve: Power
    freshness_limit_hours: Positive
    policy_version: Name


class Commercial(Schema):
    policy_version: Name
    external_export: Literal["disabled"]
    internal_reallocation: Literal["unknown", "prohibited"]
    execution: Literal["disabled"]


class Scenario(Schema):
    name: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
    kind: Literal["normal", "shutdown", "production_surge", "supply_reduction", "hot_day"]
    factory_id: Name | None = None
    demand_multiplier: Nonnegative = 1.0
    supply_multiplier: Nonnegative = 1.0
    temperature_delta: TemperatureDelta | None = None
    enabled: bool = True

    @model_validator(mode="after")
    def coherent_scenario(self) -> Self:
        if self.kind in {"shutdown", "production_surge"}:
            if self.factory_id is None:
                raise ValueError("factory scenario requires factory_id")
        elif self.factory_id is not None:
            raise ValueError("factory_id is only valid for a factory scenario")
        if self.kind == "shutdown" and self.demand_multiplier != 0:
            raise ValueError("shutdown requires zero demand multiplier")
        if self.kind == "production_surge" and self.demand_multiplier <= 1:
            raise ValueError("production surge requires demand multiplier > 1")
        if self.kind not in {"shutdown", "production_surge"} and self.demand_multiplier != 1:
            raise ValueError("demand multiplier is only valid for a factory scenario")
        if self.kind == "supply_reduction":
            if not 0 <= self.supply_multiplier < 1:
                raise ValueError("supply reduction multiplier must be in [0, 1)")
        elif self.supply_multiplier != 1:
            raise ValueError("supply multiplier is only valid for supply reduction")
        if self.kind == "hot_day":
            if self.temperature_delta is None or self.temperature_delta.value <= 0:
                raise ValueError("hot day requires a positive temperature delta")
            if self.enabled:
                raise ValueError("hot day is disabled until an issue-time weather model exists")
        elif self.temperature_delta is not None:
            raise ValueError("temperature delta is only valid for hot day")
        return self


class ProjectConfig(Schema):
    schema_version: Literal["1"]
    dataset: Dataset
    forecast: Forecast
    supply: Supply
    risk: Risk
    commercial: Commercial
    scenarios: list[Scenario] = Field(min_length=1)

    @model_validator(mode="after")
    def consistent_policy(self) -> Self:
        if self.risk.demand_quantile not in self.forecast.quantiles:
            raise ValueError("risk demand quantile must be forecast by the model")
        if self.supply.export_limit.value != 0:
            raise ValueError("disabled external export requires a zero export limit")
        if len({s.name for s in self.scenarios}) != len(self.scenarios):
            raise ValueError("scenario names must be unique")
        return self


def load_config(path: Path) -> ProjectConfig:
    """Parse TOML without silently coercing strings into numeric settings."""
    return ProjectConfig.model_validate(tomllib.loads(path.read_text(encoding="utf-8")))
