"""Amethyst live demo server.

The presenter types patch readings (no hardware yet); each submission runs the real
pipeline and streams every step to the browser:

    patch reading -> Opus agent -> XGBoost model -> treatment plan -> mobile app

Run:
    python demo_ui/server.py            # http://localhost:8000, and on the LAN for the phone app
    python demo_ui/server.py --offline  # never call the LLM (no API key needed)

With ANTHROPIC_API_KEY set (in .env), the agent step runs wound_agent.run_assessment
(Claude Opus with the model and dosing as tools). Without it, the same model and
dosing run and a rule-based summary stands in for the agent's notes.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse, StreamingResponse  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from generate_data import P as SIM  # noqa: E402
from predict import WoundRiskModel  # noqa: E402
from risk_to_dose import LIFTED_KOHM  # noqa: E402
from train_model import add_features  # noqa: E402
from wound_agent.agent import AgentRefusedError, run_assessment, summarize_history  # noqa: E402
from wound_agent.model import RiskModel  # noqa: E402
from wound_agent.schemas import SENSOR_COLUMNS  # noqa: E402

load_dotenv(ROOT / ".env")

WOUND_ID = "demo-wound"
STEP_H = 0.5
BASELINE = {"ph": 6.7, "temp_c": 33.5, "impedance_kohm": 10.0,
            "blood_glucose_mgdl": 100.0, "wound_glucose_mM": 4.2}

# Allowed input ranges (anything outside is rejected).
RANGES = {
    "ph": {"label": "pH", "unit": "pH", "min": 4.5, "max": 9.5},
    "temp_c": {"label": "Temperature", "unit": "°C", "min": 25, "max": 45},
    "impedance_kohm": {"label": "Moisture", "unit": "kΩ", "min": 1, "max": 800},
    "blood_glucose_mgdl": {"label": "Blood glucose", "unit": "mg/dL", "min": 40, "max": 400},
    "wound_glucose_mM": {"label": "Wound glucose", "unit": "mM", "min": 0.2, "max": 15},
}

# ---- one source of truth for colours, presets and the offline agent ----
# How far each sensor moves in a typical infection, taken from the simulator the
# model was trained on (generate_data.P). Moisture and wound glucose are fractions.
EFFECT = {
    "ph": SIM["ph_infection_rise"][0],                    # +0.65 pH
    "temp_c": SIM["temp_infection_rise"][0],              # +1.6 °C
    "impedance_kohm": -SIM["z_infection_drop"][0],        # -35 %
    "wound_glucose_mM": -SIM["wound_glucose_drop"][0],    # -40 %
    "blood_glucose_mgdl": SIM["blood_glucose_rise"][0],   # +8 mg/dL
}
RELATIVE = {"impedance_kohm", "wound_glucose_mM"}
WARN_K, INFECT_K = 0.25, 0.70        # share of a typical infection's change
BG_WARN_MGDL = 20                    # blood glucose is weak alone; flag only big rises
# Physically implausible readings (the agent is told the same in its prompt).
LIMITS = {"temp_c": (26.0, 41.0), "ph": (5.0, 9.2)}
TIER_LEVEL = {"monitor": "normal", "watch": "warning", "treat": "infection", "intensive": "infection"}


def signal_level(k: str, v: float, base: float) -> str:
    """normal / warning / infection for one reading against the patient's baseline."""
    if k == "blood_glucose_mgdl":
        return "warning" if v - base >= BG_WARN_MGDL else "normal"
    change = (v - base) / base if k in RELATIVE else v - base
    frac = change / EFFECT[k]
    return "infection" if frac >= INFECT_K else "warning" if frac >= WARN_K else "normal"


