"""Adapter around Adam's trained XGBoost model (predict.WoundRiskModel)."""

from __future__ import annotations

import pandas as pd

from predict import WoundRiskModel

from .schemas import InfectionPrediction, TreatmentPlan

STEPS_PER_HOUR = 2  # model works on 30-minute readings


class RiskModel:
    name = "xgboost (model/xgboost_model.json)"

    def __init__(self) -> None:
        self._model = WoundRiskModel()
        self.meta = self._model.meta

    def predict(self, history: pd.DataFrame) -> tuple[InfectionPrediction, pd.DataFrame]:
        """Score every reading after the first 24 h; summarise the latest one."""
        result = self._model.predict(history)
        last = result.iloc[-1]
        risk = result["risk_score"].tolist()

        def risk_ago(hours: int) -> float | None:
            i = len(risk) - 1 - hours * STEPS_PER_HOUR
            return float(risk[i]) if i >= 0 else None

        prediction = InfectionPrediction(
            p_infected=float(last["p_infected"]),
            predicted_label=str(last["predicted_label"]),
            risk_score=float(last["risk_score"]),
            risk_score_6h_ago=risk_ago(6),
            risk_score_24h_ago=risk_ago(24),
            tier=str(last["tier_name"]),
            model_name=self.name,
        )
        return prediction, result

    def plan(self, result: pd.DataFrame) -> TreatmentPlan:
        """Next-session plan from risk_to_dose, including the patch-lifted interlock."""
        plan = next(iter(WoundRiskModel.latest_plan(result).values()))
        skipped = plan.pop("status", None)
        return TreatmentPlan(skipped_reason=skipped, **plan)
