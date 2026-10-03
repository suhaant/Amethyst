# Databricks notebook source
# MAGIC %md
# MAGIC # 02 · Features + training with MLflow → Unity Catalog model
# MAGIC
# MAGIC 1. Bronze → **Silver** feature table (`features_silver`, 27 trend features per reading)
# MAGIC 2. **Leave-one-person-out** CV (16 folds) for XGBoost, logged to an MLflow experiment
# MAGIC 3. Demo check: model trained without participants 14-16, scored on the demo wounds
# MAGIC 4. Final model on all data, wrapped as a pyfunc (raw readings in → risk out) and
# MAGIC    **registered in Unity Catalog** with alias `champion`

# COMMAND ----------

# MAGIC %pip install xgboost databricks-sdk --upgrade mlflow
# MAGIC %restart_python

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
dbutils.widgets.text("schema", "wolfhacks", "Schema")
dbutils.widgets.text("model_name", "wound_infection_risk", "Model name")
CATALOG, SCHEMA = dbutils.widgets.get("catalog"), dbutils.widgets.get("schema")
FQ = f"{CATALOG}.{SCHEMA}"
UC_MODEL = f"{FQ}.{dbutils.widgets.get('model_name')}"

import os
import sys
import tempfile

REPO = os.path.dirname(os.getcwd())
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "databricks"))

import mlflow
import numpy as np
import pandas as pd
from mlflow import MlflowClient
from sklearn.metrics import brier_score_loss, classification_report, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from xgboost import XGBClassifier

from train_model import add_features, feature_cols, wound_alarms
from wound_risk_pyfunc import export_xgb, log_pyfunc

mlflow.set_registry_uri("databricks-uc")
user = spark.sql("SELECT current_user()").first()[0]
mlflow.set_experiment(f"/Users/{user}/wolfhacks_wound_infection")

LABELS = ["normal", "warning", "infection"]
ENC = {l: i for i, l in enumerate(LABELS)}
STEP_H = 0.5
FEATS = feature_cols(["ph", "temp_c", "log_z", "blood_glucose_mgdl", "wound_glucose_mM"])
PARAMS = dict(n_estimators=300, max_depth=6, learning_rate=0.1, subsample=0.8,
              colsample_bytree=0.8, min_child_weight=5, objective="multi:softprob",
              tree_method="hist")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver: trend features

# COMMAND ----------

bronze = spark.table(f"{FQ}.readings_bronze").toPandas()
feat = add_features(bronze, STEP_H)
feat = feat[feat["hour"] >= 24].reset_index(drop=True)      # first 24 h = baseline
spark.createDataFrame(feat[["wound_id", "participant_id", "timestamp", "hour", "label", "outcome",
                            "infection_onset_h"] + FEATS]) \
    .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{FQ}.features_silver")
print(f"{len(feat):,} feature rows, {feat.wound_id.nunique()} wounds")

X = feat[FEATS].fillna(0).values
y = feat["label"].map(ENC).values
truth = (y > 0).astype(int)
groups = feat["participant_id"].values

def xgb(seed):
    return XGBClassifier(**PARAMS, n_jobs=-1, random_state=seed, verbosity=0)

def p_inf(m, X):
    pr = m.predict_proba(X)
    return np.clip(pr[:, 1] + pr[:, 2], 0, 1)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Leave-one-person-out CV, logged to MLflow

# COMMAND ----------

with mlflow.start_run(run_name="xgb_leave_one_person_out") as run:
    mlflow.log_params({**PARAMS, "features": len(FEATS), "cv": "LeaveOneGroupOut(participant)",
                       "wounds": feat.wound_id.nunique(), "readings": len(feat)})
    pred = np.empty(len(y), dtype=object)
    prob = np.zeros(len(y))
    for k, (tr, te) in enumerate(LeaveOneGroupOut().split(X, y, groups)):
        m = xgb(k).fit(X[tr], y[tr])
        prob[te] = p_inf(m, X[te])
        pred[te] = np.array(LABELS)[m.predict_proba(X[te]).argmax(1)]
        mlflow.log_metric("fold_auc", roc_auc_score(truth[te], prob[te]), step=k)

    rep = classification_report(feat["label"], pred, labels=LABELS, output_dict=True, zero_division=0)
    al = wound_alarms(feat, pred, STEP_H)
    base = truth.mean()
    metrics = {
        "auc": roc_auc_score(truth, prob),
        "brier_skill_r2": 1 - brier_score_loss(truth, prob) / (base * (1 - base)),
        "accuracy": rep["accuracy"],
        "f1_infection": rep["infection"]["f1-score"],
        "f1_warning": rep["warning"]["f1-score"],
        "recall_warning": rep["warning"]["recall"],
        "wounds_detected": al["detected"],
        "median_hours_to_alarm": al["median_h_to_alarm"],
        "false_alarm_clean": al["false_alarm_clean"],
    }
    mlflow.log_metrics(metrics)
    cv_run_id = run.info.run_id
pd.Series(metrics).round(3)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Demo check: train without participants 14-16, score held-out demo wounds

# COMMAND ----------

HOLDOUT = [14, 15, 16]
m_demo = xgb(0).fit(X[~np.isin(groups, HOLDOUT)], y[~np.isin(groups, HOLDOUT)])

demo = spark.table(f"{FQ}.demo_readings_bronze").toPandas().merge(
    spark.table(f"{FQ}.demo_answer_key").toPandas()[["wound_id", "timestamp", "hour", "label",
                                                      "outcome", "infection_onset_h"]],
    on=["wound_id", "timestamp"])
demo["participant_id"] = demo["patient_id"].str[1:].astype(int)
dfeat = add_features(demo, STEP_H)
dfeat = dfeat[dfeat["hour"] >= 24].reset_index(drop=True)
Xd = dfeat[FEATS].fillna(0).values
dpred = np.array(LABELS)[m_demo.predict_proba(Xd).argmax(1)]
dal = wound_alarms(dfeat, dpred, STEP_H)
with mlflow.start_run(run_id=cv_run_id):
    mlflow.log_metrics({"demo_auc": roc_auc_score((dfeat.label != "normal").astype(int), p_inf(m_demo, Xd)),
                        "demo_detected": dal["detected"], "demo_false_alarm": dal["false_alarm_clean"],
                        "demo_median_hours_to_alarm": dal["median_h_to_alarm"]})
dal

# COMMAND ----------

# MAGIC %md
# MAGIC ## Final model → pyfunc → Unity Catalog (`champion`)

# COMMAND ----------

final = xgb(0).fit(X, y)
model_dir = export_xgb(final, FEATS, LABELS, step_min=30, out_dir=tempfile.mkdtemp(),
                       extra_meta={"cv_run_id": cv_run_id, **{k: float(v) for k, v in metrics.items()}})

example_wound = bronze[bronze.wound_id == bronze.wound_id.iloc[0]][
    ["wound_id", "timestamp", "ph", "temp_c", "impedance_kohm", "blood_glucose_mgdl", "wound_glucose_mM"]]
example_wound = example_wound.assign(timestamp=example_wound["timestamp"].astype(str))

with mlflow.start_run(run_name="xgb_final_all_data"):
    mlflow.log_params(PARAMS)
    mlflow.log_metrics(metrics)
    info = log_pyfunc(model_dir, example_wound, registered_model_name=UC_MODEL)

client = MlflowClient()
version = info.registered_model_version
client.set_registered_model_alias(UC_MODEL, "champion", version)
print(f"registered {UC_MODEL} version {version} as @champion")
