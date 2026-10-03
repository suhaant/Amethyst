"""
MLflow pyfunc wrapper so a Databricks Model Serving endpoint (or a batch job)
takes RAW patch readings and returns risk scores.

The bare XGBoost model needs 27 trend features built from each wound's
history; this wrapper runs the same feature code as training
(predict.WoundRiskModel) so callers never compute features themselves.

Input  (DataFrame, one row per reading, each wound's full history):
    wound_id, timestamp, ph, temp_c, impedance_kohm, blood_glucose_mgdl, wound_glucose_mM
Output (DataFrame, one row per reading after the first 24 h):
    wound_id, timestamp, hour, p_infected, predicted_label, risk_score, tier, tier_name
"""

import os
import shutil
import sys
import tempfile

import mlflow.pyfunc

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_FILES = ["predict.py", "train_model.py", "risk_to_dose.py"]


class WoundRiskPyfunc(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        from predict import WoundRiskModel
        self.model = WoundRiskModel(context.artifacts["model_dir"])

    def predict(self, context, model_input, params=None):
        out = self.model.predict(model_input)
        return out.drop(columns=["impedance_kohm"])


def export_xgb(model, features, labels, step_min, out_dir, extra_meta=None):
    """Write the XGBoost model + metadata in the layout predict.py expects."""
    import json
    os.makedirs(out_dir, exist_ok=True)
    model.save_model(os.path.join(out_dir, "xgboost_model.json"))
    meta = {"features": features, "labels": labels, "step_min": step_min, **(extra_meta or {})}
    with open(os.path.join(out_dir, "model_meta.json"), "w") as f:
        json.dump(meta, f, indent=2, default=float)
    return out_dir


def log_pyfunc(model_dir, input_example, registered_model_name=None, name="wound_risk_model"):
    """Log (and optionally register) the wrapper with its code and model files."""
    import numpy as np
    import pandas as pd
    import sklearn
    import xgboost
    from mlflow.models import infer_signature

    sys.path.insert(0, REPO)
    from predict import WoundRiskModel

    example_out = WoundRiskModel(model_dir).predict(input_example).drop(columns=["impedance_kohm"])
    signature = infer_signature(input_example, example_out)

    code_dir = tempfile.mkdtemp()
    for f in CODE_FILES:
        shutil.copy(os.path.join(REPO, f), code_dir)

    return mlflow.pyfunc.log_model(
        name=name,
        python_model=WoundRiskPyfunc(),
        artifacts={"model_dir": model_dir},
        code_paths=[os.path.join(code_dir, f) for f in CODE_FILES],
        signature=signature,
        input_example=input_example,          # one full wound (needs >24 h)
        registered_model_name=registered_model_name,
        pip_requirements=[
            f"xgboost=={xgboost.__version__}",
            f"scikit-learn=={sklearn.__version__}",
            f"pandas=={pd.__version__}",
            f"numpy=={np.__version__}",
        ],
    )
