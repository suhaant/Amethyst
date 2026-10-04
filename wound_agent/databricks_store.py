"""Databricks as the cloud record: patch readings go in, assessments come out.

Two tables in one schema (set up by `ensure_tables`, described in databricks/README.md):

  readings      one row per 30-minute patch reading
  assessments   one row per agent run, append-only

`DatabricksStore` implements the DataSource protocol from data_sources.py, so the agent,
the model and the dosing code read from Databricks without any changes.

All access goes through one injectable function, `execute(sql, params) -> list[dict]`.
The default talks to a SQL warehouse through the Databricks SDK; tests pass a fake.
"""

from __future__ import annotations

import math
import os
import re
import time
from datetime import datetime, timezone
from typing import Callable, Mapping, Optional

import pandas as pd

from .schemas import SENSOR_COLUMNS, Assessment

Execute = Callable[[str, dict], list]

SOURCES = ("simulated", "file", "patch")
REQUIRED_SETTINGS = ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_WAREHOUSE_ID")
DEFAULT_CATALOG = "workspace"
DEFAULT_SCHEMA = "pulsepatch"
INSERT_CHUNK = 500
WAREHOUSE_TIMEOUT_S = 120

_WOUND_ID = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
_NAME = re.compile(r"^[A-Za-z0-9_]+$")

# Column name -> SQL type, in table order.
ASSESSMENT_COLUMNS = {
    "wound_id": "STRING",
    "generated_at": "TIMESTAMP",
    "assessed_by": "STRING",
    "n_readings": "INT",
    "history_hours": "DOUBLE",
    "risk_score": "DOUBLE",
    "p_infected": "DOUBLE",
    "predicted_label": "STRING",
    "tier": "STRING",
    "risk_score_6h_ago": "DOUBLE",
    "risk_score_24h_ago": "DOUBLE",
    "led_dose_j_cm2": "DOUBLE",
    "led_405nm_min": "DOUBLE",
    "us_40khz_min": "DOUBLE",
    "us_1p5mhz_min": "DOUBLE",
    "skipped_reason": "STRING",
    "summary": "STRING",
    "trend": "STRING",
    "reasoning": "STRING",
    "data_quality_flags": "STRING",
    "conflicting_signals": "STRING",
    "recommend_clinician_review": "BOOLEAN",
    "confidence": "STRING",
    "caveats": "STRING",
    "assessment_json": "STRING",
}
_NOT_NULL = {"wound_id", "generated_at", "assessed_by"}


class DatabricksConfigError(RuntimeError):
    """A required Databricks setting is missing."""


def assessment_row(assessment: Assessment) -> dict:
    """Flatten an Assessment into the `assessments` columns."""
    notes = assessment.agent_notes
    pred = assessment.prediction
    plan = assessment.treatment
    return {
        "wound_id": assessment.wound_id,
        "generated_at": assessment.generated_at,
        "assessed_by": "opus-agent" if notes else "model-only",
        "n_readings": assessment.n_readings,
        "history_hours": assessment.history_hours,
        "risk_score": pred.risk_score,
        "p_infected": pred.p_infected,
        "predicted_label": pred.predicted_label,
        "tier": pred.tier,
        "risk_score_6h_ago": pred.risk_score_6h_ago,
        "risk_score_24h_ago": pred.risk_score_24h_ago,
        "led_dose_j_cm2": plan.led_dose_j_cm2,
        "led_405nm_min": plan.led_405nm_min,
        "us_40khz_min": plan.us_40khz_min,
        "us_1p5mhz_min": plan.us_1p5mhz_min,
        "skipped_reason": plan.skipped_reason,
        "summary": notes.summary if notes else None,
        "trend": notes.trend if notes else None,
        "reasoning": notes.reasoning if notes else None,
        "data_quality_flags": "; ".join(notes.data_quality_flags) if notes else None,
        "conflicting_signals": "; ".join(notes.conflicting_signals) if notes else None,
        "recommend_clinician_review": notes.recommend_clinician_review if notes else None,
        "confidence": notes.confidence if notes else None,
        "caveats": "; ".join(assessment.caveats),
        "assessment_json": assessment.model_dump_json(),
    }


