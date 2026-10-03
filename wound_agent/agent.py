"""Claude Opus agent that assesses one sensor reading for wound infection.

The agent gathers data and reasons about it through tools; it never produces the
probability or the dose itself. Those come from the model and the planner, and the
final Assessment is assembled in Python from the tool outputs plus the agent's notes.
"""

from __future__ import annotations

import json
import os
import warnings

import anthropic
from anthropic import beta_tool

from .data_sources import DataSource
from .model import InfectionModel, predict
from .schemas import AgentNotes, Assessment, InfectionPrediction, SensorReading, TreatmentPlan
from .treatment import plan_treatment as compute_treatment_plan

MODEL = "claude-opus-5-5"

# In anthropic 0.x only `output_format` accepts a Pydantic class (it's merged into
# output_config.format under the hood), so silence its deprecation notice.
warnings.filterwarnings("ignore", message="The 'output_format' parameter is deprecated")

SYSTEM_PROMPT = """You are a clinical decision-support agent for a smart wound dressing.
The dressing reports one sensor reading: glycemic variability, skin temperature around the
wound (and optionally at a reference site), heart rate, wound pH, and moisture.

Work through these steps using your tools:
1. get_sensor_reading to fetch the patient's current reading.
2. predict_infection to get the trained model's infection probability.
3. plan_treatment to get the violet-light and ultrasound (20-40 kHz) plan for that probability.

Then write your assessment. Use the numbers exactly as the tools returned them; do not
compute your own probability or dose. Your job is to judge the evidence:
- In data_quality_flags, list only concrete problems with specific sensor values (implausible,
  likely sensor fault, missing). If the reading looks sound, leave it empty; don't add entries
  saying everything is fine.
- Note signals that disagree with the model (e.g. high probability but normal pH and temperature).
- Recommend clinician review when the probability is high, the data looks unreliable, or the
  signals conflict.
- Context: healthy wounds are usually acidic (pH ~4-6.5); infection tends to raise pH,
  local temperature, moisture/exudate, heart rate, and glycemic variability.
Standing caveats (a stub model, placeholder doses, assessment from a single reading) are
attached to the result automatically. Don't repeat them in any field."""


def make_client() -> anthropic.Anthropic:
    # Keys not scoped to a workspace must name one on every request.
    workspace_id = os.environ.get("ANTHROPIC_WORKSPACE_ID")
    headers = {"anthropic-workspace-id": workspace_id} if workspace_id else None
    return anthropic.Anthropic(default_headers=headers)


class AgentRefusedError(RuntimeError):
    pass


def run_assessment(
    patient_id: str,
    data_source: DataSource,
    model: InfectionModel,
    client: anthropic.Anthropic | None = None,
    verbose: bool = False,
) -> Assessment:
    client = client or make_client()
    state: dict[str, object] = {}

    @beta_tool
    def get_sensor_reading(patient_id: str) -> str:
        """Fetch the current wound sensor reading for a patient.

        Args:
            patient_id: The patient's identifier.
        """
        reading = data_source.get_reading(patient_id)
        state["reading"] = reading
        payload = reading.model_dump(mode="json")
        payload["temp_delta_c"] = reading.temp_delta_c
        return json.dumps(payload)

    @beta_tool
    def predict_infection() -> str:
        """Run the trained infection model on the fetched reading and return the
        probability of infection. Call after get_sensor_reading."""
        reading = state.get("reading")
        if not isinstance(reading, SensorReading):
            raise ValueError("No reading yet; call get_sensor_reading first.")
        prediction = predict(model, reading)
        state["prediction"] = prediction
        return prediction.model_dump_json()

    @beta_tool
    def plan_treatment() -> str:
        """Compute the violet-light exposure time and 20-40 kHz ultrasound plan from the
        model's infection probability. Call after predict_infection."""
        prediction = state.get("prediction")
        if not isinstance(prediction, InfectionPrediction):
            raise ValueError("No prediction yet; call predict_infection first.")
        plan = compute_treatment_plan(prediction)
        state["treatment"] = plan
        return plan.model_dump_json()

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        output_format=AgentNotes,
        tools=[get_sensor_reading, predict_infection, plan_treatment],
        messages=[{"role": "user", "content": f"Assess patient {patient_id}."}],
        # On a safety-classifier refusal, the API retries on a fallback model automatically.
        betas=["server-side-fallback-2026-07-01"],
        extra_body={"fallbacks": "default"},
    )

    final = None
    for message in runner:
        final = message
        if verbose:
            for block in message.content:
                if block.type == "tool_use":
                    print(f"[agent] -> {block.name}({block.input})")

    if final is None or final.stop_reason == "refusal":
        details = getattr(final, "stop_details", None)
        raise AgentRefusedError(f"Agent declined the request: {details}")

    missing = [k for k in ("reading", "prediction", "treatment") if k not in state]
    if missing:
        raise RuntimeError(f"Agent finished without calling tools for: {missing}")

    reading = state["reading"]
    prediction = state["prediction"]
    treatment = state["treatment"]
    assert isinstance(reading, SensorReading)
    assert isinstance(prediction, InfectionPrediction)
    assert isinstance(treatment, TreatmentPlan)

    return Assessment(
        reading=reading,
        prediction=prediction,
        treatment=treatment,
        agent_notes=final.parsed_output,
        caveats=build_caveats(model, treatment),
    )


def run_offline(patient_id: str, data_source: DataSource, model: InfectionModel) -> Assessment:
    """Same pipeline without the LLM; useful for tests and when no API key is set."""
    reading = data_source.get_reading(patient_id)
    prediction = predict(model, reading)
    treatment = compute_treatment_plan(prediction)
    return Assessment(
        reading=reading,
        prediction=prediction,
        treatment=treatment,
        caveats=build_caveats(model, treatment),
    )


def build_caveats(model: InfectionModel, treatment: TreatmentPlan) -> list[str]:
    caveats = []
    if getattr(model, "is_placeholder", False):
        caveats.append(f"Infection probability comes from {model.name}, a placeholder, not the trained model.")
    if treatment.placeholder_values:
        caveats.append("Treatment doses are placeholders pending clinical sign-off.")
    caveats.append("Based on a single reading; no trend is available.")
    return caveats

