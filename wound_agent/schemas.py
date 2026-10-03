"""Data shapes shared across the pipeline.

SensorReading is the contract for real data: any source (device, CSV, database)
only has to produce one of these.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    """One snapshot of wound-site and vital-sign sensors."""

    patient_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    glycemic_variability_cv_pct: float = Field(
        description="Coefficient of variation of blood glucose, %."
    )
    wound_skin_temp_c: float = Field(description="Skin temperature around the cut, °C.")
    reference_skin_temp_c: Optional[float] = Field(
        default=None,
        description="Skin temperature at a healthy reference site, °C (optional).",
    )
    heart_rate_bpm: float
    ph: float = Field(description="Wound-bed pH.")
    moisture_pct: float = Field(description="Wound moisture, 0-100 sensor scale.")

    @property
    def temp_delta_c(self) -> Optional[float]:
        if self.reference_skin_temp_c is None:
            return None
        return round(self.wound_skin_temp_c - self.reference_skin_temp_c, 2)


class InfectionPrediction(BaseModel):
    probability: float = Field(ge=0.0, le=1.0)
    infection_detected: bool
    threshold: float
    model_name: str


class TreatmentPlan(BaseModel):
    treat: bool
    band: str
    violet_light_minutes: float
    ultrasound_frequency_khz: Optional[float]
    ultrasound_minutes: float
    sessions_per_day: int
    notes: list[str] = []
    placeholder_values: bool = True


class AgentNotes(BaseModel):
    """The only part of the result written by the LLM. All numbers come from tools."""

    summary: str = Field(description="2-3 sentence plain-language summary for a clinician.")
    reasoning: str = Field(description="Which signals drove the conclusion and why.")
    data_quality_flags: list[str] = Field(
        description=(
            "Concrete problems with specific sensor values (implausible, likely sensor fault, "
            "missing). Empty list if the reading looks sound."
        )
    )
    conflicting_signals: list[str] = Field(
        description="Signals that disagree with the model's prediction."
    )
    recommend_clinician_review: bool
    confidence: Literal["low", "medium", "high"]


class Assessment(BaseModel):
    reading: SensorReading
    prediction: InfectionPrediction
    treatment: TreatmentPlan
    agent_notes: Optional[AgentNotes] = None
    caveats: list[str] = Field(
        default=[], description="Standing limitations, generated in code rather than by the agent."
    )
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
