"""
Build a held-out demo / API-test dataset the model has never seen.

- Holds out 3 real glucose participants (14, 15, 16): the saved model is
  retrained WITHOUT them, and every demo wound uses only their glucose.
- New random seed, so every wound is new.
- 4 scripted scenario wounds for the live demo + 16 random wounds.
- Inputs (no answers) and the answer key are separate files.

Usage:
    python make_demo.py
"""

import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from generate_data import simulate_wound
from glucose_data import load_participants
from train_model import CHANNELS, LABELS, add_features, feature_cols, wound_alarms

HOLDOUT = [14, 15, 16]
SEED = 2026
DAYS = 10
STEP_MIN = 30
START = pd.Timestamp("2026-10-12 08:00")
OUT = "demo_dataset"
SENSOR_COLS = ["ph", "temp_c", "impedance_kohm", "blood_glucose_mgdl", "wound_glucose_mM"]


def train_holdout_model():
    df = pd.read_csv("data/wound_timeseries.csv")
    df = df[~df["participant_id"].isin(HOLDOUT)]
    step_h = STEP_MIN / 60
    df = add_features(df, step_h)
    df = df[df["hour"] >= 24]
    feats = feature_cols(CHANNELS["patch+cgm+wound"])
    clf = RandomForestClassifier(n_estimators=150, max_depth=14, min_samples_leaf=20,
                                 n_jobs=-1, random_state=0)
    clf.fit(df[feats].fillna(0).values, df["label"].values)
    return clf, feats, df["wound_id"].nunique()


def generate_candidates(n=80):
    rng = np.random.default_rng(SEED)
    people = load_participants(STEP_MIN)
    hours = np.arange(0, DAYS * 24, STEP_MIN / 60)
    out = []
    for w in range(n):
        pid = HOLDOUT[w % len(HOLDOUT)]
        out.append(simulate_wound(w, hours, rng, pid, people[pid]))
    return pd.concat(out, ignore_index=True)


def pick(df):
    """4 scripted scenarios + 16 random wounds -> 20 demo wounds."""
    w = df.groupby("wound_id").agg(outcome=("outcome", "first"), onset=("infection_onset_h", "first"),
                                   detached=("impedance_kohm", lambda s: (s > 150).any()))
    used, scen = [], {}

    def take(mask, name, desc):
        cand = w[mask & ~w.index.isin(used)]
        wid = cand.index[0]
        used.append(wid)
        scen[wid] = (name, desc)

    take((w.outcome == "healing") & ~w.detached, "A_healing",
         "Clean wound healing normally. Model should stay quiet the whole time.")
    take((w.outcome == "infected") & w.onset.between(60, 100) & ~w.detached, "B_infection",
         "Bacteria arrive around day 3-4. Watch pH/temp rise and impedance + wound glucose fall; alarm should fire ~1 day later.")
    take((w.outcome == "stalled") & ~w.detached, "C_stalled",
         "Non-healing but NOT infected. Tests that 'not getting better' is not mistaken for infection.")
    take((w.outcome != "infected") & w.detached, "D_patch_peel",
         "Clean wound where the patch peels off for a few hours (impedance jumps, temperature drops). Tests false-alarm resistance.")
    rest = w[~w.index.isin(used)].sample(16, random_state=SEED).index.tolist()
    order = used + rest
    rename = {old: f"DEMO-{i + 1:02d}" for i, old in enumerate(order)}
    df = df[df.wound_id.isin(order)].copy()
    df["wound_id"] = df["wound_id"].map(rename)
    scen = {rename[k]: v for k, v in scen.items()}
    return df.sort_values(["wound_id", "hour"]).reset_index(drop=True), scen


def main():
    os.makedirs(OUT, exist_ok=True)
    print("training model without held-out participants", HOLDOUT, "...")
    clf, feats, n_train = train_holdout_model()
    joblib.dump({"model": clf, "features": feats, "step_min": STEP_MIN,
                 "holdout_participants": HOLDOUT}, os.path.join(OUT, "model.joblib"))

    df, scen = pick(generate_candidates())
    df["timestamp"] = (START + pd.to_timedelta(df["hour"], unit="h")).dt.strftime("%Y-%m-%dT%H:%M:%S")
    df["patient_id"] = "P" + df["participant_id"].astype(str)

    # inputs only - what the patch/app would actually send
    inputs = df[["wound_id", "patient_id", "timestamp", "hour"] + SENSOR_COLS]
    inputs.to_csv(os.path.join(OUT, "demo_readings.csv"), index=False)

    # nested JSON: one object per wound, readings in time order (API payload style)
    payload = [{"wound_id": wid, "patient_id": g["patient_id"].iloc[0],
                "readings": g[["timestamp"] + SENSOR_COLS].to_dict(orient="records")}
               for wid, g in inputs.groupby("wound_id")]
    with open(os.path.join(OUT, "demo_readings.json"), "w") as f:
        json.dump(payload, f, indent=1)
    with open(os.path.join(OUT, "example_request.json"), "w") as f:
        ex = dict(payload[1])
        ex["readings"] = ex["readings"][:6]
        json.dump(ex, f, indent=2)

    # answer key
    key = df[["wound_id", "timestamp", "hour", "label", "artifact", "outcome", "infection_onset_h"]]
    key.to_csv(os.path.join(OUT, "answer_key.csv"), index=False)

    # score the held-out set
    feat_df = add_features(df.assign(wound_id=df["wound_id"]), STEP_MIN / 60)
    feat_df = feat_df[feat_df["hour"] >= 24].reset_index(drop=True)
    pred = clf.predict(feat_df[feats].fillna(0).values)
    proba = clf.predict_proba(feat_df[feats].fillna(0).values)
    p_inf = proba[:, list(clf.classes_).index("infection")] + proba[:, list(clf.classes_).index("warning")]
    feat_df["predicted"] = pred
    feat_df["p_infected"] = p_inf.round(3)
    feat_df[["wound_id", "timestamp", "hour", "label", "predicted", "p_infected"]].to_csv(
        os.path.join(OUT, "model_predictions.csv"), index=False)

    al = wound_alarms(feat_df, pred, STEP_MIN / 60)
    acc = (feat_df["label"] == feat_df["predicted"]).mean()
    rows = []
    for wid, g in feat_df.groupby("wound_id"):
        need = int(4 / (STEP_MIN / 60))
        run = pd.Series(np.isin(g["predicted"], ["warning", "infection"])).rolling(need).sum() >= need
        alarm = g["hour"].values[run.values].min() if run.any() else np.nan
        onset = g["infection_onset_h"].iloc[0]
        name, desc = scen.get(wid, ("random", ""))
        rows.append({"wound_id": wid, "scenario": name, "patient_id": "P" + str(g["participant_id"].iloc[0]),
                     "true_outcome": g["outcome"].iloc[0],
                     "infection_onset_day": None if pd.isna(onset) else round(onset / 24, 2),
                     "model_alarm_day": None if pd.isna(alarm) else round(alarm / 24, 2),
                     "hours_onset_to_alarm": None if (pd.isna(alarm) or pd.isna(onset)) else round(alarm - onset, 1),
                     "description": desc})
    summ = pd.DataFrame(rows)
    summ.to_csv(os.path.join(OUT, "wound_scenarios.csv"), index=False)

    print(f"model trained on {n_train} wounds; demo = {df.wound_id.nunique()} unseen wounds, {len(df):,} readings")
    print(f"per-reading accuracy {acc:.3f}")
    print({k: round(float(v), 3) for k, v in al.items()})
    print(summ.drop(columns="description").to_string(index=False))


if __name__ == "__main__":
    main()