def sensor_faults(latest: dict) -> list[str]:
    out = []
    if latest["impedance_kohm"] > LIFTED_KOHM:
        out.append(f"Patch off skin: impedance {latest['impedance_kohm']:.0f} kΩ; treatment held.")
    lo, hi = LIMITS["temp_c"]
    if not lo <= latest["temp_c"] <= hi:
        out.append(f"Temp sensor fault: {latest['temp_c']:.1f} °C is outside skin range.")
    lo, hi = LIMITS["ph"]
    if not lo <= latest["ph"] <= hi:
        out.append(f"pH sensor fault: {latest['ph']:.2f} is outside the wound range.")
    return out


def zones(base: dict) -> dict:
    """Colour bands per sensor in absolute units, for this patient's baseline."""
    z = {}
    for k in ("ph", "temp_c"):
        b, e = base[k], EFFECT[k]
        lo, hi = b - 0.9 * e, b + 1.6 * e
        t1, t2 = b + WARN_K * e, b + INFECT_K * e
        z[k] = {"lo": lo, "hi": hi, "bands": [[lo, t1, "normal"], [t1, t2, "warning"], [t2, hi, "infection"]]}
    for k in ("impedance_kohm", "wound_glucose_mM"):
        b, e = base[k], EFFECT[k]
        lo, hi = b * 0.35, b * 1.5
        t1, t2 = b * (1 + WARN_K * e), b * (1 + INFECT_K * e)
        z[k] = {"lo": lo, "hi": hi, "bands": [[lo, t2, "infection"], [t2, t1, "warning"], [t1, hi, "normal"]]}
    b = base["blood_glucose_mgdl"]
    z["blood_glucose_mgdl"] = {"lo": 50, "hi": 250, "bands": [[50, b + BG_WARN_MGDL, "normal"], [b + BG_WARN_MGDL, 250, "warning"]]}
    return z


def presets(base: dict) -> dict:
    """Scenarios built from the same effect sizes. Durations were checked against the
    model: Healthy stays in monitor, Early infection lands in watch (risk ~35-50),
    Infection in treat/intensive."""
    def shift(k: float) -> dict:
        v = {c: base[c] * (1 + k * EFFECT[c]) if c in RELATIVE else base[c] + k * EFFECT[c] for c in SENSOR_COLUMNS}
        return {c: round(x, 2) for c, x in v.items()}
    healthy = shift(0)
    return {
        "Healthy": {"values": healthy, "hours": 6, "expect": "normal"},
        "Early infection": {"values": shift(0.45), "hours": 4, "expect": "warning"},
        "Infection": {"values": shift(1.0), "hours": 6, "expect": "infection"},
        "Patch lifted": {"values": {**healthy, "impedance_kohm": 450.0, "temp_c": round(base["temp_c"] - 5, 1)},
                         "hours": 0.5, "expect": "fault"},
        "Sensor fault": {"values": {**healthy, "temp_c": 43.5}, "hours": 2, "expect": "fault"},
    }


SENSOR_NAMES = {"ph": "pH", "temp_c": "Temperature", "log_z": "Moisture",
                "impedance_kohm": "Moisture", "blood_glucose_mgdl": "Blood glucose",
                "wound_glucose_mM": "Wound glucose", "tod": "Time of day"}


