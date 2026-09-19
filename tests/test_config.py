import pytest
from pydantic import ValidationError

from energy_surplus.config import ProjectConfig, load_config


def test_sample_is_conservative(root):
    config = load_config(root / "configs/poc.toml")
    assert config.supply.export_limit.value == 0
    assert config.commercial.execution == "disabled"
    assert config.commercial.internal_reallocation == "unknown"
    assert not next(s for s in config.scenarios if s.kind == "hot_day").enabled


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("supply", "operational_capacity"), 100, "Extra inputs"),
        (("supply", "grid_import_limit", "unit"), "kW", "MW"),
        (("supply", "grid_import_limit", "value"), -1, "greater than or equal"),
        (("supply", "grid_import_limit", "value"), float("nan"), "finite"),
        (("supply", "grid_import_limit", "value"), float("inf"), "finite"),
        (("supply", "grid_import_limit", "value"), "80", "valid number"),
        (("supply", "committed_grid_import", "value"), 90, "committed grid import"),
        (("supply", "grid_import_limit", "value"), 101, "transformer"),
        (("supply", "export_limit", "value"), 1, "disabled external export"),
        (("commercial", "external_export"), "allowed", "disabled"),
        (("commercial", "execution"), "enabled", "disabled"),
        (("risk", "demand_quantile"), 0.95, "must be forecast"),
        (("risk", "freshness_limit_hours"), 0, "greater than"),
        (("forecast", "quantiles"), [0.9, 0.5, 0.1], "increasing"),
        (("forecast", "quantiles"), [0.1, 0.5, 0.9, 0.9], "unique"),
        (("forecast", "timezone"), "Not/A_Zone", "IANA"),
        (("dataset", "customer_count"), True, "valid integer"),
        (("dataset", "customer_count"), 19, "greater than or equal"),
    ],
)
def test_invalid_settings_rejected(config_dict, path, value, message):
    target = config_dict
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValidationError, match=message):
        ProjectConfig.model_validate(config_dict)


def test_units_cannot_be_omitted(config_dict):
    del config_dict["risk"]["operational_reserve"]["unit"]
    with pytest.raises(ValidationError, match="Field required"):
        ProjectConfig.model_validate(config_dict)


def test_overlapping_split_rejected(config_dict):
    config_dict["dataset"]["holdout_start"] = config_dict["dataset"]["calibration_start"]
    with pytest.raises(ValidationError, match="strictly increasing"):
        ProjectConfig.model_validate(config_dict)


@pytest.mark.parametrize(
    ("index", "field", "value", "message"),
    [
        (1, "factory_id", None, "requires factory_id"),
        (1, "demand_multiplier", 1.0, "zero demand"),
        (2, "demand_multiplier", 0.9, "multiplier > 1"),
        (3, "supply_multiplier", 1.1, "supply reduction multiplier"),
        (4, "enabled", True, "hot day is disabled"),
        (0, "demand_multiplier", 1.3, "only valid for a factory"),
        (1, "name", "normal", "names must be unique"),
    ],
)
def test_scenario_consistency(config_dict, index, field, value, message):
    config_dict["scenarios"][index][field] = value
    with pytest.raises(ValidationError, match=message):
        ProjectConfig.model_validate(config_dict)


def test_shortage_is_not_configuration_error(config_dict):
    # A high reserve may be infeasible; the later optimizer must expose the shortage.
    config_dict["risk"]["operational_reserve"]["value"] = 1000.0
    ProjectConfig.model_validate(config_dict)
