"""Databricks store, gateway and CLI, tested against a fake SQL warehouse (no network)."""

import json
import re

import numpy as np
import pandas as pd
import pytest

import main as cli
import patch_gateway
from wound_agent.agent import run_offline
from wound_agent.data_sources import DummyDataSource
from wound_agent.databricks_store import (
    ASSESSMENT_COLUMNS,
    INSERT_CHUNK,
    DatabricksConfigError,
    DatabricksStore,
    assessment_row,
)
from wound_agent.model import RiskModel
from wound_agent.schemas import SENSOR_COLUMNS, AgentNotes


class FakeWarehouse:
    """Stands in for `execute`. Holds readings in memory and answers the store's statements like Databricks:
    every value comes back as a string, or None for NULL."""

    def __init__(self):
        self.statements = []          # (sql, params) in call order
        self.readings = {}            # wound_id -> list of row dicts
        self.assessments = []         # params of each assessment insert
        self.fail_assessment_insert = False

    def load(self, history: pd.DataFrame, source: str):
        for _, row in history.iterrows():
            stored = {"wound_id": str(row["wound_id"]), "timestamp": str(row["timestamp"]), "hour": str(row["hour"]),
                      "source": source}
            for name in SENSOR_COLUMNS:
                stored[name] = None if pd.isna(row[name]) else str(row[name])
            self.readings.setdefault(stored["wound_id"], []).append(stored)

    def __call__(self, sql, params):
        self.statements.append((sql, params))
        if sql.startswith("SELECT DISTINCT wound_id"):
            return [{"wound_id": w} for w in self.readings]
        if sql.startswith("SELECT wound_id"):
            return list(reversed(self.readings.get(params["wound_id"], [])))   # out of order on purpose
        if sql.startswith("INSERT INTO") and ".assessments" in sql:
            if self.fail_assessment_insert:
                raise RuntimeError("Databricks statement failed: warehouse stopped")
            self.assessments.append(params)
        return []

    def sql(self, prefix):
        return [s for s, _ in self.statements if s.startswith(prefix)]


@pytest.fixture(scope="module")
def model():
    return RiskModel()


@pytest.fixture
def warehouse():
    return FakeWarehouse()


@pytest.fixture
def store(warehouse):
    return DatabricksStore(warehouse)


def simulated(wound_id="wound-003", scenario="infected"):
    return DummyDataSource(scenario, seed=0).get_history(wound_id)


def test_history_comes_back_typed_and_sorted_and_the_model_accepts_it(store, warehouse, model):
    original = simulated()
    warehouse.load(original, "simulated")
    history = store.get_history("wound-003")
    assert list(history.columns) == ["wound_id", "timestamp", "hour", *SENSOR_COLUMNS]
    assert history["hour"].is_monotonic_increasing
    assert all(history[name].dtype == float for name in ["hour", *SENSOR_COLUMNS])
    np.testing.assert_allclose(history["ph"], original["ph"])
    assert store.is_dummy

    from_databricks = run_offline("wound-003", store, model)
    direct = run_offline("wound-003", DummyDataSource("infected", seed=0), model)
    assert from_databricks.prediction.risk_score == pytest.approx(direct.prediction.risk_score)
    assert from_databricks.prediction.tier == direct.prediction.tier
    assert "Readings are simulated dummy data." in from_databricks.caveats


def test_wound_id_is_a_parameter_never_part_of_the_sql(store, warehouse):
    warehouse.load(simulated(), "simulated")
    store.get_history("wound-003")
    sql, params = warehouse.statements[-1]
    assert "wound-003" not in sql and params == {"wound_id": "wound-003"}


def test_history_for_unknown_wound_raises(store):
    with pytest.raises(ValueError, match="wound-404"):
        store.get_history("wound-404")


def test_is_dummy_follows_the_source(store, warehouse):
    warehouse.load(simulated("wound-007"), "file")
    store.get_history("wound-007")
    assert not store.is_dummy


def test_missing_sensor_values_come_back_as_nan(store, warehouse):
    history = simulated()
    history.loc[3, "ph"] = np.nan
    warehouse.load(history, "simulated")
    assert np.isnan(store.get_history("wound-003").loc[3, "ph"])