# --------------------------------------------------------------------------- state
class Wound:
    """One simulated wound's 30-minute history, seeded with a healthy first day."""

    def __init__(self, seed: int = 7):
        self.rng = np.random.default_rng(seed)
        self.lock = threading.Lock()
        self.start = pd.Timestamp.now(tz="UTC").floor("30min") - pd.Timedelta(hours=24)
        self.history = self._ramp(BASELINE, BASELINE, 0.0, 24.0)
        self.latest_assessment: dict | None = None

    def _ramp(self, frm: dict, to: dict, h0: float, hours: float) -> pd.DataFrame:
        """Readings from h0 for `hours`, easing from `frm` to `to` over the first half,
        with sensor noise, a day/night temperature cycle and meal spikes in glucose."""
        n = max(1, int(round(hours / STEP_H)))
        hrs = h0 + STEP_H * np.arange(1 if h0 else 0, n + (1 if h0 else 0))
        frac = np.clip((hrs - h0) / max(hours / 2, STEP_H), 0, 1)
        rows = {}
        for c in SENSOR_COLUMNS:
            a, b = frm[c], to[c]
            jump = c == "impedance_kohm" and (a > LIFTED_KOHM or b > LIFTED_KOHM)
            rows[c] = np.full(len(hrs), b) if jump else a + (b - a) * frac
        clock = ((self.start + pd.to_timedelta(hrs, unit="h")).hour.values
                 + (self.start + pd.to_timedelta(hrs, unit="h")).minute.values / 60)
        rows["ph"] = rows["ph"] + self.rng.normal(0, 0.03, len(hrs))
        rows["temp_c"] = rows["temp_c"] + 0.35 * np.cos(2 * np.pi * (clock - 3) / 24) + self.rng.normal(0, 0.06, len(hrs))
        rows["impedance_kohm"] = rows["impedance_kohm"] * (1 + self.rng.normal(0, 0.03, len(hrs)))
        meals = sum(30 * np.exp(-0.5 * ((clock - m) / 0.9) ** 2) for m in (8.7, 13.6, 19.6))
        rows["blood_glucose_mgdl"] = rows["blood_glucose_mgdl"] + meals + self.rng.normal(0, 3, len(hrs))
        rows["wound_glucose_mM"] = rows["wound_glucose_mM"] * (1 + self.rng.normal(0, 0.02, len(hrs)))
        df = pd.DataFrame({"wound_id": WOUND_ID, "hour": hrs, **rows})
        df["timestamp"] = self.start + pd.to_timedelta(df["hour"], unit="h")
        return df.round({"ph": 3, "temp_c": 2, "impedance_kohm": 2, "blood_glucose_mgdl": 1, "wound_glucose_mM": 2})

    def baseline(self) -> dict:
        day1 = self.history[self.history["hour"] < 24]
        return {c: round(float(day1[c].median()), 2) for c in SENSOR_COLUMNS}

    def add(self, target: dict, hours: float) -> pd.DataFrame:
        last = self.history.iloc[-1]
        prev = {c: float(last[c]) for c in SENSOR_COLUMNS}
        # meal spikes are added on top, so ramp from the de-spiked glucose level
        prev["blood_glucose_mgdl"] = float(self.history["blood_glucose_mgdl"].tail(12).min())
        new = self._ramp(prev, target, float(last["hour"]), hours)
        self.history = pd.concat([self.history, new], ignore_index=True)
        return new


class EventSource:
    """DataSource for the agent that reports each tool call to the UI."""

    is_dummy = True

    def __init__(self, wound: Wound, emit):
        self.wound, self.emit = wound, emit

    def get_history(self, wound_id: str) -> pd.DataFrame:
        self.emit("agent", "active", "Tool · get_sensor_history", "")
        return self.wound.history.copy()


class EventModel(RiskModel):
    """RiskModel that reports when the agent calls it."""

    def __init__(self, emit):
        super().__init__()
        self.emit = emit

    def predict(self, history):
        self.emit("ml", "active", "Tool · predict_infection", "")
        return super().predict(history)

    def plan(self, result):
        self.emit("therapy", "active", "Tool · plan_treatment", "")
        return super().plan(result)


# --------------------------------------------------------------------------- explain
def sensor_drivers(model: WoundRiskModel, history: pd.DataFrame) -> list[dict]:
    """Per-sensor SHAP contribution (infection minus normal log-odds) for the latest reading."""
    feats = add_features(history.assign(wound_id=WOUND_ID), STEP_H)
    x = feats[model.features].fillna(0).values[-1:]
    contribs = model.model.get_booster().predict(xgb.DMatrix(x, feature_names=model.features), pred_contribs=True)
    c = contribs[0]                                       # (classes, features + bias)
    i_n, i_w, i_i = (model.labels.index(k) for k in ("normal", "warning", "infection"))
    toward = (np.maximum(c[i_w], c[i_i]) - c[i_n])[:-1]
    sensors = ["ph", "temp_c", "log_z", "blood_glucose_mgdl", "wound_glucose_mM"]
    by_sensor: dict[str, float] = {}
    for f, v in zip(model.features, toward):
        key = next((k for k in sensors if f.startswith(k)), "tod")
        by_sensor[key] = by_sensor.get(key, 0.0) + float(v)
    return sorted(({"sensor": SENSOR_NAMES[k], "contribution": round(v, 3)} for k, v in by_sensor.items()),
                  key=lambda d: -abs(d["contribution"]))


