# Databricks notebook source
# MAGIC %md
# MAGIC # 03 · Model Serving endpoint
# MAGIC
# MAGIC Deploys the `@champion` version as a REST endpoint (scale-to-zero) and sends it one demo
# MAGIC wound. Callers send **raw readings for a wound's full history**; the endpoint returns
# MAGIC `p_infected`, `risk_score` (0-100) and `tier` per reading.
# MAGIC
# MAGIC If your workspace doesn't include Model Serving (check on Free Edition), skip this notebook and
# MAGIC use `04_batch_score` instead.

# COMMAND ----------

# MAGIC %pip install --upgrade databricks-sdk mlflow
# MAGIC %restart_python

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
dbutils.widgets.text("schema", "wolfhacks", "Schema")
dbutils.widgets.text("model_name", "wound_infection_risk", "Model name")
dbutils.widgets.text("endpoint", "wound-infection-risk", "Endpoint name")
CATALOG, SCHEMA = dbutils.widgets.get("catalog"), dbutils.widgets.get("schema")
FQ = f"{CATALOG}.{SCHEMA}"
UC_MODEL = f"{FQ}.{dbutils.widgets.get('model_name')}"
ENDPOINT = dbutils.widgets.get("endpoint")

import datetime

import mlflow
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedEntityInput
from mlflow import MlflowClient

mlflow.set_registry_uri("databricks-uc")
version = MlflowClient().get_model_version_by_alias(UC_MODEL, "champion").version
print(f"serving {UC_MODEL} v{version}")

w = WorkspaceClient()
config = EndpointCoreConfigInput(served_entities=[ServedEntityInput(
    entity_name=UC_MODEL, entity_version=str(version),
    workload_size="Small", scale_to_zero_enabled=True)])

existing = [e.name for e in w.serving_endpoints.list()]
if ENDPOINT in existing:
    w.serving_endpoints.update_config_and_wait(name=ENDPOINT, served_entities=config.served_entities,
                                               timeout=datetime.timedelta(minutes=40))
else:
    w.serving_endpoints.create_and_wait(name=ENDPOINT, config=config,
                                        timeout=datetime.timedelta(minutes=40))
print("endpoint ready:", ENDPOINT)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test: send DEMO-02's full history

# COMMAND ----------

import pandas as pd

wound = spark.table(f"{FQ}.demo_readings_bronze").where("wound_id = 'DEMO-02'").orderBy("timestamp").toPandas()
wound["timestamp"] = wound["timestamp"].astype(str)
cols = ["wound_id", "timestamp", "ph", "temp_c", "impedance_kohm", "blood_glucose_mgdl", "wound_glucose_mM"]

resp = w.serving_endpoints.query(name=ENDPOINT, dataframe_records=wound[cols].to_dict("records"))
result = pd.DataFrame(resp.predictions)
display(result.tail(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Calling it from your app (REST)
# MAGIC ```bash
# MAGIC curl -X POST "$DATABRICKS_HOST/serving-endpoints/wound-infection-risk/invocations" \
# MAGIC   -H "Authorization: Bearer $DATABRICKS_TOKEN" -H "Content-Type: application/json" \
# MAGIC   -d '{"dataframe_records": [{"wound_id": "DEMO-02", "timestamp": "2026-10-01T08:00:00",
# MAGIC        "ph": 7.1, "temp_c": 33.4, "impedance_kohm": 9.8, "blood_glucose_mgdl": 112,
# MAGIC        "wound_glucose_mM": 4.2}, ...]}'
# MAGIC ```
# MAGIC Send > 24 h of readings per wound; the response has one prediction per reading after hour 24.
