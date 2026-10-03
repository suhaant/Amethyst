"""Deterministic treatment planner: infection probability -> violet light + ultrasound.

Every number in this file is a PLACEHOLDER. Replace them with values from your team's
clinical/literature source before using this on anyone.
"""

from __future__ import annotations

from .schemas import InfectionPrediction, TreatmentPlan

# Hard device limits. Plans are always clamped to these.
ULTRASOUND_MIN_KHZ = 20.0
ULTRASOUND_MAX_KHZ = 40.0
MAX_VIOLET_LIGHT_MINUTES = 30.0  # PLACEHOLDER
MAX_ULTRASOUND_MINUTES = 15.0  # PLACEHOLDER

# PLACEHOLDER bands, checked top-down: (min_probability, band, light_min, khz, us_min, sessions/day)
TREATMENT_BANDS = [
    (0.85, "high", 25.0, 40.0, 10.0, 3),
    (0.60, "moderate", 15.0, 35.0, 7.0, 2),
    (0.30, "low", 8.0, 30.0, 5.0, 1),
    (0.00, "none", 0.0, None, 0.0, 0),
]


def _clamp(value: float, lo: float, hi: float) -> float:
    return min(max(value, lo), hi)


def plan_treatment(prediction: InfectionPrediction) -> TreatmentPlan:
    p = prediction.probability
    for min_p, band, light, khz, us_min, sessions in TREATMENT_BANDS:
        if p >= min_p:
            break

    notes = []
    if band == "none":
        notes.append("Probability below treatment threshold; continue monitoring.")
    if band == "high":
        notes.append("High infection probability; clinician review recommended.")

    return TreatmentPlan(
        treat=band != "none",
        band=band,
        violet_light_minutes=_clamp(light, 0.0, MAX_VIOLET_LIGHT_MINUTES),
        ultrasound_frequency_khz=(
            None if khz is None else _clamp(khz, ULTRASOUND_MIN_KHZ, ULTRASOUND_MAX_KHZ)
        ),
        ultrasound_minutes=_clamp(us_min, 0.0, MAX_ULTRASOUND_MINUTES),
        sessions_per_day=sessions,
        notes=notes,
    )