def test_upload_deletes_first_then_inserts_in_chunks(store, warehouse):
    rows = 2 * INSERT_CHUNK + 7
    history = pd.concat([simulated("wound-001", "healthy")] * 8, ignore_index=True).head(rows)
    assert len(history) == rows
    assert store.upload_readings(history, "simulated") == rows
    kinds = [sql.split()[0] for sql, _ in warehouse.statements]
    assert kinds == ["DELETE"] + ["INSERT"] * 3
    assert warehouse.statements[0][1] == {"wound_id": "wound-001"}
    rows_per_insert = [sql.count("TIMESTAMP '") // 2 for sql in warehouse.sql("INSERT")]
    assert rows_per_insert == [INSERT_CHUNK, INSERT_CHUNK, 7]
    assert all(", 'simulated', TIMESTAMP '" in sql for sql in warehouse.sql("INSERT"))


def test_upload_writes_null_for_missing_values(store, warehouse):
    history = simulated().head(4).copy()
    history.loc[1, "impedance_kohm"] = np.nan
    history.loc[2, "wound_glucose_mM"] = None
    store.upload_readings(history, "file")
    insert = warehouse.sql("INSERT")[0]
    assert insert.count("NULL") == 2 and "nan" not in insert.lower()


def test_upload_one_delete_per_wound(store, warehouse):
    history = pd.concat([simulated("wound-001", "healthy").head(3), simulated("wound-002").head(3)])
    store.upload_readings(history, "simulated")
    assert [p["wound_id"] for s, p in warehouse.statements if s.startswith("DELETE")] == ["wound-001", "wound-002"]


@pytest.mark.parametrize("bad_id", ["x'; DROP TABLE readings; --", "", "wound 1", "w" * 65])
def test_bad_wound_ids_are_rejected_before_any_sql(store, warehouse, bad_id):
    with pytest.raises(ValueError):
        store.upload_readings(simulated().head(2).assign(wound_id=bad_id), "simulated")
    with pytest.raises(ValueError):
        store.get_history(bad_id)
    assert warehouse.statements == []


def test_unknown_source_is_rejected(store, warehouse):
    with pytest.raises(ValueError, match="source"):
        store.upload_readings(simulated().head(2), "guesswork")
    assert warehouse.statements == []


@pytest.mark.parametrize("catalog,schema", [("work space", "pulsepatch"), ("workspace", "pulse;patch"), ("", "x")])
def test_bad_catalog_or_schema_names_are_rejected(warehouse, catalog, schema):
    with pytest.raises(ValueError):
        DatabricksStore(warehouse, catalog, schema)


def test_ensure_tables_creates_schema_and_both_tables(store, warehouse):
    store.ensure_tables()
    schema, readings, assessments = [sql for sql, _ in warehouse.statements]
    assert schema == "CREATE SCHEMA IF NOT EXISTS workspace.pulsepatch"
    assert "workspace.pulsepatch.readings" in readings and "impedance_kohm DOUBLE" in readings
    assert "workspace.pulsepatch.assessments" in assessments
    assert all(re.search(rf"\b{name}\b", assessments) for name in ASSESSMENT_COLUMNS)


def test_assessment_row_without_agent_notes(model):
    assessment = run_offline("wound-003", DummyDataSource("infected", seed=0), model)
    row = assessment_row(assessment)
    assert list(row) == list(ASSESSMENT_COLUMNS)
    assert row["assessed_by"] == "model-only"
    assert row["summary"] is None and row["recommend_clinician_review"] is None
    assert row["risk_score"] == assessment.prediction.risk_score
    assert row["caveats"] == "; ".join(assessment.caveats)
    assert json.loads(row["assessment_json"])["wound_id"] == "wound-003"


def test_assessment_row_with_agent_notes(model):
    assessment = run_offline("wound-003", DummyDataSource("infected", seed=0), model)
    assessment.agent_notes = AgentNotes(
        summary="Rising risk.", trend="pH up 0.6 in 24 h.", reasoning="pH and temperature agree.",
        data_quality_flags=["impedance spike at hour 40", "glucose gap"], conflicting_signals=[],
        recommend_clinician_review=True, confidence="medium")
    row = assessment_row(assessment)
    assert row["assessed_by"] == "opus-agent"
    assert row["data_quality_flags"] == "impedance spike at hour 40; glucose gap"
    assert row["conflicting_signals"] == ""
    assert row["recommend_clinician_review"] is True and row["confidence"] == "medium"


def test_save_assessment_sends_every_field_as_a_parameter(store, warehouse, model):
    assessment = run_offline("wound-003", DummyDataSource("infected", seed=0), model)
    assessment.agent_notes = AgentNotes(
        summary="It's worse'); DROP TABLE assessments; --", trend="t", reasoning="r", data_quality_flags=[],
        conflicting_signals=[], recommend_clinician_review=False, confidence="low")
    store.save_assessment(assessment)
    sql, params = warehouse.statements[-1]
    assert "DROP TABLE" not in sql
    assert set(params) == set(ASSESSMENT_COLUMNS)
    assert params["summary"] == "It's worse'); DROP TABLE assessments; --"
    assert params["recommend_clinician_review"] == "false"
    assert params["risk_score_24h_ago"] is None or float(params["risk_score_24h_ago"]) >= 0
    assert "CAST(:risk_score AS DOUBLE)" in sql and "CAST(:generated_at AS TIMESTAMP)" in sql


def test_from_env_names_every_missing_setting():
    with pytest.raises(DatabricksConfigError) as error:
        DatabricksStore.from_env({"DATABRICKS_HOST": "https://example.cloud.databricks.com"})
    assert "DATABRICKS_TOKEN" in str(error.value) and "DATABRICKS_WAREHOUSE_ID" in str(error.value)
    assert "DATABRICKS_HOST" not in str(error.value)


def test_from_env_uses_defaults_and_overrides():
    env = {"DATABRICKS_HOST": "h", "DATABRICKS_TOKEN": "t", "DATABRICKS_WAREHOUSE_ID": "w"}
    assert DatabricksStore.from_env(env).readings == "workspace.pulsepatch.readings"
    custom = DatabricksStore.from_env({**env, "DATABRICKS_CATALOG": "main", "DATABRICKS_SCHEMA": "demo"})
    assert custom.assessments == "main.demo.assessments"


# ---- command line ----

def test_cli_databricks_offline_saves_one_assessment(store, warehouse, capsys):
    warehouse.load(simulated(), "simulated")
    assert cli.main(["--databricks", "--offline", "--wound", "wound-003"], store=store) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["wound_id"] == "wound-003"
    assert len(warehouse.assessments) == 1
    assert warehouse.assessments[0]["wound_id"] == "wound-003"
    assert warehouse.assessments[0]["assessed_by"] == "model-only"


def test_cli_all_assesses_every_wound(store, warehouse, capsys):
    warehouse.load(simulated("wound-001", "healthy"), "simulated")
    warehouse.load(simulated("wound-003", "infected"), "simulated")
    assert cli.main(["--databricks", "--offline", "--all"], store=store) == 0
    assert [a["wound_id"] for a in warehouse.assessments] == ["wound-001", "wound-003"]


def test_cli_prints_the_assessment_even_when_saving_fails(store, warehouse, capsys):
    warehouse.load(simulated(), "simulated")
    warehouse.fail_assessment_insert = True
    assert cli.main(["--databricks", "--offline", "--wound", "wound-003"], store=store) == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out)["wound_id"] == "wound-003"
    assert "Could not save" in captured.err