def _param(value) -> Optional[str]:
    """Statement parameters travel as strings; the SQL casts each one to its column type."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        return _timestamp(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return str(value)


def _timestamp(value) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is not None:
        ts = ts.tz_convert("UTC").tz_localize(None)
    return ts.strftime("%Y-%m-%d %H:%M:%S.%f")


def _number(value) -> str:
    """A finite number as a SQL literal, anything else as NULL."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NULL"
    return repr(number) if math.isfinite(number) else "NULL"


def _check_wound_id(wound_id) -> str:
    wound_id = str(wound_id)
    if not _WOUND_ID.match(wound_id):
        raise ValueError(f"Invalid wound id {wound_id!r}: use letters, digits, '_', '.', '-' (64 max).")
    return wound_id


class DatabricksStore:
    """Moves readings and assessments between pandas and two Databricks tables."""

    def __init__(self, execute: Execute, catalog: str = DEFAULT_CATALOG, schema: str = DEFAULT_SCHEMA):
        for kind, name in (("catalog", catalog), ("schema", schema)):
            if not _NAME.match(name or ""):
                raise ValueError(f"Invalid Databricks {kind} name {name!r}: use letters, digits and '_'.")
        self._execute = execute
        self.catalog = catalog
        self.schema = schema
        self.is_dummy = False

    @classmethod
    def from_env(cls, env: Optional[Mapping[str, str]] = None) -> "DatabricksStore":
        env = os.environ if env is None else env
        missing = [name for name in REQUIRED_SETTINGS if not env.get(name)]
        if missing:
            raise DatabricksConfigError(
                f"Databricks is not configured: {', '.join(missing)} not set. Add to .env (see .env.example)."
            )
        execute = sdk_execute(env["DATABRICKS_HOST"], env["DATABRICKS_TOKEN"], env["DATABRICKS_WAREHOUSE_ID"])
        return cls(execute, env.get("DATABRICKS_CATALOG") or DEFAULT_CATALOG,
                   env.get("DATABRICKS_SCHEMA") or DEFAULT_SCHEMA)

    @property
    def readings(self) -> str:
        return f"{self.catalog}.{self.schema}.readings"

    @property
    def assessments(self) -> str:
        return f"{self.catalog}.{self.schema}.assessments"

    def ensure_tables(self) -> None:
        self._execute(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.{self.schema}", {})
        sensors = "".join(f"  {name} DOUBLE,\n" for name in SENSOR_COLUMNS)
        self._execute(
            f"CREATE TABLE IF NOT EXISTS {self.readings} (\n"
            "  wound_id STRING NOT NULL,\n"
            "  `timestamp` TIMESTAMP NOT NULL,\n"
            "  hour DOUBLE NOT NULL,\n"
            f"{sensors}"
            "  source STRING NOT NULL,\n"
            "  ingested_at TIMESTAMP NOT NULL\n)",
            {},
        )
        columns = ",\n".join(
            f"  {name} {sql_type}{' NOT NULL' if name in _NOT_NULL else ''}"
            for name, sql_type in ASSESSMENT_COLUMNS.items()
        )
        self._execute(f"CREATE TABLE IF NOT EXISTS {self.assessments} (\n{columns}\n)", {})

    def upload_readings(self, history: pd.DataFrame, source: str) -> int:
        """Replace the stored readings for the wounds in `history`. Returns the number of rows written."""
        if source not in SOURCES:
            raise ValueError(f"Unknown source {source!r}: expected one of {', '.join(SOURCES)}.")
        if "wound_id" not in history.columns or "hour" not in history.columns:
            raise ValueError("History needs `wound_id` and `hour` columns.")
        wound_ids = [_check_wound_id(w) for w in history["wound_id"].unique()]
        ingested = datetime.now(timezone.utc)
        if "timestamp" in history.columns:
            timestamps = pd.to_datetime(history["timestamp"], utc=True)
        else:   # no clock in the file: place the last reading at the upload time
            hours = history["hour"].astype(float)
            timestamps = pd.Timestamp(ingested) - pd.to_timedelta(hours.max() - hours, unit="h")

        rows = []
        for i, (_, reading) in enumerate(history.iterrows()):
            sensors = ", ".join(_number(reading.get(name)) for name in SENSOR_COLUMNS)
            rows.append(
                f"('{_check_wound_id(reading['wound_id'])}', TIMESTAMP '{_timestamp(timestamps.iloc[i])}', "
                f"{_number(reading['hour'])}, {sensors}, '{source}', TIMESTAMP '{_timestamp(ingested)}')"
            )

        for wound_id in wound_ids:
            self._execute(f"DELETE FROM {self.readings} WHERE wound_id = :wound_id", {"wound_id": wound_id})
        columns = ", ".join(["wound_id", "`timestamp`", "hour", *SENSOR_COLUMNS, "source", "ingested_at"])
        for start in range(0, len(rows), INSERT_CHUNK):
            values = ",\n".join(rows[start:start + INSERT_CHUNK])
            self._execute(f"INSERT INTO {self.readings} ({columns}) VALUES\n{values}", {})
        return len(rows)

    def list_wounds(self) -> list:
        rows = self._execute(f"SELECT DISTINCT wound_id FROM {self.readings} ORDER BY wound_id", {})
        return sorted(str(row["wound_id"]) for row in rows)

    def get_history(self, wound_id: str) -> pd.DataFrame:
        wound_id = _check_wound_id(wound_id)
        sensors = ", ".join(SENSOR_COLUMNS)
        rows = self._execute(
            f"SELECT wound_id, `timestamp`, hour, {sensors}, source FROM {self.readings} "
            "WHERE wound_id = :wound_id ORDER BY hour",
            {"wound_id": wound_id},
        )
        if not rows:
            raise ValueError(f"No readings for wound {wound_id!r} in Databricks table {self.readings}")
        df = pd.DataFrame(rows)
        self.is_dummy = bool((df["source"] == "simulated").any())
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        for name in ["hour", *SENSOR_COLUMNS]:
            df[name] = pd.to_numeric(df[name], errors="coerce")
        df["wound_id"] = df["wound_id"].astype(str)
        return df[["wound_id", "timestamp", "hour", *SENSOR_COLUMNS]].sort_values("hour").reset_index(drop=True)

    def save_assessment(self, assessment: Assessment) -> None:
        row = assessment_row(assessment)
        columns = ", ".join(ASSESSMENT_COLUMNS)
        values = ", ".join(f"CAST(:{name} AS {sql_type})" for name, sql_type in ASSESSMENT_COLUMNS.items())
        self._execute(
            f"INSERT INTO {self.assessments} ({columns}) VALUES ({values})",
            {name: _param(row[name]) for name in ASSESSMENT_COLUMNS},
        )


def sdk_execute(host: str, token: str, warehouse_id: str, timeout_s: int = WAREHOUSE_TIMEOUT_S) -> Execute:
    """The real `execute`: runs one statement on a SQL warehouse and returns its rows as dicts of strings."""
    client = None

    def execute(sql: str, params: dict) -> list:
        nonlocal client
        from databricks.sdk import WorkspaceClient   # only needed when --databricks is used
        from databricks.sdk.service.sql import StatementParameterListItem, StatementState

        if client is None:
            client = WorkspaceClient(host=host, token=token)
        api = client.statement_execution
        response = api.execute_statement(
            statement=sql,
            warehouse_id=warehouse_id,
            parameters=[StatementParameterListItem(name=name, value=value) for name, value in params.items()],
            wait_timeout="30s",
        )
        deadline = time.monotonic() + timeout_s
        while response.status.state in (StatementState.PENDING, StatementState.RUNNING):
            if time.monotonic() > deadline:
                raise TimeoutError(
                    f"Databricks did not finish the statement within {timeout_s} s. Is the SQL warehouse starting?"
                )
            time.sleep(2)
            response = api.get_statement(response.statement_id)
        if response.status.state != StatementState.SUCCEEDED:
            error = response.status.error
            raise RuntimeError(f"Databricks statement failed: {error.message if error else response.status.state}")

        schema = response.manifest.schema if response.manifest else None
        names = [column.name for column in (schema.columns or [])] if schema else []
        chunk = response.result
        rows = []
        while chunk is not None:
            rows.extend(chunk.data_array or [])
            if chunk.next_chunk_index is None:
                break
            chunk = api.get_statement_result_chunk_n(response.statement_id, chunk.next_chunk_index)
        return [dict(zip(names, row)) for row in rows]

    return execute
