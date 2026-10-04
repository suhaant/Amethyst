"""
Infection risk from smart-patch readings, using the trained XGBoost model.

Input: one or more wounds' readings in time order (every 30 min), with columns
    wound_id, timestamp (ISO 8601) or hour, ph, temp_c, impedance_kohm,
    blood_glucose_mgdl, wound_glucose_mM

Output per reading:
    p_infected   model probability of warning or infection (0-1): how LIKELY infection is
    severity     how far the patch signals have moved toward a full infection (0-1)
    risk_score   3-hour smoothed p_infected x severity (0-100)
    tier         0 monitor / 1 watch / 2 treat / 3 intensive
plus the LED / ultrasound plan for the latest reading.

The first 24 h of each wound are used to learn that patient's baseline, so
no risk is returned for them.

Why likelihood x severity: trained on cleanly separated simulated data, the
classifier is near-certain (p ~ 1) for ANY sustained shift, even 15% of a full
infection, so p alone only says "something is off" and the score pinned at 0 or
100. Severity scales it by how strong the infection signs are, so a small shift
gives a low/moderate risk and a full-blown infection a high one.

Command line:
    python predict.py readings.csv            # flat CSV, one row per reading
    python predict.py readings.json           # [{"wound_id", "readings": [...]}, ...]
    python predict.py readings.csv --out risk.csv

From Python (e.g. inside an API):
    from predict import WoundRiskModel
    model = WoundRiskModel()
    result = model.predict(readings_df)       # DataFrame in, DataFrame out
    plan = model.latest_plan(result)          # dict per wound
"""

import argparse
import json
import os

import numpy as np
import pandas as pd
from xgboost import XGBClassifier

from risk_to_dose import TIERS, session_plan, smooth_risk, tiers_with_hysteresis
from train_model import add_features

HERE = os.path.dirname(os.path.abspath(__file__))

# Mean change from baseline in a full infection, from generate_data.P (the simulator the
# model was trained on): pH +0.65, temperature +1.6 °C, impedance -35 %, wound glucose -40 %.
FULL_EFFECT = {"ph": 0.65, "temp_c": 1.6, "log_z": -np.log(1 - 0.35), "wound_glucose_rel": 0.40}


def infection_severity(feats, step_h):
    """0-1: how far the patch signals have moved, against the patient's own day-1
    baseline, toward a full infection. Mean of the 3 strongest of 4 signs, since not
    every infection shows every sign (pH fails to rise in some). Uses a 2 h median
    (knocks out shower / dressing spikes but reacts faster than the model's 6 h one)."""
    w2 = max(1, int(round(2 / step_h)))
    cols = []
    for c, sign, scale in [("ph", 1, FULL_EFFECT["ph"]), ("temp_c", 1, FULL_EFFECT["temp_c"]),
                           ("log_z", -1, FULL_EFFECT["log_z"]), ("wound_glucose_mM", -1, None)]:
        base = feats[f"{c}_sm"] - feats[f"{c}_vs_base"]          # day-1 baseline per row
        now = feats.groupby("wound_id")[c].transform(lambda s: s.rolling(w2, min_periods=1).median())
        delta = sign * (now - base)
        cols.append(delta / (scale if scale else base.clip(lower=0.1) * FULL_EFFECT["wound_glucose_rel"]))
    parts = np.clip(np.nan_to_num(np.column_stack(cols)), 0, 1.25)
    top3 = np.sort(parts, axis=1)[:, 1:]
    return np.clip(top3.mean(axis=1), 0, 1)


SENSORS = ["ph", "temp_c", "impedance_kohm", "blood_glucose_mgdl", "wound_glucose_mM"]


class WoundRiskModel:
    def __init__(self, model_dir=os.path.join(HERE, "model")):
        with open(os.path.join(model_dir, "model_meta.json")) as f:
            self.meta = json.load(f)
        self.model = XGBClassifier()
        self.model.load_model(os.path.join(model_dir, "xgboost_model.json"))
        self.features = self.meta["features"]
        self.labels = self.meta["labels"]
        self.step_h = self.meta["step_min"] / 60

    def _prepare(self, df):
        df = df.copy()
        missing = [c for c in SENSORS if c not in df.columns]
        if missing:
            raise ValueError(f"missing sensor columns: {missing}")
        if "wound_id" not in df.columns:
            df["wound_id"] = "wound"
        if "hour" not in df.columns:
            if "timestamp" not in df.columns:
                raise ValueError("need a 'timestamp' or 'hour' column")
            ts = pd.to_datetime(df["timestamp"])
            df["hour"] = (ts - ts.groupby(df["wound_id"]).transform("min")).dt.total_seconds() / 3600
        return df.sort_values(["wound_id", "hour"]).reset_index(drop=True)

    def predict(self, df):
        df = self._prepare(df)
        feats = add_features(df, self.step_h)
        feats = feats[feats["hour"] >= 24].reset_index(drop=True)
        if feats.empty:
            raise ValueError("need more than 24 h of readings per wound to set the baseline")
        proba = self.model.predict_proba(feats[self.features].fillna(0).values)
        i_w, i_i = self.labels.index("warning"), self.labels.index("infection")
        feats["p_infected"] = np.clip(proba[:, i_w] + proba[:, i_i], 0, 1).round(4)
        feats["predicted_label"] = np.array(self.labels)[proba.argmax(1)]
        feats["severity"] = infection_severity(feats, self.step_h).round(3)

        out = []
        for _, g in feats.groupby("wound_id", sort=False):
            g = g.copy()
            g["risk_score"] = smooth_risk((g["p_infected"] * g["severity"]).values, self.step_h).round(1)
            g["tier"] = tiers_with_hysteresis(g["risk_score"].values)
            g["tier_name"] = [TIERS[t][0] for t in g["tier"]]
            out.append(g)
        keep = ["wound_id"] + (["timestamp"] if "timestamp" in df.columns else []) + \
               ["hour", "p_infected", "severity", "predicted_label", "risk_score", "tier", "tier_name", "impedance_kohm"]
        return pd.concat(out, ignore_index=True)[keep]

    @staticmethod
    def latest_plan(result):
        plans = {}
        for wid, g in result.groupby("wound_id", sort=False):
            last = g.iloc[-1]
            plan = session_plan(last["risk_score"], int(last["tier"]))
            if last["impedance_kohm"] > 150:                     # patch not on skin
                plan = {"status": "SKIPPED: patch not on skin"}
            plans[wid] = {"risk_score": float(last["risk_score"]), "tier": last["tier_name"], **plan}
        return plans


def load_readings(path):
    if path.endswith(".json"):
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        return pd.DataFrame([{"wound_id": w.get("wound_id", "wound"), **r}
                             for w in data for r in w["readings"]])
    return pd.read_csv(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("readings", help="CSV or JSON of patch readings")
    ap.add_argument("--out", help="write per-reading risk to this CSV")
    a = ap.parse_args()

    model = WoundRiskModel()
    result = model.predict(load_readings(a.readings))
    if a.out:
        result.drop(columns="impedance_kohm").to_csv(a.out, index=False)
        print(f"wrote {len(result):,} rows -> {a.out}")
    print(json.dumps(model.latest_plan(result), indent=2, default=float))


if __name__ == "__main__":
    main()
