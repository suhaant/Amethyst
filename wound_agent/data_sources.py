"""Where a wound's sensor history comes from.

A history is a DataFrame with one row every 30 min and columns
`timestamp` (or `hour`) plus SENSOR_COLUMNS, starting when the patch went on.
The model needs at least 24 h (the first day sets the patient's baseline).

To plug in real data, either:
  * pass `--history path.csv` / `.json` (same format predict.py reads), or
  * write a class with `get_history(wound_id) -> DataFrame`, plus an `is_dummy`
    attribute, and return it from `get_data_source()`.
"""

from __future__ import annotations

from typing import Protocol

import numpy as np
import pandas as pd

from generate_data import simulate_wound
from predict import load_readings

from .schemas import SENSOR_COLUMNS

STEP_MIN = 30
STEPS_PER_DAY = 24 * 60 // STEP_MIN
SIM_DAYS = 10


class DataSource(Protocol):
    is_dummy: bool

    def get_history(self, wound_id: str) -> pd.DataFrame: ...


def synthetic_person(rng: np.random.Generator, n_days: int = 7) -> dict:
    """Stand-in for a real CGM trace (the simulator normally uses PhysioNet Dexcom data):
    ~95 mg/dL fasting with breakfast, lunch and dinner spikes."""
    t = np.arange(STEPS_PER_DAY) * STEP_MIN / 60
    days = []
    for _ in range(n_days):
        day = rng.normal(95, 4) + rng.normal(0, 3, STEPS_PER_DAY)
        for meal_h in (8, 13, 19):
            peak_h = meal_h + rng.uniform(0.5, 1.0)
            day += rng.uniform(25, 55) * np.exp(-0.5 * ((t - peak_h) / 0.8) ** 2)
        days.append(day)
    return {"hba1c": 5.6, "days": days}


# Each scenario: which simulated outcome to look for and where to cut the history.
SCENARIOS = {
    "healthy": "healing wound, 4 days of readings",
    "early_infection": "infected wound, cut 2 h after the model first reaches the watch tier",
    "infected": "infected wound, cut ~72 h after infection onset",
    "sensor_fault": "healing wound whose temperature sensor reads ~43 °C for the last 3 h",
    "patch_lifted": "healing wound whose patch lifted off in the last 2 h",
}


class DummyDataSource:
    """Runs Adam's wound simulator until it produces a wound matching the scenario."""

    is_dummy = True

    def __init__(self, scenario: str = "infected", seed: int | None = None):
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario {scenario!r}; choose from {list(SCENARIOS)}")
        self.scenario = scenario
        self.seed = seed if seed is not None else int(np.random.SeedSequence().entropy % 2**31)

    def get_history(self, wound_id: str) -> pd.DataFrame:
        want_infected = self.scenario in ("early_infection", "infected")
        hours = np.arange(0, SIM_DAYS * 24, STEP_MIN / 60)
        for attempt in range(500):
            rng = np.random.default_rng([self.seed, attempt])
            sim = simulate_wound(wound_id, hours, rng, 0, synthetic_person(rng))
            infected = sim["outcome"].iloc[0] == "infected"
            if want_infected != infected or (not infected and sim["outcome"].iloc[0] != "healing"):
                continue
            cut = self._cut_hour(sim)
            if cut is None:
                continue
            hist = sim[sim["hour"] < cut]
            # Patch peel-offs are injected deliberately below, not left to chance.
            if hist["impedance_kohm"].max() > 150:
                continue
            return self._finish(hist.copy(), rng)
        raise RuntimeError(f"Simulator found no {self.scenario!r} wound in 500 tries")

    def _cut_hour(self, sim: pd.DataFrame) -> float | None:
        onset = sim["infection_onset_h"].iloc[0]
        if self.scenario == "early_infection":
            from .model import RiskModel  # deferred: only this scenario needs the model

            result = RiskModel().predict(sim[["wound_id", "hour", *SENSOR_COLUMNS]])[1]
            flagged = result[(result["hour"] >= onset) & (result["risk_score"] >= 30)]
            return None if flagged.empty else flagged["hour"].iloc[0] + 2
        if self.scenario == "infected":
            return onset + 72
        return 96

    def _finish(self, hist: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
        if self.scenario == "sensor_fault":
            last = hist.index[-6:]
            hist.loc[last, "temp_c"] = np.round(rng.uniform(42.5, 44.0, len(last)), 2)
        if self.scenario == "patch_lifted":
            last = hist.index[-4:]
            hist.loc[last, "impedance_kohm"] = np.round(rng.uniform(300, 700, len(last)), 2)
            hist.loc[last, "temp_c"] = np.round(hist.loc[last, "temp_c"] - rng.uniform(4, 6), 2)
        # Real data won't carry the simulator's answer key, so drop it here too.
        start = pd.Timestamp.now(tz="UTC").floor("30min") - pd.Timedelta(hours=hist["hour"].iloc[-1])
        hist["timestamp"] = start + pd.to_timedelta(hist["hour"], unit="h")
        return hist[["wound_id", "timestamp", "hour", *SENSOR_COLUMNS]].reset_index(drop=True)


class FileDataSource:
    """Reads a history from CSV or JSON in the format predict.py accepts."""

    is_dummy = False

    def __init__(self, path: str):
        self.path = path

    def get_history(self, wound_id: str) -> pd.DataFrame:
        df = load_readings(self.path)
        if "wound_id" in df.columns and df["wound_id"].nunique() > 1:
            df = df[df["wound_id"].astype(str) == wound_id]
            if df.empty:
                raise ValueError(f"No readings for wound {wound_id!r} in {self.path}")
        df = df.assign(wound_id=wound_id)
        if "hour" not in df.columns:
            ts = pd.to_datetime(df["timestamp"])
            df["hour"] = (ts - ts.min()).dt.total_seconds() / 3600
        return df.sort_values("hour").reset_index(drop=True)


def get_data_source(
    history_path: str | None = None, scenario: str = "infected", seed: int | None = None
) -> DataSource:
    if history_path:
        return FileDataSource(history_path)
    return DummyDataSource(scenario=scenario, seed=seed)
