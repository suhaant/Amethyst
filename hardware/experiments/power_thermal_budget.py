#!/usr/bin/env python3
"""Power and heat budget for the PulsePatch pod.

Three questions:
  1. How long does a battery last on sensing alone, per sensor set?
  2. How many therapy sessions does a battery hold?
  3. How much 405 nm irradiance can skin take before the patch overheats it?

Inputs come from datasheets and from research/raw/C-therapy-hardware.md.
Values marked ASSUMED are engineering estimates, not sourced numbers.

Usage: python3 power_thermal_budget.py
Output: out/power_thermal_results.md
"""
import math
from pathlib import Path

OUT = Path(__file__).parent / "out"
SAMPLE_PERIOD_S = 300          # one reading every 5 minutes, as in the pitch
V_BATT = 3.7
USABLE = 0.8                   # ASSUMED usable fraction of nominal capacity
CELLS_MAH = [40, 100, 150, 300, 500]

# name: (always-on current in uA, charge per sample in uC = active uA x active s)
# Datasheet typical values; see research/02-parts-and-kicad.md for sources.
LOADS = {
    "nRF52832 sleep + RTC":            (1.9, 0),
    "BLE link (1 s interval)":         (15.0, 0),        # ASSUMED; check with Nordic Online Power Profiler
    "MCU wake per sample":             (0, 4000 * 0.05),
    "TMP117 x3 (one-shot, 8 avg)":     (3 * 0.25, 3 * 135 * 0.124),
    "pH buffer op-amp (always on)":    (0.65, 0),
    "FDC1004 moisture (power-gated)":  (0, 750 * 0.05),
    "AD5941 AFE (hibernate + 1 s scan)": (8.5, 6000 * 1.0),   # ASSUMED scan time and current
    "LIS2DH12 accelerometer 10 Hz LP": (3.0, 0),
    "AS7341 + 405 nm LED flash 0.2 s": (0.7, (210 + 20000) * 0.2),
    "MAX30102 heart rate, 10 s burst": (0.7, (600 + 1000) * 10.0),
}
SETS = {
    "A pitch baseline": ["nRF52832 sleep + RTC", "BLE link (1 s interval)", "MCU wake per sample",
                         "TMP117 x3 (one-shot, 8 avg)", "pH buffer op-amp (always on)", "FDC1004 moisture (power-gated)"],
    "B recommended": ["nRF52832 sleep + RTC", "BLE link (1 s interval)", "MCU wake per sample",
                      "TMP117 x3 (one-shot, 8 avg)", "pH buffer op-amp (always on)", "FDC1004 moisture (power-gated)",
                      "LIS2DH12 accelerometer 10 Hz LP"],
    "C stretch": ["nRF52832 sleep + RTC", "BLE link (1 s interval)", "MCU wake per sample",
                  "TMP117 x3 (one-shot, 8 avg)", "AD5941 AFE (hibernate + 1 s scan)",
                  "LIS2DH12 accelerometer 10 Hz LP", "AS7341 + 405 nm LED flash 0.2 s",
                  "MAX30102 heart rate, 10 s burst"],
}

# Therapy session energy in mWh (research/raw/C-therapy-hardware.md section 5, 4 cm2 treated area).
SESSIONS = {
    "light only, 60 J/cm2 (human-trial dose), 40% system efficiency": 168,
    "optimistic: 15 min ultrasound + 60 J/cm2 light": 272,
    "mixed: 15 min ultrasound + 100 J/cm2 light": 474,
    "conservative: ultrasound + 250 J/cm2 light (pig MRSA dose)": 1684,
}

# Heat model: uniform heat flux on a disc of skin, tissue cooled by blood perfusion (Pennes bioheat, steady state).
# Centre temperature rise = (q / k) * d * (1 - exp(-a / d)), d = sqrt(k / (perfusion * rho_b * c_b)).
K_TISSUE = 0.4                 # W/m/K, skin and subcutaneous tissue (ASSUMED mid value, range 0.3 to 0.5)
RHO_C_BLOOD = 1050 * 3600      # J/m3/K
PERFUSION = {"normal skin (10 mL/100 g/min)": 10, "ischaemic foot (2 mL/100 g/min)": 2}   # ASSUMED representative values
TREATED_CM2 = 4.0
SKIN_BASELINE_C = 34.0         # ASSUMED skin temperature under a dressing
CEILING_C = 41.0               # design ceiling; IEC 60601-1 allows 43 C for contact of 10 min or more
LED_WASTE_PER_OPTICAL = 1 / (0.55 * 0.80) - 1   # LED heat per unit of light delivered (55% wall-plug, 80% coupling)
IRRADIANCES = [5, 10, 20, 40, 100]              # mW/cm2
DOSES = [60, 250]                               # J/cm2


