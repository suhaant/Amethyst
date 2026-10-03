"""
Random forest vs XGBoost, same features, same leave-one-person-out CV
(16 folds), then both scored on the unseen demo set.

Usage:
    python compare_models.py
"""

import os
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import brier_score_loss, classification_report, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from xgboost import XGBClassifier

from train_model import add_features, feature_cols, wound_alarms

ALL = ["ph", "temp_c", "log_z", "blood_glucose_mgdl", "wound_glucose_mM"]
LABELS = ["normal", "warning", "infection"]
ENC = {l: i for i, l in enumerate(LABELS)}

MODELS = {
    "Random forest": lambda s: RandomForestClassifier(
        n_estimators=150, max_depth=14, min_samples_leaf=20, n_jobs=-1, random_state=s),
    "XGBoost": lambda s: XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8,
        min_child_weight=5, objective="multi:softprob", tree_method="hist", n_jobs=-1,
        random_state=s, verbosity=0),
}


def infected_prob(m, X):
    pr = m.predict_proba(X)
    return np.clip(pr[:, ENC["warning"]] + pr[:, ENC["infection"]], 0, 1)


def predict_labels(m, X):
    return np.array(LABELS)[m.predict_proba(X).argmax(1)]


def main():
    df = pd.read_csv("data/wound_timeseries.csv")
    step_h = df["hour"].iloc[1] - df["hour"].iloc[0]
    df = add_features(df, step_h)
    df = df[df["hour"] >= 24].reset_index(drop=True)
    feats = feature_cols(ALL)
    X = df[feats].fillna(0).values
    y = df["label"].map(ENC).values          # same integer labels for both models
    ylab = df["label"].values
    truth = (ylab != "normal").astype(int)
    groups = df["participant_id"].values

    demo = pd.read_csv("demo_dataset/demo_readings.csv").merge(
        pd.read_csv("demo_dataset/answer_key.csv")[["wound_id", "hour", "label", "outcome", "infection_onset_h"]],
        on=["wound_id", "hour"])
    demo["participant_id"] = demo["patient_id"].str[1:].astype(int)
    demo = add_features(demo, step_h)
    demo = demo[demo["hour"] >= 24].reset_index(drop=True)
    Xd = demo[feats].fillna(0).values
    dtruth = (demo["label"] != "normal").astype(int).values

    rows, imps = [], {}
    for name, make in MODELS.items():
        print(f"\n=== {name}: leave-one-person-out (16 folds) ===")
        pred = np.empty(len(y), dtype=object)
        prob = np.zeros(len(y))
        fit_s = 0.0
        for k, (tr, te) in enumerate(LeaveOneGroupOut().split(X, y, groups)):
            m = make(k)
            t0 = time.time()
            m.fit(X[tr], y[tr])
            fit_s += time.time() - t0
            pred[te] = predict_labels(m, X[te])
            prob[te] = infected_prob(m, X[te])
        rep = classification_report(ylab, pred, labels=LABELS, output_dict=True, zero_division=0)
        print(classification_report(ylab, pred, labels=LABELS, digits=3, zero_division=0))
        al = wound_alarms(df, pred, step_h)

        # final model on all data -> unseen demo set (demo people 14-16 are in
        # the training glucose pool, but every demo wound is new)
        final = make(0).fit(X, y)
        os.makedirs("models", exist_ok=True)
        joblib.dump({"model": final, "features": feats, "labels": LABELS},
                    f"models/{name.lower().replace(' ', '_')}.joblib")
        size_mb = os.path.getsize(f"models/{name.lower().replace(' ', '_')}.joblib") / 1e6
        dpred = predict_labels(final, Xd)
        dal = wound_alarms(demo, dpred, step_h)
        t0 = time.time()
        for _ in range(20):
            final.predict_proba(Xd[:1])
        lat_ms = (time.time() - t0) / 20 * 1000

        imps[name] = pd.Series(final.feature_importances_, index=feats)
        rows.append({
            "model": name,
            "AUC (infected vs not)": roc_auc_score(truth, prob),
            "Brier (lower=better)": brier_score_loss(truth, prob),
            "accuracy": rep["accuracy"],
            "warning recall": rep["warning"]["recall"],
            "infection recall": rep["infection"]["recall"],
            "infection precision": rep["infection"]["precision"],
            "wounds detected": al["detected"],
            "median h onset->alarm": al["median_h_to_alarm"],
            "alarm before onset": al["alarm_before_onset"],
            "false alarm clean wounds": al["false_alarm_clean"],
            "demo AUC": roc_auc_score(dtruth, infected_prob(final, Xd)),
            "demo detected": dal["detected"],
            "demo false alarm": dal["false_alarm_clean"],
            "demo median h": dal["median_h_to_alarm"],
            "train time 16 folds (s)": fit_s,
            "model size (MB)": size_mb,
            "1 prediction (ms)": lat_ms,
        })

    res = pd.DataFrame(rows).set_index("model").T
    res.to_csv("models/rf_vs_xgboost.csv")
    print("\n=== Random forest vs XGBoost ===")
    print(res.round(3).to_string())

    imp = pd.DataFrame(imps)
    imp = imp / imp.sum()
    imp.sort_values("XGBoost", ascending=False).round(3).to_csv("models/rf_vs_xgboost_importance.csv")
    print("\n=== Top features (share of importance) ===")
    print(imp.sort_values("XGBoost", ascending=False).head(10).round(3).to_string())


if __name__ == "__main__":
    main()
