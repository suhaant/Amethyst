"""
Turn the model's infection probability into a 0-100 risk score and a
treatment plan for the 405 nm LED and the two ultrasound modes.

Risk score
    p_infected = P(warning) + P(infection) from the random forest
    risk       = exponential moving average of p_infected (tau 3 h), x100
                 -> smooths single-reading spikes
    tier       = with hysteresis (tier goes up at the "up" threshold,
                 only comes down 10 points below it) so the device
                 doesn't flip on/off every reading

Treatment sessions every 8 h (3/day). Doses scale continuously with risk
inside safety caps. ALL VALUES ARE PROTOTYPE SETTINGS FROM LITERATURE,
NOT A VALIDATED MEDICAL PROTOCOL.

Usage:
    python risk_to_dose.py      # writes demo_dataset/treatment_plan.csv
"""

import numpy as np
import pandas as pd

# --- dosing settings (sources in README / chat) ----------------------------
LED_IRRADIANCE_MW = 10.0       # 405 nm; 3-10 mW/cm2 used in wound studies
LED_DAILY_CAP_J = 36.0         # 36 J/cm2 bactericidal, no harm to mammalian cells in vitro;
                               # 54 J/cm2 started killing them (Ramakrishnan 2016)
US_LF = {"freq": "40 kHz", "intensity_w_cm2": (0.1, 0.5), "max_min": 10}
                               # non-contact LFU: 0.1-0.8 W/cm2, 4-10 min (Aetna CPB 0746)
US_HEAL = {"freq": "1.5 MHz", "intensity_mw_cm2": 30, "duty": 0.2, "min_per_day": 20}
                               # LIPUS: 1.5 MHz, 30 mW/cm2, 20% duty, 20 min/day
SESSIONS_PER_DAY = 3
SESSION_EVERY_H = 24 / SESSIONS_PER_DAY
EMA_TAU_H = 3.0
LIFTED_KOHM = 150              # patch off skin -> never fire LED/ultrasound

TIERS = [  # (name, up threshold on 0-100 risk)
    ("0 monitor", 0),
    ("1 watch", 30),
    ("2 treat", 55),
    ("3 intensive", 80),
]


def smooth_risk(p, step_h):
    a = step_h / (EMA_TAU_H + step_h)
    out = np.empty(len(p))
    out[0] = p[0]
    for i in range(1, len(p)):
        out[i] = out[i - 1] + a * (p[i] - out[i - 1])
    return out * 100


def tiers_with_hysteresis(risk, down_gap=10):
    t, cur = [], 0
    ups = [u for _, u in TIERS]
    for r in risk:
        while cur + 1 < len(ups) and r >= ups[cur + 1]:
            cur += 1
        while cur > 0 and r < ups[cur] - down_gap:
            cur -= 1
        t.append(cur)
    return np.array(t)


def session_plan(risk, tier):
    """Dose for ONE 8-hour session given current risk (0-100) and tier."""
    x = np.clip((risk - 30) / 60, 0, 1)                     # 0 at risk 30, 1 at risk 90
    led_j = LED_DAILY_CAP_J / SESSIONS_PER_DAY * x if tier >= 1 else 0.0
    led_min = led_j / (LED_IRRADIANCE_MW / 1000) / 60      # E = P*t
    if tier >= 2:                                           # break biofilm first
        lf_min = max(4.0, US_LF["max_min"] * np.clip((risk - 55) / 35, 0, 1))
        lo, hi = US_LF["intensity_w_cm2"]
        lf_int = lo + (hi - lo) * np.clip((risk - 55) / 35, 0, 1)
    else:
        lf_min, lf_int = 0.0, 0.0
    heal_min = US_HEAL["min_per_day"] / SESSIONS_PER_DAY if tier == 0 else 0.0
    return {
        "us_40khz_min": round(lf_min, 1),
        "us_40khz_w_cm2": round(lf_int, 2),
        "led_405nm_min": round(led_min, 1),
        "led_405nm_mw_cm2": LED_IRRADIANCE_MW if led_min > 0 else 0.0,
        "led_dose_j_cm2": round(led_j, 2),
        "us_1p5mhz_min": round(heal_min, 1),
        "order": "40 kHz ultrasound -> 405 nm LED" if lf_min > 0 else ("405 nm LED" if led_min > 0 else
                 ("1.5 MHz healing ultrasound" if heal_min > 0 else "-")),
    }


def main():
    pred = pd.read_csv("demo_dataset/model_predictions.csv")
    raw = pd.read_csv("demo_dataset/demo_readings.csv")[["wound_id", "hour", "impedance_kohm"]]
    pred = pred.merge(raw, on=["wound_id", "hour"], how="left")
    step_h = pred["hour"].iloc[1] - pred["hour"].iloc[0]

    readings, sessions = [], []
    for wid, g in pred.groupby("wound_id"):
        g = g.sort_values("hour").copy()
        g["risk_score"] = smooth_risk(g["p_infected"].values, step_h).round(1)
        g["tier"] = tiers_with_hysteresis(g["risk_score"].values)
        g["tier_name"] = [TIERS[t][0] for t in g["tier"]]
        readings.append(g)
        for _, r in g[(g["hour"] % SESSION_EVERY_H) == 0].iterrows():
            plan = session_plan(r["risk_score"], r["tier"])
            if r["impedance_kohm"] > LIFTED_KOHM:            # safety interlock
                plan = {k: (0 if isinstance(v, (int, float)) else "SKIPPED: patch not on skin")
                        for k, v in plan.items()}
            sessions.append({"wound_id": wid, "timestamp": r["timestamp"], "hour": r["hour"],
                             "true_label": r["label"], "risk_score": r["risk_score"],
                             "tier": r["tier_name"], **plan})

    pd.concat(readings)[["wound_id", "timestamp", "hour", "label", "p_infected", "risk_score", "tier_name"]] \
        .to_csv("demo_dataset/risk_scores.csv", index=False)
    s = pd.DataFrame(sessions)
    s.to_csv("demo_dataset/treatment_plan.csv", index=False)

    daily = s.assign(day=(s.hour // 24 + 1).astype(int)).groupby(["wound_id", "day"])[
        ["led_dose_j_cm2", "us_40khz_min"]].sum()
    assert daily["led_dose_j_cm2"].max() <= LED_DAILY_CAP_J + 1e-6
    print("max daily LED dose:", daily["led_dose_j_cm2"].max(), "J/cm2 (cap", LED_DAILY_CAP_J, ")")
    print("\nDEMO-02 sessions (infection ~hour 76):")
    print(s[(s.wound_id == "DEMO-02") & (s.hour.between(64, 128))]
          [["hour", "true_label", "risk_score", "tier", "us_40khz_min", "led_405nm_min", "led_dose_j_cm2"]]
          .to_string(index=False))
    tot = s.groupby("wound_id")[["led_dose_j_cm2", "us_40khz_min"]].sum().round(1)
    tot["outcome"] = pd.read_csv("demo_dataset/wound_scenarios.csv").set_index("wound_id")["true_outcome"]
    print("\nTotal over 10 days per wound:")
    print(tot.to_string())


if __name__ == "__main__":
    main()
