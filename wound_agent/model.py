"""Infection model adapter.

Anything with `predict_proba(reading) -> float` in [0, 1] works. Swap the stub for
the real model by setting INFECTION_MODEL_PATH (joblib/sklearn) or by adding a new
class and returning it from `load_model()`.
"""

from __future__ import annotations

import math
import os
from typing import Protocol

from .schemas import InfectionPrediction, SensorReading

# PLACEHOLDER: decision threshold; set from the real model's validation results.
INFECTION_THRESHOLD = 0.5

# Order the real model expects its features in. Update to match training.
FEATURE_ORDER = [
    "glycemic_variability_cv_pct",
    "wound_skin_temp_c",
    "heart_rate_bpm",
    "ph",
    "moisture_pct",
]


class InfectionModel(Protocol):
    name: str
    is_placeholder: bool

    def predict_proba(self, reading: SensorReading) -> float: ...


class StubModel:
    """Hand-tuned logistic score standing in for the trained model. NOT a real model."""

    name = "stub-heuristic-v0"
    is_placeholder = True

    def predict_proba(self, reading: SensorReading) -> float:
        z = (
            0.08 * (reading.glycemic_variability_cv_pct - 28)
            + 0.9 * (reading.wound_skin_temp_c - 35.0)
            + 0.05 * (reading.heart_rate_bpm - 90)
            + 1.6 * (reading.ph - 7.0)
            + 0.06 * (reading.moisture_pct - 65)
        )
        return 1.0 / (1.0 + math.exp(-z))


class JoblibModel:
    """Loads a scikit-learn style classifier saved with joblib."""

    def __init__(self, path: str):
        import joblib  # only needed once a real model exists

        self.name = os.path.basename(path)
        self.is_placeholder = False
        self._model = joblib.load(path)

    def predict_proba(self, reading: SensorReading) -> float:
        row = [[getattr(reading, f) for f in FEATURE_ORDER]]
        return float(self._model.predict_proba(row)[0][1])


def load_model() -> InfectionModel:
    path = os.environ.get("INFECTION_MODEL_PATH")
    return JoblibModel(path) if path else StubModel()


def predict(model: InfectionModel, reading: SensorReading) -> InfectionPrediction:
    p = min(max(model.predict_proba(reading), 0.0), 1.0)
    return InfectionPrediction(
        probability=round(p, 4),
        infection_detected=p >= INFECTION_THRESHOLD,
        threshold=INFECTION_THRESHOLD,
        model_name=model.name,
    )
