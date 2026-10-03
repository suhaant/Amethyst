"""
Synthetic smart-wound-patch data generator.

Produces labeled time series of wound pH, temperature and moisture (as
electrical impedance at 1 kHz) for wounds that heal, stall, or become
infected with bacteria. Every parameter below is tied to a published
value (see research/*.md) or marked ASSUMPTION where no number exists.

Output: data/wound_timeseries.csv, one row per sensor reading.
    wound_id, hour, ph, temp_c, impedance_kohm,
    wound_type, outcome, infection_onset_h, artifact, label

label (per row, from the TRUE hidden state, not from sensor values):
    normal     - no infection, or before onset
    warning    - first 24 h after bacterial infection onset
    infection  - >24 h after onset (established infection)

Usage:
    python generate_data.py --wounds 600 --days 14 --step-min 30 --seed 42
"""

import argparse
import os

import numpy as np
import pandas as pd

from glucose_data import build_trace, load_participants

# ---------------------------------------------------------------------------
# Parameters (sources in research/ph.md, temperature.md, moisture.md)
# ---------------------------------------------------------------------------
P = {
    # --- pH -------------------------------------------------------------
    # Acute 6.59 +/- 0.62, chronic 7.11 +/- 0.66 (PMC13035947)
    "ph_base": {"acute": (6.6, 0.45), "chronic": (7.0, 0.45)},
    # Healing -0.088/wk, non-healing -0.03/wk (PMC13035947)
    "ph_slope_per_day": {"healing": -0.088 / 7, "stalled": -0.03 / 7},
    # Infected 7.53 vs non-infected 6.90 -> ~+0.63 (PMC13035947)
    "ph_infection_rise": (0.65, 0.25),
    # Fraction of infections with little pH response (horse study p=0.75,
    # necrosis lowers pH) -- ASSUMPTION on the fraction
    "ph_nonresponder_frac": 0.15,
    # S. aureus may acidify first (~-0.3 for ~8 h, in vitro, unverified)
    "ph_staph_dip": 0.3,
    "ph_noise": 0.05,             # meter +/-0.1-0.2; sensor noise ASSUMPTION
    "ph_drift_per_h": 0.01,       # bench drift up to 0.04/h; in-vivo smaller ASSUMPTION
    # --- temperature ----------------------------------------------------
    # Covered skin ~33-35 C; wound centre ~28.7-29 C under probe in clinic
    # (PMC13035947). Patch sits under dressing -> use ~33.5 C
    "temp_base": (33.5, 0.8),
    # Healing -0.19 C/wk, wounds overall -0.09 C/wk (PMC13035947)
    "temp_slope_per_day": {"healing": -0.19 / 7, "stalled": -0.09 / 7},
    # Infection dT: 1.1 C (Fierheller), 1.6 C (SIDESTEP), 2.15 C cutoff
    # (AUC .85), up to 4-5 C severe (Chanmugam)
    "temp_infection_rise": (1.6, 0.6),
    # Circadian amplitude 1.2-2.2 C peak-to-peak at limbs (PMC11353769);
    # dressing damps it -> half-amplitude 0.3-0.7 C (ASSUMPTION)
    "temp_circadian_half_amp": (0.3, 0.7),
    "temp_circadian_peak_hour": 3,    # distal skin peaks at night
    "temp_noise": 0.1,                # MAX30205 +/-0.1 C
    # Shower: ~-3.5 C, recovers ~30 min (PMC4476093)
    "shower_temp_drop": 3.5,
    "shower_prob_per_day": 0.7,
    # --- moisture (impedance at 1 kHz, kOhm) ----------------------------
    # Fresh wound 6.3 kOhm, intact skin 58.6 kOhm (PMC6603574)
    "z_base": {"acute": (8.0, 2.0), "chronic": (12.0, 4.0)},
    # Impedance rises as wound heals (reactance +90%, PMC12162137).
    # Daily log-growth rates are ASSUMPTION
    "z_log_growth_per_day": {"healing": 0.06, "stalled": 0.01},
    # Impedance falls with infection / more exudate; magnitude unpublished
    # -> ASSUMPTION 20-50% drop
    "z_infection_drop": (0.35, 0.12),
    "z_noise_frac": 0.05,
    "z_shower_frac": -0.4,            # wetter -> lower impedance (ASSUMPTION)
    # --- infection time course -----------------------------------------
    # Rat: pH up at 6 h; peak day 3-4 (Gao 2023, PMC11216007, PMC7080536)
    "lag_h": (6, 24),                 # delay before signals start moving
    "time_to_peak_h": (48, 96),
    # --- dressing changes & artifacts ----------------------------------
    "dressing_change_h": (48, 72),    # DFU ~every 3 days (Milne 2016)
    "detach_prob_per_wound": 0.1,     # ASSUMPTION
    "detach_duration_h": (3, 12),
    "ambient_temp": 27.0,
    # --- cohort mix -----------------------------------------------------
    "frac_chronic": 0.5,
    "frac_infected": 0.35,
    "frac_stalled_of_uninfected": 0.3,
    "staph_frac_of_infected": 0.55,   # S. aureus 6/11 cultures (PMC13035947)
    # --- glucose (real Dexcom backgrounds, BIG IDEAs PhysioNet) ----------
    # Infection risk: OR 1.07 per +10 mg/dL glucose (SCOAP, PMC4242425)
    "glucose_or_per_10": 1.07,
    "glucose_ref_mgdl": 110,
    # Systemic rise during infection: ~+4 mg/dL non-diabetic (103 vs 99,
    # PMC12952634), +15-20 mg/dL in type 1 diabetes (PMC8418789,
    # PMC11917402). Our cohort is normal/prediabetic -> mean +8
    "blood_glucose_rise": (8.0, 4.0),
    # Bigger spikes during infection (CV 37.3 -> 39.6%, PMC8418789)
    "glucose_spike_amplify": 0.15,
    # Wound fluid lags blood by ~4 h (Gao 2023) and is lower than serum
    # (Trengove 1996; ratio itself is ASSUMPTION)
    "wound_glucose_lag_h": 4.0,
    "wound_serum_ratio": (0.5, 0.8),
    # Bacteria consume wound glucose: >35% drop after infection (Gao 2023)
    "wound_glucose_drop": (0.40, 0.10),
    "wound_glucose_noise_frac": 0.03,
}