def offline_notes(summary: dict, pred: dict, plan: dict) -> dict:
    """Rule-based stand-in for the Opus agent's notes (used when no API key is set).
    Uses the same thresholds as the input colours."""
    s = summary["sensors"]
    base = {k: s[k]["day1_baseline_median"] for k in s}
    recent = {k: s[k]["median_last_6h"] for k in s}
    latest = {k: s[k]["latest"] for k in s}
    signs = []
    for k, name in [("ph", "pH"), ("temp_c", "temp"), ("impedance_kohm", "moisture"), ("wound_glucose_mM", "wound glucose")]:
        if signal_level(k, recent[k], base[k]) != "normal":
            d = recent[k] - base[k]
            signs.append(f"{name} {d / base[k] * 100:+.0f}%" if k in RELATIVE else f"{name} {d:+.2f}" if k == "ph" else f"{name} {d:+.1f} °C")
    flags = sensor_faults(latest)
    conflicts = []
    risk, tier = pred["risk_score"], pred["tier"].split(" ", 1)[1]
    level = TIER_LEVEL[tier]
    if level == "infection" and signal_level("ph", recent["ph"], base["ph"]) == "normal":
        conflicts.append("pH is not rising; some infections keep the wound acidic, so this does not rule it out.")
    if level == "normal" and len(signs) >= 2:
        conflicts.append("Several signals have moved but not for long enough to cross the watch threshold.")
    if signal_level("blood_glucose_mgdl", recent["blood_glucose_mgdl"], base["blood_glucose_mgdl"]) != "normal" and not signs:
        conflicts.append("Blood glucose is up but no wound signals moved; likely a meal, not infection.")
    verdict = {"monitor": "Healing normally.", "watch": "Early warning signs.",
               "treat": "Infection likely. Starting therapy.", "intensive": "Strong infection signal. Intensive therapy."}[tier]
    if flags:
        verdict = "Sensor problem. Check the patch."
    summary_txt = f"{verdict} {', '.join(signs)} vs baseline." if signs else f"{verdict} Signals at baseline."
    trend = (f"Risk {pred['risk_score_6h_ago'] or 0:.0f} six hours ago → {risk:.0f} now."
             if pred.get("risk_score_6h_ago") is not None else f"Risk {risk:.0f} now.")
    review = level == "infection" or bool(flags) or bool(conflicts and level != "normal")
    confidence = "low" if flags else ("high" if len(signs) >= 3 or (level == "normal" and not signs) else "medium")
    return {"summary": summary_txt, "trend": trend,
            "reasoning": ("Combined change across sensors drives the call; no single sensor is reliable alone."
                          if signs else "No sensor has moved enough from baseline to suggest infection."),
            "data_quality_flags": flags, "conflicting_signals": conflicts,
            "recommend_clinician_review": review, "confidence": confidence}


# --------------------------------------------------------------------------- pipeline
class Reading(BaseModel):
    ph: float
    temp_c: float
    impedance_kohm: float
    blood_glucose_mgdl: float
    wound_glucose_mM: float
    advance_hours: float = Field(6.0, ge=0.5, le=48)
    use_agent: bool = True


