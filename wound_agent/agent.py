"""Claude Opus agent that assesses a wound's sensor history for infection.

The agent gathers data and reasons about it through tools; it never produces the
risk score or the dose itself. Those come from Adam's XGBoost model and
risk_to_dose.py, and the final Assessment is assembled in Python from the tool
outputs plus the agent's notes.
"""

from __future__ import annotations

import json
import os
import warnings

import anthropic
import pandas as pd
from anthropic import beta_tool

from risk_to_dose import LIFTED_KOHM

from .data_sources import DataSource
from .model import RiskModel
from .schemas import (
    SENSOR_COLUMNS,
    AgentNotes,
    Assessment,
    InfectionPrediction,
    SensorReading,
    TreatmentPlan,
)

MODEL = "claude-opus-5-5"

# In anthropic 0.x only `output_format` accepts a Pydantic class (it's merged into
# output_config.format under the hood), so silence its deprecation notice.
warnings.filterwarnings("ignore", message="The 'output_format' parameter is deprecated")

SYSTEM_PROMPT = """You are a clinical decision-support agent for a smart wound patch.
The patch reports a reading every 30 minutes since it was applied: wound pH, skin
temperature around the wound, moisture-sensor impedance (kΩ), blood glucose from a CGM
(mg/dL), and wound-fluid glucose (mM).

Work through these steps using your tools:
1. get_sensor_history to fetch a summary of the wound's readings.
2. predict_infection to get the trained model's infection risk.
3. plan_treatment to get the next session's 405 nm LED and ultrasound plan.

Then write your assessment. Use the numbers exactly as the tools returned them; do not
compute your own risk or dose. Your job is to judge the evidence:
- Describe how the signals and the risk score have moved over time, against the
  patient's own day-1 baseline.
- In data_quality_flags, list only concrete problems with specific sensor values
  (physiologically implausible, likely sensor fault, patch lifted, gaps). If the data
  looks sound, leave it empty; don't add entries saying everything is fine. Brief dips
  from showers or dressing changes are normal and not worth flagging.
- Note signals that disagree with the model.
- Recommend clinician review when risk is in the treat or intensive tier, the data looks
  unreliable, or the signals conflict.

Context:
- Infection tends to raise wound pH (healthy healing wounds trend acidic, ~6.5 and
  falling; infected ~7.5) and local temperature (+1-2 °C), lower impedance (more
  exudate), lower wound-fluid glucose (bacteria consume it), and nudge blood glucose up.
- Not every infection shows every sign. pH fails to rise in a meaningful minority of
  infections (some organisms and necrotic tissue keep it acidic), and the temperature
  rise ranges from under 1 °C to over 2 °C. A normal pH or a small temperature rise on
  its own is not evidence against infection; judge the signals together.
- How well each sensor alone separated infected from clean wounds in the model's
  validation (AUC): impedance/moisture 0.95, temperature 0.93, pH 0.92, wound-fluid
  glucose 0.89, blood glucose 0.65. All patch sensors together: 0.98. Blood glucose is
  weak on its own and is easily moved by meals.
- Lower your confidence when the model's call rests on signals that look like
  artifacts or meal spikes, or when strong signals point the other way. Don't lower
  it just because one sign is missing.
- Impedance above 150 kΩ means the patch is off the skin; treatment is skipped then.
- Risk tiers: 0 monitor, 1 watch (enter at >=30), 2 treat (>=55), 3 intensive (>=80).
  Tiers have 10-point hysteresis: a tier is entered at its threshold but only left when
  the risk falls 10 points below it (e.g. watch holds until risk < 20). A risk score
  below the tier's entry threshold is therefore expected, not an error.
- The 405 nm LED dose scales with risk from 30 to 90, so it is zero below 30. Any
  session without LED gets 1.5 MHz healing ultrasound instead (monitor tier, and watch
  tier while risk is under 30). Treat and above add 40 kHz ultrasound before the LED.
Standing caveats (simulated training data, prototype doses, dummy readings) are
attached to the result automatically. Don't repeat them in any field."""


def make_client() -> anthropic.Anthropic:
    # Keys not scoped to a workspace must name one on every request.
    workspace_id = os.environ.get("ANTHROPIC_WORKSPACE_ID")
    headers = {"anthropic-workspace-id": workspace_id} if workspace_id else None
    return anthropic.Anthropic(default_headers=headers)


class AgentRefusedError(RuntimeError):
    pass


