"""
Real glucose backgrounds from the BIG IDEAs Lab Glycemic Variability and
Wearable Device Data (PhysioNet, v1.1.3, ODC-By 1.0).
https://physionet.org/content/big-ideas-glycemic-wearable/1.1.3/

16 adults (HbA1c 5.2-6.4%, normal to prediabetic), Dexcom G6 CGM every
5 min for ~8-10 days. Each person's trace is cut into whole days and
resampled to the simulator's time step, so a 14-day wound can be built
from that person's real days (meal spikes, overnight patterns kept).
"""

import glob
import os

import numpy as np
import pandas as pd

# override with WOUND_GLUCOSE_DIR (e.g. a Databricks Unity Catalog volume path)
DATA_DIR = os.environ.get("WOUND_GLUCOSE_DIR",
                          os.path.join(os.path.dirname(__file__), "data", "bigideas"))


def load_participants(step_min=30):
    """Return {participant_id: {"hba1c": float, "days": [np.array per day]}}."""
    demo = pd.read_csv(os.path.join(DATA_DIR, "Demographics.csv"), encoding="utf-8-sig")
    hba1c = dict(zip(demo["ID"].astype(int), demo["HbA1c"].astype(float)))
    per_day = int(24 * 60 / step_min)
    people = {}
    for f in sorted(glob.glob(os.path.join(DATA_DIR, "*", "Dexcom_*.csv"))):
        pid = int(os.path.basename(f).split("_")[1].split(".")[0])
        d = pd.read_csv(f)
        d = d[d["Event Type"] == "EGV"]
        s = pd.Series(pd.to_numeric(d["Glucose Value (mg/dL)"], errors="coerce").values,
                      index=pd.to_datetime(d["Timestamp (YYYY-MM-DDThh:mm:ss)"])).sort_index()
        s = s.resample(f"{step_min}min").mean().interpolate(limit=4)
        days = []
        for _, day in s.groupby(s.index.date):
            if len(day) == per_day and day.notna().all():   # complete days only
                days.append(day.values.astype(float))
        if days:
            people[pid] = {"hba1c": hba1c.get(pid, np.nan), "days": days}
    return people


def build_trace(person, n_steps, rng):
    """Concatenate randomly chosen real days of one person to n_steps."""
    out, days = [], person["days"]
    while sum(len(d) for d in out) < n_steps:
        out.append(days[rng.integers(len(days))])
    return np.concatenate(out)[:n_steps]


if __name__ == "__main__":
    ppl = load_participants()
    for pid, p in ppl.items():
        allg = np.concatenate(p["days"])
        print(f"{pid:>3} HbA1c {p['hba1c']:.1f}  full days {len(p['days'])}  "
              f"mean {allg.mean():.0f}  CV {allg.std() / allg.mean():.0%}")