def run_pipeline(wound: Wound, reading: Reading, use_llm: bool, emit) -> dict:
    target = reading.model_dump(include=set(SENSOR_COLUMNS))
    for k, v in target.items():
        r = RANGES[k]
        if not r["min"] <= v <= r["max"]:
            raise ValueError(f"{r['label']} must be between {r['min']} and {r['max']} {r['unit']}")

    with wound.lock:
        emit("hardware", "active", "Reading received",
             " · ".join(f"{v:g} {RANGES[k]['unit']}" for k, v in target.items()),
             {"reading": target})
        new = wound.add(target, reading.advance_hours)
        hist = wound.history
        emit("hardware", "done", f"{reading.advance_hours:g} h streamed", f"{len(new)} readings · hour {hist['hour'].iloc[-1]:.1f}")

        summary = summarize_history(hist)
        emit("agent", "active", "Compared to baseline",
             " · ".join(f"{SENSOR_NAMES[k]} {v['change_vs_baseline']:+.2g}" for k, v in summary["sensors"].items()),
             {"summary": summary["sensors"]})

        model = RiskModel()
        notes, source = None, "rules"
        if use_llm:
            emit("agent", "active", "Opus reasoning", "")
            try:
                t0 = time.time()
                a = run_assessment(WOUND_ID, EventSource(wound, emit), EventModel(emit))
                pred, plan = a.prediction.model_dump(), a.treatment.model_dump()
                notes, source = (a.agent_notes.model_dump() if a.agent_notes else None), "opus"
                emit("agent", "done", f"Opus done · {time.time() - t0:.0f} s", "")
            except (AgentRefusedError, Exception) as exc:  # fall back so the demo never stalls
                emit("agent", "warn", "Opus unavailable · offline", str(exc)[:120])
                use_llm = False
        if not use_llm:
            emit("ml", "active", "XGBoost scoring", "27 trend features")
            p, result = model.predict(hist)
            pred = p.model_dump()
            emit("therapy", "active", "Planning therapy", "")
            plan = model.plan(result).model_dump()

        drivers = sensor_drivers(model._model, hist)
        emit("ml", "done", f"Risk {pred['risk_score']:.0f} · {pred['tier'].split(' ', 1)[1]}",
             "Pushing risk up: " + (", ".join(d["sensor"] for d in drivers if d["contribution"] > 0.05 and d["sensor"] != "Time of day")[:80] or "none"),
             {"prediction": pred, "drivers": drivers,
              "level": TIER_LEVEL[pred["tier"].split(" ", 1)[1]]})

        if notes is None:
            notes = offline_notes(summary, pred, plan)
        emit("agent", "done", "Assessment ready", "", {"notes": notes, "source": source})

        if plan.get("skipped_reason"):
            therapy = plan["skipped_reason"]
        elif plan["order"] == "-":
            therapy = "No treatment this session"
        else:
            parts = []
            if plan["us_40khz_min"]:
                parts.append(f"40 kHz ultrasound {plan['us_40khz_min']:g} min @ {plan['us_40khz_w_cm2']:g} W/cm²")
            if plan["led_405nm_min"]:
                parts.append(f"405 nm LED {plan['led_405nm_min']:g} min ({plan['led_dose_j_cm2']:g} J/cm²)")
            if plan["us_1p5mhz_min"]:
                parts.append(f"1.5 MHz healing ultrasound {plan['us_1p5mhz_min']:g} min")
            therapy = " → ".join(parts)
        emit("therapy", "done", "Therapy plan", therapy, {"plan": plan})

        series = model._model.predict(hist)
        risk_series = series[["hour", "risk_score"]].round(1).to_dict("records")
        latest = hist.iloc[-1]
        faults = sensor_faults({c: float(latest[c]) for c in SENSOR_COLUMNS})
        level = "fault" if faults else TIER_LEVEL[pred["tier"].split(" ", 1)[1]]
        state = {
            "level": level, "faults": faults, "baseline": wound.baseline(),
            "wound_id": WOUND_ID,
            "hours": float(latest["hour"]),
            "latest_reading": {c: float(latest[c]) for c in SENSOR_COLUMNS},
            "prediction": pred, "treatment": plan, "therapy_text": therapy,
            "notes": notes, "notes_source": source, "drivers": drivers,
            "risk_series": risk_series,
            "history": hist[["hour", *SENSOR_COLUMNS]].iloc[::2].round(3).to_dict("records"),
        }
        state["zones"] = zones(state["baseline"])
        state["seq"] = next_seq()
        state["updated_at"] = time.time()
        wound.latest_assessment = state
        emit("mobile", "done", "Sent to app",
             {"normal": "Normal", "warning": "Warning", "infection": "Infection alert", "fault": "Check patch"}[level],
             {"state": state, "level": level})
        return state


