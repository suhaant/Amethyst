# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Batch scoring → Gold tables
# MAGIC
# MAGIC Loads `@champion`, scores every wound in a readings table, and writes:
# MAGIC
# MAGIC | Table | Contents |
# MAGIC |---|---|
# MAGIC | `risk_scores_gold` | per reading: `p_infected`, `risk_score`, `tier` |
# MAGIC | `treatment_plan_gold` | per wound: latest risk + next LED / ultrasound session |
# MAGIC
# MAGIC Schedule this as a Job every 30 min (see `databricks/README.md`) so new patch readings are
# MAGIC scored automatically. Dashboard queries: `dashboard_queries.sql`.

# COMMAND ----------

# MAGIC %pip install xgboost --upgrade mlflow
# MAGIC %restart_python

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
dbutils.widgets.text("schema", "wolfhacks", "Schema")
dbutils.widgets.text("model_name", "wound_infection_risk", "Model name")
dbutils.widgets.text("source_table", "demo_readings_bronze", "Readings table to score")
CATALOG, SCHEMA = dbutils.widgets.get("catalog"), dbutils.widgets.get("schema")
FQ = f"{CATALOG}.{SCHEMA}"
UC_MODEL = f"{FQ}.{dbutils.widgets.get('model_name')}"
SOURCE = f"{FQ}.{dbutils.widgets.get('source_table')}"

import os
import sys

REPO = os.path.dirname(os.getcwd())
sys.path.insert(0, REPO)

import mlflow
import pandas as pd

from risk_to_dose import session_plan

mlflow.set_registry_uri("databricks-uc")
model = mlflow.pyfunc.load_model(f"models:/{UC_MODEL}@champion")

cols = ["wound_id", "timestamp", "ph", "temp_c", "impedance_kohm", "blood_glucose_mgdl", "wound_glucose_mM"]
readings = spark.table(SOURCE).select(*cols).toPandas()
readings["timestamp"] = readings["timestamp"].astype(str)

# wounds with < 24 h of data can't be scored yet (baseline still forming)
hours = readings.groupby("wound_id")["timestamp"].agg(
    lambda s: (pd.to_datetime(s).max() - pd.to_datetime(s).min()).total_seconds() / 3600)
ready = hours[hours > 24].index
print(f"{len(ready)} of {len(hours)} wounds have > 24 h of readings")

scores = model.predict(readings[readings.wound_id.isin(ready)])
scores["scored_at"] = pd.Timestamp.utcnow()
spark.createDataFrame(scores).write.mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{FQ}.risk_scores_gold")

# COMMAND ----------

last = scores.sort_values("hour").groupby("wound_id").tail(1)
latest_z = readings.sort_values("timestamp").groupby("wound_id").tail(1).set_index("wound_id")["impedance_kohm"]
plans = []
for _, r in last.iterrows():
    plan = session_plan(r["risk_score"], int(r["tier"]))
    if latest_z.get(r["wound_id"], 0) > 150:             # patch lifted -> never fire LED / ultrasound
        plan = {k: (0 if isinstance(v, (int, float)) else "SKIPPED: patch not on skin") for k, v in plan.items()}
    plans.append({"wound_id": r["wound_id"], "timestamp": r["timestamp"], "risk_score": r["risk_score"],
                  "tier": r["tier_name"], **plan})
plans = pd.DataFrame(plans)
spark.createDataFrame(plans).write.mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{FQ}.treatment_plan_gold")
display(plans.sort_values("risk_score", ascending=False))
