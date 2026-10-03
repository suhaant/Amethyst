"""Where sensor readings come from.

To plug in real data, either:
  * drop a JSON file matching SensorReading and run with `--reading path.json`, or
  * write a class with `get_reading(patient_id) -> SensorReading` and register it
    in `get_data_source()`.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Protocol

from .schemas import SensorReading


class DataSource(Protocol):
    def get_reading(self, patient_id: str) -> SensorReading: ...


# DUMMY DATA: rough ranges chosen to look plausible, not clinically validated.
# Each value is (low, high) for a uniform draw.
SCENARIOS: dict[str, dict[str, tuple[float, float]]] = {
    "healthy": {
        "glycemic_variability_cv_pct": (15, 24),
        "wound_skin_temp_c": (32.8, 34.0),
        "heart_rate_bpm": (62, 85),
        "ph": (5.0, 6.3),
        "moisture_pct": (40, 58),
    },
    "early_infection": {
        "glycemic_variability_cv_pct": (26, 34),
        "wound_skin_temp_c": (34.6, 35.6),
        "heart_rate_bpm": (85, 98),
        "ph": (6.8, 7.4),
        "moisture_pct": (60, 72),
    },
    "infected": {
        "glycemic_variability_cv_pct": (35, 45),
        "wound_skin_temp_c": (35.8, 37.2),
        "heart_rate_bpm": (98, 118),
        "ph": (7.5, 8.6),
        "moisture_pct": (74, 90),
    },
    # Mixed/implausible signals, to exercise the agent's data-quality checks.
    "noisy_sensor": {
        "glycemic_variability_cv_pct": (18, 22),
        "wound_skin_temp_c": (41.0, 44.0),
        "heart_rate_bpm": (70, 80),
        "ph": (5.2, 5.8),
        "moisture_pct": (2, 6),
    },
}


class DummyDataSource:
    def __init__(self, scenario: str = "infected", seed: int | None = None):
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario {scenario!r}; choose from {list(SCENARIOS)}")
        self.scenario = scenario
        self.rng = random.Random(seed)

    def get_reading(self, patient_id: str) -> SensorReading:
        ranges = SCENARIOS[self.scenario]
        values = {k: round(self.rng.uniform(lo, hi), 2) for k, (lo, hi) in ranges.items()}
        values["reference_skin_temp_c"] = round(self.rng.uniform(32.5, 33.5), 2)
        return SensorReading(patient_id=patient_id, **values)


class JsonFileDataSource:
    """Reads a single SensorReading from a JSON file."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def get_reading(self, patient_id: str) -> SensorReading:
        data = json.loads(self.path.read_text())
        data.setdefault("patient_id", patient_id)
        return SensorReading(**data)


def get_data_source(
    reading_path: str | None = None, scenario: str = "infected", seed: int | None = None
) -> DataSource:
    if reading_path:
        return JsonFileDataSource(reading_path)
    return DummyDataSource(scenario=scenario, seed=seed)