def sensing_current_ua(names):
    return sum(LOADS[n][0] + LOADS[n][1] / SAMPLE_PERIOD_S for n in names)


def delta_t(flux_w_m2, perfusion_ml):
    w = perfusion_ml / 100 / 60 * 1.1          # mL blood per mL tissue per second (tissue density 1.1 g/mL)
    depth = math.sqrt(K_TISSUE / (w * RHO_C_BLOOD))
    radius = math.sqrt(TREATED_CM2 * 1e-4 / math.pi)
    return flux_w_m2 / K_TISSUE * depth * (1 - math.exp(-radius / depth))


def main():
    OUT.mkdir(exist_ok=True)
    md = ["# Power and heat budget", "", f"Sampling every {SAMPLE_PERIOD_S // 60} min. Battery usable fraction {USABLE}.", ""]

    md += ["## 1. Sensing-only battery life", "", "| Load | Average current (uA) |", "|---|---|"]
    for name, (idle, charge) in LOADS.items():
        md.append(f"| {name} | {idle + charge / SAMPLE_PERIOD_S:.1f} |")
    md += ["", "| Sensor set | Average current (uA) | " + " | ".join(f"{c} mAh" for c in CELLS_MAH) + " |",
           "|---|---|" + "---|" * len(CELLS_MAH)]
    for name, loads in SETS.items():
        ua = sensing_current_ua(loads)
        days = [c * USABLE * 1000 / ua / 24 for c in CELLS_MAH]
        md.append(f"| {name} | {ua:.0f} | " + " | ".join(f"{d:.0f} days" for d in days) + " |")
    md.append("")

    md += ["## 2. Therapy sessions per charge", "",
           "| Session | Energy (mWh) | Equivalent mAh | " + " | ".join(f"{c} mAh" for c in CELLS_MAH) + " |",
           "|---|---|---|" + "---|" * len(CELLS_MAH)]
    for name, mwh in SESSIONS.items():
        per_cell = [c * V_BATT * USABLE / mwh for c in CELLS_MAH]
        md.append(f"| {name} | {mwh} | {mwh / V_BATT:.0f} | " + " | ".join(f"{n:.1f}" for n in per_cell) + " |")
    one_day_sensing = sensing_current_ua(SETS["B recommended"]) * 24 / 1000 * V_BATT
    md += ["", f"For scale: a full day of sensing on set B costs {one_day_sensing:.1f} mWh, "
               f"which is {one_day_sensing / 168 * 100:.1f}% of the smallest therapy session.", ""]

    md += ["## 3. Skin heating from 405 nm light", "",
           f"Treated area {TREATED_CM2:.0f} cm2, skin baseline {SKIN_BASELINE_C:.0f} C, design ceiling {CEILING_C:.0f} C.",
           "Two columns per tissue type: light absorbed in tissue only, and light plus LED waste heat conducted into the same area (worst case, no heat sinking).", "",
           "| Irradiance (mW/cm2) | " + " | ".join(f"Minutes for {d} J/cm2" for d in DOSES) + " | "
           + " | ".join(f"{p}: light only / with LED heat" for p in PERFUSION) + " |",
           "|---|" + "---|" * (len(DOSES) + len(PERFUSION))]
    for e in IRRADIANCES:
        flux = e * 10.0      # mW/cm2 -> W/m2
        cells = []
        for perf in PERFUSION.values():
            a, b = delta_t(flux, perf), delta_t(flux * (1 + LED_WASTE_PER_OPTICAL), perf)
            mark = lambda t: f"{SKIN_BASELINE_C + t:.1f} C" + (" OVER" if SKIN_BASELINE_C + t > CEILING_C else "")
            cells.append(f"{mark(a)} / {mark(b)}")
        md.append(f"| {e} | " + " | ".join(f"{d * 1000 / e / 60:.0f}" for d in DOSES) + " | " + " | ".join(cells) + " |")
    md.append("")
    for label, perf in PERFUSION.items():
        per_unit = delta_t(10.0, perf)     # C per mW/cm2
        limit = (CEILING_C - SKIN_BASELINE_C) / per_unit
        md.append(f"- {label}: {per_unit:.2f} C per mW/cm2 of absorbed heat, so the ceiling is reached at "
                  f"{limit:.0f} mW/cm2 (light only) or {limit / (1 + LED_WASTE_PER_OPTICAL):.0f} mW/cm2 (with LED heat).")
    md += ["", "Sanity check against published data: a pig study at 40 mW/cm2 over a large area burned skin until active cooling was added, "
               f"and the same model for a large area predicts {SKIN_BASELINE_C + 400 / K_TISSUE * math.sqrt(K_TISSUE / (10 / 100 / 60 * 1.1 * RHO_C_BLOOD)):.1f} C "
               "from the light alone in well-perfused skin, before LED heat.", ""]
    (OUT / "power_thermal_results.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
