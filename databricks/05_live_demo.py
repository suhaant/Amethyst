# Databricks notebook source
# MAGIC %md
# MAGIC # 05 · Live demo — replay one wound as if the patch were streaming
# MAGIC
# MAGIC Appends DEMO-02's readings into `live_readings_bronze` a few hours at a time and re-scores
# MAGIC after each batch, so you can watch the risk score climb when the infection starts (~day 3.2).
# MAGIC Point the dashboard at `live_risk_gold` and refresh while this runs.

# COMMAND ----------

# MAGIC %pip install xgboost --upgrade mlflow
# MAGIC %restart_python

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
dbutils.widgets.text("schema", "wolfhacks", "Schema")
dbutils.widgets.text("model_name", "wound_infection_risk", "Model name")
dbutils.widgets.text("wound_id", "DEMO-02", "Wound to replay")
dbutils.widgets.text("hours_per_step", "6", "Hours of readings per step")
dbutils.widgets.text("seconds_between_steps", "3", "Pause between steps (s)")
CATALOG, SCHEMA = dbutils.widgets.get("catalog"), dbutils.widgets.get("schema")
FQ = f"{CATALOG}.{SCHEMA}"
UC_MODEL = f"{FQ}.{dbutils.widgets.get('model_name')}"
WOUND = dbutils.widgets.get("wound_id")
STEP = int(dbutils.widgets.get("hours_per_step")) * 2          # readings every 30 min
PAUSE = float(dbutils.widgets.get("seconds_between_steps"))

import time

import mlflow
import pandas as pd

mlflow.set_registry_uri("databricks-uc")
model = mlflow.pyfunc.load_model(f"models:/{UC_MODEL}@champion")

cols = ["wound_id", "timestamp", "ph", "temp_c", "impedance_kohm", "blood_glucose_mgdl", "wound_glucose_mM"]
wound = spark.table(f"{FQ}.demo_readings_bronze").where(f"wound_id = '{WOUND}'") \
    .orderBy("timestamp").select(*cols).toPandas()
wound["timestamp"] = wound["timestamp"].astype(str)
spark.sql(f"DROP TABLE IF EXISTS {FQ}.live_readings_bronze")
spark.sql(f"DROP TABLE IF EXISTS {FQ}.live_risk_gold")

# COMMAND ----------

for end in range(STEP, len(wound) + STEP, STEP):
    batch = wound.iloc[end - STEP:end]
    spark.createDataFrame(batch).write.mode("append").saveAsTable(f"{FQ}.live_readings_bronze")
    history = wound.iloc[:end]
    hours = (pd.to_datetime(history.timestamp.iloc[-1]) - pd.to_datetime(history.timestamp.iloc[0])).total_seconds() / 3600
    if hours <= 24:
        print(f"hour {hours:5.1f}: learning baseline...")
    else:
        risk = model.predict(history)
        spark.createDataFrame(risk).write.mode("overwrite").option("overwriteSchema", "true") \
            .saveAsTable(f"{FQ}.live_risk_gold")
        last = risk.iloc[-1]
        bar = "#" * int(last.risk_score / 5)
        print(f"hour {last.hour:5.1f}  risk {last.risk_score:5.1f}  {last.tier_name:<12} {bar}")
    time.sleep(PAUSE)
