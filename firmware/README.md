# PulsePatch firmware

C firmware for the PulsePatch board (`hardware/kicad/pulsepatch/`). It reads the sensors every 30 minutes, sends each reading to a phone or gateway as a text line, and runs light and ultrasound sessions on command with hard safety limits.

## Layout

| Folder | What is in it | Status |
|---|---|---|
| `core/` | All the logic: sensor drivers, pH conversion, therapy controller, message format, scheduler. No hardware dependencies. | Tested on a computer; compiles for the nRF52832 |
| `tests/` | A simulated board and the test suite | 15 tests, all passing |
| `port/zephyr/` | Glue that runs `core/` on the real chip with the nRF Connect SDK | **Not built or run yet** |

## Run the tests

```
cd firmware
make test        # builds core/ against the simulated board and runs 15 tests
make arm-check   # compiles core/ for the nRF52832 with arm-none-eabi-gcc
```

## Messages

Patch to host:

```
R,<uptime_s>,<ph>,<temp_wound_c>,<impedance_kohm>,<temp_ref_c>,<temp_ambient_c>,<battery_mv>,<pad_kohm>,<faults_hex>
A,<result>,<us_ms>,<led_ms>       answer to a T command; result 0 = started
E,<reason>,<dose_mj_cm2>,0        session ended; dose is today's light total
B,1,0,0                           the wearer pressed the button
```

Host to patch:

```
T,<us_40khz_min>,<us_40khz_w_cm2>,<led_405nm_min>,<led_405nm_mw_cm2>    start a session
S                                                      stop
?                                                      send a reading now
```

Result and reason codes are the enums in `core/therapy.h`. Fault bits are in `core/telemetry.h`.

## How it lines up with the ML and agent pipeline

The pipeline (`predict.py`, `risk_to_dose.py`, `wound_agent/` on the `agent-reasoning` branch) expects one row every 30 minutes and produces a session plan. The firmware matches that cadence and takes the plan's fields directly in the `T` command.

| Pipeline field | From the patch | Note |
|---|---|---|
| `ph` | `ph` | Needs per-pad calibration (`PP_PH_UV_AT_PH7`, `PP_PH_UV_PER_PH`) |
| `temp_c` | `temp_wound_c` | The patch also sends reference and ambient temperatures, which the model does not use yet |
| `impedance_kohm` | `impedance_kohm` | Measured between the two pad electrodes with a 1 kHz square wave, so it includes some harmonic content. Reads 9999 with nothing connected |
| `wound_glucose_mM`, `blood_glucose_mgdl` | Not from the patch | These come from the team's dataset, by design |
| `us_40khz_min` | Ultrasound phase length | The board drives a 30 kHz disc, the patch-sized one available |
| `us_40khz_w_cm2` | Drive strength | Adjustable from about a quarter to full output. Full output is assumed to be 0.1 W/cm² and is unmeasured; requests above it are clamped |
| `led_405nm_min`, `led_405nm_mw_cm2` | Light phase length and brightness | Brightness relies on an unmeasured calibration constant (below) |
| `us_1p5mhz_min` | **Not available** | No 1.5 MHz hardware on the board |
| "patch lifted" (impedance above 150 kΩ) | Same rule on the patch | The firmware refuses or stops therapy above 150 kΩ, or when no pad is detected |

## Safety limits enforced on the patch

These hold even if the host asks for more. The caps mirror `risk_to_dose.py`.

| Limit | Value | Where |
|---|---|---|
| Light brightness | 10 mW/cm² | `PP_LED_MAX_UW_CM2` |
| Light dose per day | 36 J/cm² | `PP_LED_DAILY_CAP_UJ_CM2` |
| Ultrasound per session | 10 minutes, pulsed 500 ms on / 500 ms off | `PP_US_MAX_MS` |
| Patch on skin | moisture impedance at or below 150 kΩ | `PP_LIFTED_OHMS` |
| Wound temperature, firmware stop | 41 °C | `PP_WOUND_MAX_MC` |
| Wound temperature, hardware cutoff | 42 °C, releases at 40 °C | written to the TMP117 sensors at start-up |
| No session without | a pad attached and on skin, a working wound temperature sensor, battery above 3.5 V | `core/therapy.c` |

## Not verified

- **Nothing has run on real hardware.** The tests use a simulated board.
- **`port/zephyr/` has never been compiled.** The nRF Connect SDK is not installed on the machine it was written on. Expect small fixes on the first build, and replace the DK overlay with a proper board definition.
- **`PP_LED_FULL_SCALE_UW_CM2` (30 mW/cm² at full current) is a guess.** Measure the real irradiance at the wound plane with a power meter and set it, or every light dose is wrong by that ratio.
- **`PP_US_FULL_SCALE_UW_CM2` (0.1 W/cm² at full drive) is also a guess.** It needs a hydrophone measurement.
- **Chip register values** (TMP117 configuration `0x0230`) come from memory of the datasheet and are checked only against the simulated chip, which was written from the same memory.
- **The daily dose resets on a 24-hour timer from power-on**, not at midnight, and the millisecond clock wraps after 49 days.