def summarize_history(history: pd.DataFrame) -> dict:
    """Compact view of the history for the agent (the full series is too long to send)."""
    h = history.sort_values("hour").reset_index(drop=True)
    now = h["hour"].iloc[-1]
    recent, day1 = h[h["hour"] > now - 6], h[h["hour"] < 24]
    prior = h[(h["hour"] > now - 30) & (h["hour"] <= now - 24)]
    last24 = h[h["hour"] > now - 24]

    sensors = {}
    for c in SENSOR_COLUMNS:
        base = day1[c].median()
        sensors[c] = {
            "latest": round(float(h[c].iloc[-1]), 3),
            "median_last_6h": round(float(recent[c].median()), 3),
            "day1_baseline_median": round(float(base), 3),
            "change_vs_baseline": round(float(recent[c].median() - base), 3),
            "change_vs_24h_ago": (
                round(float(recent[c].median() - prior[c].median()), 3) if len(prior) else None
            ),
            "min_last_24h": round(float(last24[c].min()), 3),
            "max_last_24h": round(float(last24[c].max()), 3),
        }
    cols = ["hour", *SENSOR_COLUMNS]
    return {
        "wound_id": str(h["wound_id"].iloc[0]) if "wound_id" in h else None,
        "n_readings": len(h),
        "hours_since_patch_applied": float(now),
        "latest_timestamp": str(h["timestamp"].iloc[-1]) if "timestamp" in h else None,
        "readings_with_patch_lifted": int((h["impedance_kohm"] > LIFTED_KOHM).sum()),
        "sensors": sensors,
        "last_6h_readings": h[cols].tail(12).round(3).to_dict(orient="records"),
    }


def build_assessment(
    wound_id: str,
    history: pd.DataFrame,
    prediction: InfectionPrediction,
    treatment: TreatmentPlan,
    model: RiskModel,
    data_source: DataSource,
    agent_notes: AgentNotes | None = None,
) -> Assessment:
    last = history.sort_values("hour").iloc[-1]
    return Assessment(
        wound_id=wound_id,
        n_readings=len(history),
        history_hours=float(last["hour"]),
        latest_reading=SensorReading(**{k: last[k] for k in last.index if k in SensorReading.model_fields}),
        prediction=prediction,
        treatment=treatment,
        agent_notes=agent_notes,
        caveats=build_caveats(model, data_source),
    )


def build_caveats(model: RiskModel, data_source: DataSource) -> list[str]:
    caveats = [
        f"Model trained on simulated data only ({model.meta['validation']}); "
        "retrain on real patch data before clinical use.",
        "Doses are prototype settings from published studies, not a validated medical protocol.",
    ]
    if data_source.is_dummy:
        caveats.append("Readings are simulated dummy data.")
    return caveats


def run_assessment(
    wound_id: str,
    data_source: DataSource,
    model: RiskModel,
    client: anthropic.Anthropic | None = None,
    verbose: bool = False,
) -> Assessment:
    client = client or make_client()
    state: dict[str, object] = {}

    @beta_tool
    def get_sensor_history(wound_id: str) -> str:
        """Fetch a summary of the wound's patch readings since it was applied: per-sensor
        latest value, last-6h median, day-1 baseline, 24 h change, 24 h range, and the
        last 6 hours of raw readings.

        Args:
            wound_id: The wound's identifier.
        """
        history = data_source.get_history(wound_id)
        state["history"] = history
        return json.dumps(summarize_history(history), default=str)

    @beta_tool
    def predict_infection() -> str:
        """Run the trained infection model over the fetched history and return the latest
        infection probability, 0-100 risk score (with 6 h and 24 h ago for trend), and
        tier. Call after get_sensor_history."""
        history = state.get("history")
        if not isinstance(history, pd.DataFrame):
            raise ValueError("No history yet; call get_sensor_history first.")
        prediction, result = model.predict(history)
        state["prediction"], state["result"] = prediction, result
        return prediction.model_dump_json()

    @beta_tool
    def plan_treatment() -> str:
        """Compute the next 8-hour session's 405 nm LED, 40 kHz ultrasound and 1.5 MHz
        healing ultrasound plan from the risk score. Call after predict_infection."""
        result = state.get("result")
        if not isinstance(result, pd.DataFrame):
            raise ValueError("No prediction yet; call predict_infection first.")
        plan = model.plan(result)
        state["treatment"] = plan
        return plan.model_dump_json()

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        output_format=AgentNotes,
        tools=[get_sensor_history, predict_infection, plan_treatment],
        messages=[{"role": "user", "content": f"Assess wound {wound_id}."}],
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

    missing = [k for k in ("history", "prediction", "treatment") if k not in state]
    if missing:
        raise RuntimeError(f"Agent finished without calling tools for: {missing}")

    history, prediction, treatment = state["history"], state["prediction"], state["treatment"]
    assert isinstance(history, pd.DataFrame)
    assert isinstance(prediction, InfectionPrediction)
    assert isinstance(treatment, TreatmentPlan)
    return build_assessment(
        wound_id, history, prediction, treatment, model, data_source, final.parsed_output
    )


def run_offline(wound_id: str, data_source: DataSource, model: RiskModel) -> Assessment:
    """Same pipeline without the LLM; useful for tests and when no API key is set."""
    history = data_source.get_history(wound_id)
    prediction, result = model.predict(history)
    return build_assessment(wound_id, history, prediction, model.plan(result), model, data_source)
