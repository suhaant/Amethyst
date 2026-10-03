"""
Full training run.

1. Leave-one-person-out CV (16 folds, one real glucose participant held
   out each time) with all 5 sensors -> main results, per-person results.
2. Sensor ablation with 4-fold person-grouped CV -> which sensors matter.
3. Probability calibration (isotonic, person-grouped folds) -> does a
   risk of 70 mean ~70%?
4. Final calibrated model trained on all data -> models/final_model.joblib
5. Score the unseen demo set with the final model.

Usage:
    python train_final.py
"""

import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import brier_score_loss, classification_report, roc_auc_score
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut

from train_model import add_features, feature_cols, wound_alarms

ALL = ["ph", "temp_c", "log_z", "blood_glucose_mgdl", "wound_glucose_mM"]
ABLATIONS = {
    "pH only": ["ph"],
    "temperature only": ["temp_c"],
    "moisture only": ["log_z"],
    "blood glucose only": ["blood_glucose_mgdl"],
    "wound glucose only": ["wound_glucose_mM"],
    "pH + temp + moisture": ["ph", "temp_c", "log_z"],
    "all 5 sensors": ALL,
}
LABELS = ["normal", "warning", "infection"]


def rf(seed=0):
    return RandomForestClassifier(n_estimators=150, max_depth=14, min_samples_leaf=20,
                                  n_jobs=-1, random_state=seed)


def p_infected(model, X):
    pr = model.predict_proba(X)
    c = list(model.classes_)
    return np.clip(pr[:, c.index("warning")] + pr[:, c.index("infection")], 0, 1)


def run_cv(X, y, groups, splitter):
    pred = np.empty(len(y), dtype=object)
    prob = np.zeros(len(y))
    for k, (tr, te) in enumerate(splitter.split(X, y, groups)):
        m = rf(k).fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
        prob[te] = p_infected(m, X[te])
    return pred, prob


def calib_table(prob, truth, bins=(0, .1, .3, .5, .7, .9, 1.0001)):
    d = pd.DataFrame({"p": prob, "t": truth})
    d["bin"] = pd.cut(d["p"], bins, right=False)
    t = d.groupby("bin", observed=True).agg(readings=("t", "size"), mean_predicted=("p", "mean"),
                                            actually_infected=("t", "mean"))
    return t.round(3)


