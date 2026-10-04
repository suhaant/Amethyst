"""Round trip against a real Databricks workspace. Skipped unless the settings are in the environment or .env."""

import os
import uuid
from pathlib import Path

import numpy as np
import pytest
from dotenv import load_dotenv

from wound_agent.agent import run_offline
from wound_agent.data_sources import DummyDataSource
from wound_agent.databricks_store import REQUIRED_SETTINGS, DatabricksStore
from wound_agent.model import RiskModel

load_dotenv(Path(__file__).parent.parent / ".env")
pytestmark = pytest.mark.skipif(
    not all(os.environ.get(name) for name in REQUIRED_SETTINGS), reason="Databricks settings not present"
)


def test_upload_read_assess_save_round_trip():
    store = DatabricksStore.from_env()
    store.ensure_tables()
    wound = f"pytest-{uuid.uuid4().hex[:12]}"                     # throwaway id, removed below
    history = DummyDataSource("infected", seed=0).get_history(wound).head(60)
    try:
        assert store.upload_readings(history, "simulated") == 60
        assert wound in store.list_wounds()
        stored = store.get_history(wound)
        assert len(stored) == 60 and store.is_dummy
        np.testing.assert_allclose(stored["ph"], history["ph"])
        assessment = run_offline(wound, store, RiskModel())
        store.save_assessment(assessment)
        saved = store._execute(
            f"SELECT risk_score, assessed_by FROM {store.assessments} WHERE wound_id = :wound_id", {"wound_id": wound}
        )
        assert len(saved) == 1 and saved[0]["assessed_by"] == "model-only"
        assert float(saved[0]["risk_score"]) == pytest.approx(assessment.prediction.risk_score)
    finally:
        for table in (store.readings, store.assessments):
            store._execute(f"DELETE FROM {table} WHERE wound_id = :wound_id", {"wound_id": wound})
