# Power and heat budget

Sampling every 5 min. Battery usable fraction 0.8.

## 1. Sensing-only battery life

| Load | Average current (uA) |
|---|---|
| nRF52832 sleep + RTC | 1.9 |
| BLE link (1 s interval) | 15.0 |
| MCU wake per sample | 0.7 |
| TMP117 x3 (one-shot, 8 avg) | 0.9 |
| pH buffer op-amp (always on) | 0.7 |
| FDC1004 moisture (power-gated) | 0.1 |
| AD5941 AFE (hibernate + 1 s scan) | 28.5 |
| LIS2DH12 accelerometer 10 Hz LP | 3.0 |
| AS7341 + 405 nm LED flash 0.2 s | 14.2 |
| MAX30102 heart rate, 10 s burst | 54.0 |

| Sensor set | Average current (uA) | 40 mAh | 100 mAh | 150 mAh | 300 mAh | 500 mAh |
|---|---|---|---|---|---|---|
| A pitch baseline | 19 | 69 days | 173 days | 260 days | 519 days | 865 days |
| B recommended | 22 | 60 days | 150 days | 225 days | 449 days | 749 days |
| C stretch | 118 | 11 days | 28 days | 42 days | 85 days | 141 days |

## 2. Therapy sessions per charge

| Session | Energy (mWh) | Equivalent mAh | 40 mAh | 100 mAh | 150 mAh | 300 mAh | 500 mAh |
|---|---|---|---|---|---|---|---|
| light only, 60 J/cm2 (human-trial dose), 40% system efficiency | 168 | 45 | 0.7 | 1.8 | 2.6 | 5.3 | 8.8 |
| optimistic: 15 min ultrasound + 60 J/cm2 light | 272 | 74 | 0.4 | 1.1 | 1.6 | 3.3 | 5.4 |
| mixed: 15 min ultrasound + 100 J/cm2 light | 474 | 128 | 0.2 | 0.6 | 0.9 | 1.9 | 3.1 |
| conservative: ultrasound + 250 J/cm2 light (pig MRSA dose) | 1684 | 455 | 0.1 | 0.2 | 0.3 | 0.5 | 0.9 |

For scale: a full day of sensing on set B costs 2.0 mWh, which is 1.2% of the smallest therapy session.

## 3. Skin heating from 405 nm light

Treated area 4 cm2, skin baseline 34 C, design ceiling 41 C.
Two columns per tissue type: light absorbed in tissue only, and light plus LED waste heat conducted into the same area (worst case, no heat sinking).

| Irradiance (mW/cm2) | Minutes for 60 J/cm2 | Minutes for 250 J/cm2 | normal skin (10 mL/100 g/min): light only / with LED heat | ischaemic foot (2 mL/100 g/min): light only / with LED heat |
|---|---|---|---|---|
| 5 | 200 | 833 | 34.7 C / 35.7 C | 35.0 C / 36.3 C |
| 10 | 100 | 417 | 35.5 C / 37.3 C | 36.1 C / 38.7 C |
| 20 | 50 | 208 | 36.9 C / 40.7 C | 38.1 C / 43.4 C OVER |
| 40 | 25 | 104 | 39.9 C / 47.4 C OVER | 42.2 C OVER / 52.7 C OVER |
| 100 | 10 | 42 | 48.7 C OVER / 67.4 C OVER | 54.6 C OVER / 80.8 C OVER |

- normal skin (10 mL/100 g/min): 0.15 C per mW/cm2 of absorbed heat, so the ceiling is reached at 48 mW/cm2 (light only) or 21 mW/cm2 (with LED heat).
- ischaemic foot (2 mL/100 g/min): 0.21 C per mW/cm2 of absorbed heat, so the ceiling is reached at 34 mW/cm2 (light only) or 15 mW/cm2 (with LED heat).

Sanity check against published data: a pig study at 40 mW/cm2 over a large area burned skin until active cooling was added, and the same model for a large area predicts 41.6 C from the light alone in well-perfused skin, before LED heat.