# --------------------------------------------------------------------------- app
app = FastAPI(title="Amethyst live demo")
# The Expo app polls /api/state from the phone (or Expo web in a browser).
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])
WOUND = Wound()
OFFLINE = False
SEQ = 0          # bumps on every new assessment or reset so the app knows something changed
RUNNING = False  # a reading is being processed right now


def next_seq() -> int:
    global SEQ
    SEQ += 1
    return SEQ


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/api/config")
def config():
    llm = (not OFFLINE) and bool(os.environ.get("ANTHROPIC_API_KEY"))
    return {"ranges": RANGES, "llm_available": llm, **patient_config()}


def patient_config() -> dict:
    base = WOUND.baseline()
    return {"baseline": base, "zones": zones(base), "presets": presets(base),
            "hours": float(WOUND.history["hour"].iloc[-1])}


@app.get("/api/state")
def state():
    """Latest assessment; the Expo app polls this. `level` is absent until the first reading."""
    base = WOUND.latest_assessment or {"wound_id": WOUND_ID, "hours": float(WOUND.history["hour"].iloc[-1]),
                                       "baseline": WOUND.baseline(), "zones": zones(WOUND.baseline()), "seq": SEQ}
    return {**base, "running": RUNNING}


@app.post("/api/reset")
def reset():
    global WOUND
    WOUND = Wound(seed=int(time.time()) % 10_000)
    next_seq()
    return patient_config()


@app.post("/api/reading")
async def reading(r: Reading):
    use_llm = r.use_agent and not OFFLINE and bool(os.environ.get("ANTHROPIC_API_KEY"))
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    t0 = time.time()

    def emit(stage, status, title, detail="", data=None):
        ev = {"stage": stage, "status": status, "title": title, "detail": detail,
              "data": data, "t": round(time.time() - t0, 2)}
        loop.call_soon_threadsafe(queue.put_nowait, ev)

    def work():
        global RUNNING
        RUNNING = True
        try:
            run_pipeline(WOUND, r, use_llm, emit)
        except ValueError as exc:
            emit("error", "error", "Invalid reading", str(exc))
        except Exception as exc:  # surface anything else to the UI
            emit("error", "error", "Pipeline error", repr(exc)[:300])
        finally:
            RUNNING = False
            loop.call_soon_threadsafe(queue.put_nowait, None)

    threading.Thread(target=work, daemon=True).start()

    async def stream():
        while (ev := await queue.get()) is not None:
            yield json.dumps(ev, default=float) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")


if __name__ == "__main__":
    import uvicorn

    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    # 0.0.0.0 so a phone on the same Wi-Fi can reach /api/state; use --host 127.0.0.1 to keep it local
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--offline", action="store_true", help="never call the LLM")
    a = ap.parse_args()
    OFFLINE = a.offline
    if a.host == "0.0.0.0":
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.connect(("10.255.255.255", 1))
                ip = s.getsockname()[0]
            except OSError:
                ip = "<this laptop's IP>"
        print(f"\n  Demo UI:  http://localhost:{a.port}\n  App API:  http://{ip}:{a.port}  (set this in the Expo app if it can't find the server)\n")
    uvicorn.run(app, host=a.host, port=a.port)