def sigmoid_rise(t, onset, lag, t_peak):
    """0 before onset+lag, smooth S-curve reaching ~1 at onset+lag+t_peak."""
    x = (t - (onset + lag)) / max(t_peak, 1.0)
    x = np.clip(x, 0, None)
    return 1 - np.exp(-4.0 * x ** 2)


def simulate_wound(wid, hours, rng, pid, person):
    n = len(hours)
    wtype = "chronic" if rng.random() < P["frac_chronic"] else "acute"
    bg = build_trace(person, n, rng)                      # real glucose, mg/dL
    # higher personal glucose -> higher infection odds
    base_odds = P["frac_infected"] / (1 - P["frac_infected"])
    odds = base_odds * P["glucose_or_per_10"] ** ((bg.mean() - P["glucose_ref_mgdl"]) / 10)
    infected = rng.random() < odds / (1 + odds)
    if infected:
        outcome = "infected"
        course = "stalled"
    else:
        outcome = "stalled" if rng.random() < P["frac_stalled_of_uninfected"] else "healing"
        course = outcome
    days = hours / 24.0

    # ---- underlying physiology ------------------------------------------
    ph0 = rng.normal(*P["ph_base"][wtype])
    ph = ph0 + P["ph_slope_per_day"][course] * days

    t0 = rng.normal(*P["temp_base"])
    temp = t0 + P["temp_slope_per_day"][course] * days
    half_amp = rng.uniform(*P["temp_circadian_half_amp"])
    phase = 2 * np.pi * (hours - P["temp_circadian_peak_hour"]) / 24.0
    temp = temp + half_amp * np.cos(phase)

    z0 = max(2.0, rng.normal(*P["z_base"][wtype]))
    logz = np.log(z0) + P["z_log_growth_per_day"][course] * days

    onset = np.nan
    label = np.array(["normal"] * n, dtype=object)
    if infected:
        onset = rng.uniform(48, hours[-1] - 72)       # leave room to develop
        lag = rng.uniform(*P["lag_h"])
        tpk = rng.uniform(*P["time_to_peak_h"])
        s = sigmoid_rise(hours, onset, lag, tpk)

        dph = max(0.15, rng.normal(*P["ph_infection_rise"]))
        if rng.random() < P["ph_nonresponder_frac"]:
            dph = rng.uniform(0.0, 0.15)
        ph = ph + dph * s
        if rng.random() < P["staph_frac_of_infected"]:
            # transient acidification right after onset
            dip = np.exp(-0.5 * ((hours - (onset + 6)) / 4.0) ** 2)
            ph = ph - P["ph_staph_dip"] * rng.uniform(0.3, 1.0) * dip

        dT = max(0.4, rng.normal(*P["temp_infection_rise"]))
        temp = temp + dT * s

        dz = np.clip(rng.normal(*P["z_infection_drop"]), 0.05, 0.7)
        logz = logz + np.log(1 - dz) * s

        label[(hours >= onset) & (hours < onset + 24)] = "warning"
        label[hours >= onset + 24] = "infection"

    # ---- sensor effects ---------------------------------------------------
    artifact = np.zeros(n, dtype=bool)

    # dressing changes: pH sensor drift resets, fresh dressing is drier
    drift = np.zeros(n)
    t_next = rng.uniform(*P["dressing_change_h"])
    last = 0.0
    step = hours[1] - hours[0]
    walk = 0.0
    for i, h in enumerate(hours):
        if h >= t_next:
            last, walk = h, 0.0
            t_next = h + rng.uniform(*P["dressing_change_h"])
            artifact[i] = True
        walk += rng.normal(0, P["ph_drift_per_h"] * np.sqrt(step))
        drift[i] = walk
        # fresh dressing: impedance briefly higher, decays over ~6 h
        logz[i] += 0.3 * np.exp(-(h - last) / 6.0) if last > 0 else 0.0
    ph = ph + drift

    # showers: temp drop + wetter
    for d in range(int(np.ceil(hours[-1] / 24))):
        if rng.random() < P["shower_prob_per_day"]:
            sh = d * 24 + rng.choice([rng.uniform(6, 9), rng.uniform(19, 22)])
            dt = hours - sh
            m = (dt >= 0) & (dt < 3)
            temp[m] -= P["shower_temp_drop"] * np.exp(-dt[m] / 0.5)
            logz[m] += np.log(1 + P["z_shower_frac"]) * np.exp(-dt[m] / 1.0)
            artifact |= (dt >= 0) & (dt < 1)

    # patch peeling off: temp toward ambient, open-circuit impedance, pH junk
    if rng.random() < P["detach_prob_per_wound"]:
        st = rng.uniform(24, hours[-1] - 12)
        m = (hours >= st) & (hours < st + rng.uniform(*P["detach_duration_h"]))
        temp[m] = P["ambient_temp"] + 0.5 * (temp[m] - P["ambient_temp"])
        logz[m] = np.log(rng.uniform(200, 800))
        ph[m] = rng.uniform(5.0, 9.0) + rng.normal(0, 0.3, m.sum())
        artifact |= m

    # ---- glucose ---------------------------------------------------------
    step = hours[1] - hours[0]
    if infected:
        gmean = bg.mean()
        bg = gmean + (bg - gmean) * (1 + P["glucose_spike_amplify"] * s)
        bg = bg + max(0.0, rng.normal(*P["blood_glucose_rise"])) * s
    # wound fluid: lagged (exponential smoothing), diluted, consumed by bacteria
    alpha = step / (P["wound_glucose_lag_h"] + step)
    wg = np.empty(n)
    wg[0] = bg[0]
    for i in range(1, n):
        wg[i] = wg[i - 1] + alpha * (bg[i] - wg[i - 1])
    wg = wg / 18.0 * rng.uniform(*P["wound_serum_ratio"])   # mg/dL -> mM
    if infected:
        drop = np.clip(rng.normal(*P["wound_glucose_drop"]), 0.2, 0.7)
        wg = wg * (1 - drop * s)
    wg = wg * (1 + rng.normal(0, P["wound_glucose_noise_frac"], n))

    ph = ph + rng.normal(0, P["ph_noise"], n)
    temp = temp + rng.normal(0, P["temp_noise"], n)
    z = np.exp(logz) * (1 + rng.normal(0, P["z_noise_frac"], n))

    return pd.DataFrame({
        "wound_id": wid,
        "hour": hours,
        "ph": np.round(np.clip(ph, 3.5, 10.0), 3),
        "temp_c": np.round(temp, 2),
        "impedance_kohm": np.round(z, 2),
        "blood_glucose_mgdl": np.round(bg, 1),
        "wound_glucose_mM": np.round(wg, 2),
        "participant_id": pid,
        "hba1c": person["hba1c"],
        "wound_type": wtype,
        "outcome": outcome,
        "infection_onset_h": np.round(onset, 1),
        "artifact": artifact,
        "label": label,
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wounds", type=int, default=600)
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--step-min", type=int, default=30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="data/wound_timeseries.csv")
    a = ap.parse_args()

    rng = np.random.default_rng(a.seed)
    hours = np.arange(0, a.days * 24, a.step_min / 60.0)
    people = load_participants(a.step_min)
    pids = sorted(people)
    assign = rng.permutation(np.resize(pids, a.wounds))      # ~equal wounds per person
    df = pd.concat([simulate_wound(w, hours, rng, int(assign[w]), people[int(assign[w])])
                    for w in range(a.wounds)],
                   ignore_index=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    df.to_csv(a.out, index=False)

    print(f"wrote {len(df):,} rows, {a.wounds} wounds -> {a.out}")
    print(df.groupby("outcome")["wound_id"].nunique().to_string())
    print(df["label"].value_counts().to_string())


if __name__ == "__main__":
    main()
