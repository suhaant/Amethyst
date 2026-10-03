#!/usr/bin/env bash
# Full pipeline, in order. Takes ~20-30 min on a laptop.
set -euo pipefail
cd "$(dirname "$0")"
[ -f data/bigideas/Demographics.csv ] || ./download_glucose.sh
python generate_data.py        # 1. simulate 600 wounds -> data/wound_timeseries.csv
python train_model.py          # 2. quick 4-fold person-grouped CV, sensor sets compared
python make_demo.py            # 3. held-out demo/API set -> demo_dataset/
python train_final.py          # 4. leave-one-person-out, ablation, calibration, final model -> models/
python compare_models.py       # 5. random forest vs XGBoost -> models/rf_vs_xgboost.csv
python risk_to_dose.py         # 6. risk score -> LED / ultrasound plan -> demo_dataset/treatment_plan.csv
python build_workbook.py       # 7. Excel summary -> Wound_Patch_ML_Dataset.xlsx
