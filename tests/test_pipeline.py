from pathlib import Path

import pytest

from wound_agent.agent import run_offline
from wound_agent.data_sources import SCENARIOS, DummyDataSource, JsonFileDataSource
from wound_agent.model import StubModel, predict
from wound_agent.schemas import InfectionPrediction
from wound_agent.treatment import ULTRASOUND_MAX_KHZ, ULTRASOUND_MIN_KHZ, plan_treatment

SAMPLE = Path(__file__).parent.parent / "sample_data" / "reading_example.json"


def _prediction(p: float) -> InfectionPrediction:
    return InfectionPrediction(probability=p, infection_detected=p >= 0.5, threshold=0.5, model_name="t")


@pytest.mark.parametrize("p", [0.0, 0.29, 0.3, 0.6, 0.85, 1.0])
def test_plan_stays_within_device_limits(p):
    plan = plan_treatment(_prediction(p))
    if plan.treat:
        assert ULTRASOUND_MIN_KHZ <= plan.ultrasound_frequency_khz <= ULTRASOUND_MAX_KHZ
        assert plan.violet_light_minutes > 0
    else:
        assert plan.ultrasound_frequency_khz is None
        assert plan.violet_light_minutes == 0


def test_dose_increases_with_probability():
    doses = [plan_treatment(_prediction(p)).violet_light_minutes for p in (0.1, 0.4, 0.7, 0.9)]
    assert doses == sorted(doses)


@pytest.mark.parametrize("seed", range(20))
def test_stub_separates_healthy_from_infected(seed):
    model = StubModel()
    healthy = predict(model, DummyDataSource("healthy", seed).get_reading("p"))
    infected = predict(model, DummyDataSource("infected", seed).get_reading("p"))
    assert not healthy.infection_detected
    assert infected.infection_detected


@pytest.mark.parametrize("scenario", list(SCENARIOS))
def test_offline_pipeline_runs_for_every_scenario(scenario):
    a = run_offline("p", DummyDataSource(scenario, seed=0), StubModel())
    assert 0.0 <= a.prediction.probability <= 1.0
    assert a.agent_notes is None


def test_json_file_source_loads_sample():
    reading = JsonFileDataSource(SAMPLE).get_reading("ignored")
    assert reading.patient_id == "patient-001"
    assert reading.temp_delta_c == pytest.approx(2.3)


def test_caveats_come_from_code_not_agent():
    a = run_offline("p", DummyDataSource("healthy", seed=0), StubModel())
    assert any("stub-heuristic-v0" in c for c in a.caveats)
    assert any("placeholders" in c for c in a.caveats)
    assert not any("placeholder" in n for n in a.treatment.notes)