def main():
    os.makedirs("models", exist_ok=True)
    df = pd.read_csv("data/wound_timeseries.csv")
    step_h = df["hour"].iloc[1] - df["hour"].iloc[0]
    df = add_features(df, step_h)
    df = df[df["hour"] >= 24].reset_index(drop=True)
    y = df["label"].values
    truth = (y != "normal").astype(int)
    groups = df["participant_id"].values
    feats = feature_cols(ALL)
    X = df[feats].fillna(0).values
    res = {"rows": int(len(df)), "wounds": int(df.wound_id.nunique()),
           "people": int(len(np.unique(groups)))}
    print(f"{res['rows']:,} readings, {res['wounds']} wounds, {res['people']} people\n")

    # ---- 1. leave-one-person-out -----------------------------------------
    print("1) leave-one-person-out CV (16 folds)...")
    pred, prob = run_cv(X, y, groups, LeaveOneGroupOut())
    rep = classification_report(y, pred, labels=LABELS, output_dict=True, zero_division=0)
    al = wound_alarms(df, pred, step_h)
    res["lopo"] = {"auc": roc_auc_score(truth, prob), "brier": brier_score_loss(truth, prob),
                   "accuracy": rep["accuracy"], **{f"{l}_recall": rep[l]["recall"] for l in LABELS},
                   **{f"{l}_precision": rep[l]["precision"] for l in LABELS}, **al}
    print(classification_report(y, pred, labels=LABELS, digits=3, zero_division=0))
    print({k: round(float(v), 3) for k, v in res["lopo"].items()})

    per = []
    for pid in np.unique(groups):
        m = groups == pid
        a = wound_alarms(df[m].reset_index(drop=True), pred[m], step_h)
        per.append({"participant": int(pid), "auc": roc_auc_score(truth[m], prob[m]), **a})
    per = pd.DataFrame(per).round(3)
    per.to_csv("models/per_person_results.csv", index=False)
    print("\nper person:\n", per.to_string(index=False))

    # ---- 2. ablation --------------------------------------------------------
    print("\n2) sensor ablation (4-fold person-grouped)...")
    abl = []
    for name, chans in ABLATIONS.items():
        Xa = df[feature_cols(chans)].fillna(0).values
        pa, qa = run_cv(Xa, y, groups, GroupKFold(n_splits=4))
        a = wound_alarms(df, pa, step_h)
        abl.append({"sensors": name, "auc": roc_auc_score(truth, qa), **a})
        print(f"   {name:<22} AUC {abl[-1]['auc']:.3f}  detected {a['detected']:.0%}  "
              f"false alarm {a['false_alarm_clean']:.1%}  median h {a['median_h_to_alarm']:.1f}")
    abl = pd.DataFrame(abl).round(3)
    abl.to_csv("models/sensor_ablation.csv", index=False)

    # ---- 3. calibration ----------------------------------------------------
    print("\n3) calibration...")
    raw_tab = calib_table(prob, truth)
    splits = list(GroupKFold(n_splits=4).split(X, y, groups))
    cprob = np.zeros(len(y))
    for k, (tr, te) in enumerate(splits):
        inner = list(GroupKFold(n_splits=3).split(X[tr], y[tr], groups[tr]))
        cm = CalibratedClassifierCV(rf(k), method="isotonic", cv=inner).fit(X[tr], y[tr])
        cprob[te] = p_infected(cm, X[te])
    cal_tab = calib_table(cprob, truth)
    res["calibration"] = {"brier_raw": brier_score_loss(truth, prob),
                          "brier_calibrated": brier_score_loss(truth, cprob)}
    print("raw:\n", raw_tab, "\ncalibrated:\n", cal_tab)
    pd.concat({"raw": raw_tab, "calibrated": cal_tab}).to_csv("models/calibration.csv")

    # ---- 4. final model --------------------------------------------------------
    print("\n4) final calibrated model on all data...")
    final = CalibratedClassifierCV(rf(0), method="isotonic",
                                   cv=list(GroupKFold(n_splits=4).split(X, y, groups))).fit(X, y)
    plain = rf(0).fit(X, y)
    imp = pd.Series(plain.feature_importances_, index=feats).sort_values(ascending=False).round(4)
    imp.to_csv("models/feature_importance.csv", header=["importance"])
    joblib.dump({"model": final, "features": feats, "step_min": int(step_h * 60),
                 "classes": list(final.classes_)}, "models/final_model.joblib")

    # ---- 5. unseen demo set -----------------------------------------------
    demo = pd.read_csv("demo_dataset/demo_readings.csv").merge(
        pd.read_csv("demo_dataset/answer_key.csv")[["wound_id", "hour", "label", "outcome", "infection_onset_h"]],
        on=["wound_id", "hour"])
    demo["participant_id"] = demo["patient_id"].str[1:].astype(int)
    demo = add_features(demo, step_h)
    demo = demo[demo["hour"] >= 24].reset_index(drop=True)
    Xd = demo[feats].fillna(0).values
    dp = final.predict(Xd)
    dq = p_infected(final, Xd)
    dt = (demo["label"] != "normal").astype(int).values
    res["demo"] = {"auc": roc_auc_score(dt, dq), **wound_alarms(demo, dp, step_h)}
    print("demo:", {k: round(float(v), 3) for k, v in res["demo"].items()})

    res["top_features"] = imp.head(10).to_dict()
    with open("models/results.json", "w") as f:
        json.dump(res, f, indent=2, default=float)
    print("\ntop features:\n", imp.head(10).to_string())


if __name__ == "__main__":
    main()
