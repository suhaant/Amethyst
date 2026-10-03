"""Data shapes shared across the agent.

Sensor history travels as a pandas DataFrame with the columns in SENSOR_COLUMNS
(the same format predict.py takes); these models describe what goes in and out.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field

# Same order and units as predict.SENSORS.
SENSOR_COLUMNS = ["ph", "temp_c", "impedance_kohm", "blood_glucose_mgdl", "wound_glucose_mM"]


class SensorReading(BaseModel):
    """One 30-minute reading from the patch."""

    timestamp: Optional[datetime] = None
    hour: float = Field(description="Hours since the patch was applied.")
    ph: float = Field(description="Wound-bed pH.")
    temp_c: float = Field(description="Skin temperature around the wound, °C.")
    impedance_kohm: float = Field(description="Moisture sensor impedance at 1 kHz; lower = wetter.")
    blood_glucose_mgdl: float = Field(description="Blood glucose from CGM, mg/dL.")
    wound_glucose_mM: float = Field(description="Wound-fluid glucose, mM.")


class InfectionPrediction(BaseModel):
    p_infected: float = Field(ge=0.0, le=1.0, description="P(warning) + P(infection), latest reading.")
    predicted_label: str
    risk_score: float = Field(description="3 h smoothed risk, 0-100.")
    risk_score_6h_ago: Optional[float] = None
    risk_score_24h_ago: Optional[float] = None
    tier: str
    model_name: str


class TreatmentPlan(BaseModel):
    """Plan for the next 8-hour session, from risk_to_dose.session_plan."""

    tier: str
    risk_score: float
    skipped_reason: Optional[str] = None
    us_40khz_min: float = 0.0
    us_40khz_w_cm2: float = 0.0
    led_405nm_min: float = 0.0
    led_405nm_mw_cm2: float = 0.0
    led_dose_j_cm2: float = 0.0
    us_1p5mhz_min: float = 0.0
    order: str = "-"
    sessions_per_day: int = 3


class AgentNotes(BaseModel):
    """The only part of the result written by the LLM. All numbers come from tools."""

    summary: str = Field(description="2-3 sentence plain-language summary for a clinician.")
    trend: str = Field(description="How the sensor signals and risk have changed over the history.")
    reasoning: str = Field(description="Which signals drove the conclusion and why.")
    data_quality_flags: list[str] = Field(
        description=(
            "Concrete problems with specific sensor values (implausible, likely sensor fault, "
            "patch lifted, gaps). Empty list if the data looks sound."
        )
    )
    conflicting_signals: list[str] = Field(
        description="Signals that disagree with the model's prediction."
    )
    recommend_clinician_review: bool
    confidence: Literal["low", "medium", "high"]


class Assessment(BaseModel):
    wound_id: str
    n_readings: int
    history_hours: float
    latest_reading: SensorReading
    prediction: InfectionPrediction
    treatment: TreatmentPlan
    agent_notes: Optional[AgentNotes] = None
    caveats: list[str] = Field(
        default=[], description="Standing limitations, generated in code rather than by the agent."
    )
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