@pytest.mark.parametrize("argv", [["--all"], ["--databricks", "--all", "--out", "x.json"],
                                  ["--databricks", "--history", "sample_data/simulated_wound_history.csv"]])
def test_cli_rejects_bad_flag_combinations(argv):
    with pytest.raises(SystemExit) as exit_info:
        cli.main(argv)
    assert exit_info.value.code == 2


def test_cli_reports_missing_databricks_settings(monkeypatch, capsys):
    for name in ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_WAREHOUSE_ID"):
        monkeypatch.delenv(name, raising=False)
    assert cli.main(["--databricks", "--offline"]) == 1
    assert "DATABRICKS_HOST" in capsys.readouterr().err


# ---- gateway ----

def test_gateway_demo_cohort_uploads_five_simulated_wounds(store, warehouse, capsys):
    assert patch_gateway.main(["--demo-cohort"], store=store) == 0
    kinds = [sql.split()[0] for sql, _ in warehouse.statements]
    assert kinds[:3] == ["CREATE", "CREATE", "CREATE"]                       # tables are ensured first
    deleted = [p["wound_id"] for s, p in warehouse.statements if s.startswith("DELETE")]
    assert deleted == ["wound-001", "wound-002", "wound-003", "wound-004", "wound-005"]
    assert all("'simulated'" in sql for sql in warehouse.sql("INSERT"))
    assert capsys.readouterr().out.count("uploaded") == 5


