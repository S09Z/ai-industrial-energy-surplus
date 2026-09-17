import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def root():
    return ROOT


@pytest.fixture
def config_dict():
    return tomllib.loads((ROOT / "configs/poc.toml").read_text())
