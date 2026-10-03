"""
Train a random forest on the synthetic patch data with trend features.

Validation is leave-people-out: GroupKFold on participant_id, so every
wound built from one real person's glucose trace is either all in train
or all in test. Scores therefore show how the model does on people it
has never seen.

Compares three sensor sets:
    patch            pH + temperature + impedance
    patch+cgm        + blood glucose (Dexcom-style CGM)
    patch+cgm+wound  + wound-fluid glucose

Usage:
    python train_model.py --data data/wound_timeseries.csv
"""

import argparse

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GroupKFold

CHANNELS = {
    "patch": ["ph", "temp_c", "log_z"],
    "patch+cgm": ["ph", "temp_c", "log_z", "blood_glucose_mgdl"],
    "patch+cgm+wound": ["ph", "temp_c", "log_z", "blood_glucose_mgdl", "wound_glucose_mM"],
}
LABELS = ["normal", "warning", "infection"]


def add_features(df, step_h):
    """Past-only features per wound, so the model never sees the future."""
    out = []
    w6, w24 = int(6 / step_h), int(24 / step_h)
    for _, g in df.groupby("wound_id", sort=False):
        g = g.sort_values("hour").copy()
        g["log_z"] = np.log(g["impedance_kohm"])
        for c in CHANNELS["patch+cgm+wound"]:
            s = g[c]
            # median filter knocks out shower / dressing spikes
            sm = s.rolling(w6, min_periods=1).median()
            base = sm.iloc[:w24].median()              # personal baseline, day 1
            g[f"{c}_sm"] = sm
            g[f"{c}_vs_base"] = sm - base
            g[f"{c}_d6h"] = sm - sm.shift(w6)
            g[f"{c}_d24h"] = sm - sm.shift(w24)
            g[f"{c}_std24h"] = s.rolling(w24, min_periods=2).std()
        g["tod_sin"] = np.sin(2 * np.pi * g["hour"] / 24)
        g["tod_cos"] = np.cos(2 * np.pi * g["hour"] / 24)
        out.append(g)
    return pd.concat(out, ignore_index=True)


def feature_cols(channels):
    f = [f"{c}_{k}" for c in channels for k in ["sm", "vs_base", "d6h", "d24h", "std24h"]]
    return f + ["tod_sin", "tod_cos"]


def wound_alarms(df, pred, step_h):
    """Alarm = 4 h of consecutive warning/infection predictions."""
    d = df[["wound_id", "hour", "outcome", "infection_onset_h"]].copy()
    d["hit"] = pd.Series(pred).isin(["warning", "infection"]).astype(int).values
    need = int(4 / step_h)
    rows = []
    for _, g in d.groupby("wound_id"):
        run = g["hit"].rolling(need).sum() >= need
        rows.append((g["outcome"].iloc[0], g["infection_onset_h"].iloc[0],
                     g.loc[run, "hour"].min() if run.any() else np.nan))
    w = pd.DataFrame(rows, columns=["outcome", "onset", "alarm"])
    inf, clean = w[w.outcome == "infected"], w[w.outcome != "infected"]
    lead = inf["alarm"] - inf["onset"]
    return {
        "detected": inf["alarm"].notna().mean(),
        "median_h_to_alarm": lead.median(),
        "alarm_before_onset": (lead < 0).mean(),
        "false_alarm_clean": clean["alarm"].notna().mean(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/wound_timeseries.csv")
    a = ap.parse_args()

    df = pd.read_csv(a.data)
    step_h = df["hour"].iloc[1] - df["hour"].iloc[0]
    df = add_features(df, step_h)
    df = df[df["hour"] >= 24].reset_index(drop=True)   # need day-1 baseline
    y = df["label"].values
    groups = df["participant_id"].values
    n_people = len(np.unique(groups))
    print(f"{df.wound_id.nunique()} wounds from {n_people} real glucose participants; "
          f"leave-people-out 4-fold CV\n")

    summary = []
    for name, chans in CHANNELS.items():
        feats = feature_cols(chans)
        X = df[feats].fillna(0).values
        pred = np.empty(len(y), dtype=object)
        for k, (tr, te) in enumerate(GroupKFold(n_splits=4).split(X, y, groups)):
            clf = RandomForestClassifier(n_estimators=150, max_depth=14, min_samples_leaf=20,
                                         n_jobs=-1, random_state=k)
            clf.fit(X[tr], y[tr])
            pred[te] = clf.predict(X[te])
        rep = classification_report(y, pred, labels=LABELS, output_dict=True, zero_division=0)
        al = wound_alarms(df, pred, step_h)
        summary.append({"sensors": name,
                        "warning_recall": rep["warning"]["recall"],
                        "infection_recall": rep["infection"]["recall"],
                        "infection_precision": rep["infection"]["precision"],
                        "macro_f1": rep["macro avg"]["f1-score"], **al})
        print(f"=== {name} ===")
        print(classification_report(y, pred, labels=LABELS, digits=3, zero_division=0))
        print("confusion (rows=true, cols=pred):", LABELS)
        print(confusion_matrix(y, pred, labels=LABELS))
        print({k: round(v, 3) for k, v in al.items()}, "\n")

    s = pd.DataFrame(summary)
    s.to_csv("data/model_comparison.csv", index=False)
    print("=== Comparison ===")
    print(s.round(3).to_string(index=False))

    clf.fit(X, y)   # last (full) sensor set, all data
    imp = pd.Series(clf.feature_importances_, index=feats).sort_values(ascending=False)
    imp.to_csv("data/feature_importance.csv", header=["importance"])
    print("\n=== Top 12 features (all sensors) ===")
    print(imp.head(12).round(3).to_string())


if __name__ == "__main__":
    main()