def test_gateway_history_file_is_stored_as_file_source(store, warehouse):
    assert patch_gateway.main(["--wound", "wound-007", "--history", "sample_data/simulated_wound_history.csv"],
                              store=store) == 0
    inserts = warehouse.sql("INSERT")
    assert inserts and all("'wound-007'" in sql and "'file'" in sql for sql in inserts)


def test_gateway_needs_a_cohort_or_a_wound():
    with pytest.raises(SystemExit):
        patch_gateway.main([])


# ---- the real `execute`, against a stand-in for the Databricks SDK client ----

def _response(state, rows=None, next_chunk=None, error=None, columns=("wound_id", "hour")):
    from databricks.sdk.service import sql

    return sql.StatementResponse(
        statement_id="stmt-1",
        status=sql.StatementStatus(state=state, error=sql.ServiceError(message=error) if error else None),
        manifest=sql.ResultManifest(schema=sql.ResultSchema(columns=[sql.ColumnInfo(name=c) for c in columns])),
        result=sql.ResultData(data_array=rows, next_chunk_index=next_chunk) if rows is not None else None,
    )


class FakeSdkClient:
    script = []          # responses handed out in order: first to execute_statement, the rest to get_statement
    chunks = {}
    calls = []

    def __init__(self, host, token):
        self.statement_execution = self
        FakeSdkClient.calls.append(("client", host))

    def execute_statement(self, statement, warehouse_id, parameters, wait_timeout):
        FakeSdkClient.calls.append(("execute", statement, warehouse_id, [(p.name, p.value) for p in parameters]))
        return FakeSdkClient.script.pop(0)

    def get_statement(self, statement_id):
        return FakeSdkClient.script.pop(0) if len(FakeSdkClient.script) > 1 else FakeSdkClient.script[0]

    def get_statement_result_chunk_n(self, statement_id, chunk_index):
        return FakeSdkClient.chunks[chunk_index]


@pytest.fixture
def sdk(monkeypatch):
    import databricks.sdk

    FakeSdkClient.script, FakeSdkClient.chunks, FakeSdkClient.calls = [], {}, []
    monkeypatch.setattr(databricks.sdk, "WorkspaceClient", FakeSdkClient)
    monkeypatch.setattr("wound_agent.databricks_store.time.sleep", lambda seconds: None)
    return FakeSdkClient


def test_sdk_execute_waits_for_a_cold_warehouse_and_reads_every_chunk(sdk):
    from databricks.sdk.service import sql
    from wound_agent.databricks_store import sdk_execute

    state = sql.StatementState
    sdk.script = [_response(state.PENDING), _response(state.RUNNING),
                  _response(state.SUCCEEDED, rows=[["wound-001", "0.0"]], next_chunk=1)]
    sdk.chunks = {1: sql.ResultData(data_array=[["wound-001", "0.5"]], next_chunk_index=None)}
    execute = sdk_execute("https://example.cloud.databricks.com", "token", "wh-1")
    rows = execute("SELECT wound_id, hour FROM t WHERE wound_id = :wound_id", {"wound_id": "wound-001"})
    assert rows == [{"wound_id": "wound-001", "hour": "0.0"}, {"wound_id": "wound-001", "hour": "0.5"}]
    kind, statement, warehouse, params = sdk.calls[1]
    assert (kind, warehouse, params) == ("execute", "wh-1", [("wound_id", "wound-001")])
    sdk.script = [_response(state.SUCCEEDED, rows=[])]
    assert execute("SELECT 1", {}) == []
    assert [c[0] for c in sdk.calls].count("client") == 1          # one client, reused


def test_sdk_execute_raises_the_databricks_error_message(sdk):
    from databricks.sdk.service import sql
    from wound_agent.databricks_store import sdk_execute

    sdk.script = [_response(sql.StatementState.FAILED, error="TABLE_OR_VIEW_NOT_FOUND: readings")]
    with pytest.raises(RuntimeError, match="TABLE_OR_VIEW_NOT_FOUND"):
        sdk_execute("h", "t", "w")("SELECT 1", {})


def test_sdk_execute_times_out_when_the_warehouse_never_starts(sdk):
    from databricks.sdk.service import sql
    from wound_agent.databricks_store import sdk_execute

    sdk.script = [_response(sql.StatementState.PENDING)]
    with pytest.raises(TimeoutError, match="warehouse"):
        sdk_execute("h", "t", "w", timeout_s=0)("SELECT 1", {})
