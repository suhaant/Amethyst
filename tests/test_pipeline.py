from pathlib import Path

import pytest

from risk_to_dose import LED_DAILY_CAP_J, SESSIONS_PER_DAY
from wound_agent.agent import run_offline, summarize_history
from wound_agent.data_sources import SCENARIOS, DummyDataSource, FileDataSource
from wound_agent.model import RiskModel

SAMPLE = Path(__file__).parent.parent / "sample_data" / "simulated_wound_history.csv"


@pytest.fixture(scope="module")
def model():
    return RiskModel()


def tier_num(assessment):
    return int(assessment.prediction.tier.split()[0])


@pytest.mark.parametrize("scenario", list(SCENARIOS))
def test_offline_pipeline_runs_for_every_scenario(model, scenario):
    a = run_offline("w", DummyDataSource(scenario, seed=0), model)
    assert a.history_hours >= 24
    assert 0 <= a.prediction.risk_score <= 100
    assert a.agent_notes is None
    assert "Readings are simulated dummy data." in a.caveats


@pytest.mark.parametrize("seed", range(5))
def test_scenarios_land_in_expected_tiers(model, seed):
    def run(s):
        return run_offline("w", DummyDataSource(s, seed=seed), model)

    assert tier_num(run("healthy")) == 0
    assert 1 <= tier_num(run("early_infection")) <= 2
    assert tier_num(run("infected")) >= 2


@pytest.mark.parametrize("scenario", list(SCENARIOS))
def test_doses_stay_within_caps(model, scenario):
    t = run_offline("w", DummyDataSource(scenario, seed=1), model).treatment
    assert t.led_dose_j_cm2 * SESSIONS_PER_DAY <= LED_DAILY_CAP_J + 1e-6
    assert t.us_40khz_min <= 10


def test_patch_lifted_skips_treatment(model):
    t = run_offline("w", DummyDataSource("patch_lifted", seed=0), model).treatment
    assert t.skipped_reason
    assert t.led_405nm_min == t.us_40khz_min == t.us_1p5mhz_min == 0


def test_monitor_tier_gets_healing_ultrasound_only(model):
    t = run_offline("w", DummyDataSource("healthy", seed=0), model).treatment
    assert t.us_1p5mhz_min > 0 and t.led_405nm_min == 0 and t.us_40khz_min == 0


def test_dummy_history_has_no_answer_key():
    h = DummyDataSource("infected", seed=0).get_history("w")
    assert not {"label", "outcome", "infection_onset_h"} & set(h.columns)


def test_file_source_matches_sample(model):
    a = run_offline("wound-001", FileDataSource(str(SAMPLE)), model)
    assert a.n_readings > 48
    assert not any("dummy" in c for c in a.caveats)


def test_summary_reports_baseline_and_lifted_patch():
    s = summarize_history(DummyDataSource("patch_lifted", seed=0).get_history("w"))
    assert s["readings_with_patch_lifted"] == 4
    assert set(s["sensors"]["ph"]) >= {"day1_baseline_median", "change_vs_24h_ago"}
    assert len(s["last_6h_readings"]) == 12


@pytest.mark.parametrize("risk,tier", [(10, 0), (25, 1), (29.9, 1), (35, 1), (50, 1)])
def test_sessions_without_led_get_healing_ultrasound(risk, tier):
    from risk_to_dose import session_plan

    plan = session_plan(risk, tier)
    assert plan["led_405nm_min"] == 0 and plan["us_1p5mhz_min"] > 0


@pytest.mark.parametrize("risk,tier", [(55, 2), (60, 2), (95, 3)])
def test_led_sessions_skip_healing_ultrasound(risk, tier):
    from risk_to_dose import session_plan

    plan = session_plan(risk, tier)
    assert plan["led_405nm_min"] > 0 and plan["us_1p5mhz_min"] == 0
