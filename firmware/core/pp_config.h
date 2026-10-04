/* PulsePatch firmware settings. Units are integers: milli-degrees C, milli-pH, femtofarads, millivolts. */
#ifndef PP_CONFIG_H
#define PP_CONFIG_H

/* Sampling: one reading every 30 minutes, the step the infection model was trained on. */
#define PP_SAMPLE_PERIOD_MS       (30u * 60u * 1000u)
#define PP_THERAPY_CHECK_MS       2000u        /* sensor re-check interval while therapy runs */

/* I2C addresses (set by each TMP117's ADD0 pin on the board). */
#define PP_ADDR_TEMP_WOUND        0x48
#define PP_ADDR_TEMP_REFERENCE    0x49
#define PP_ADDR_TEMP_AMBIENT      0x4A

/* Temperature safety. Firmware stops therapy at 41 C; the TMP117 alert pins cut it in hardware at 42 C. */
#define PP_WOUND_MAX_MC           41000
#define PP_ALERT_HIGH_MC          42000
#define PP_ALERT_LOW_MC           40000
#define PP_AMBIENT_ALERT_HIGH_MC  60000
#define PP_AMBIENT_ALERT_LOW_MC   55000

/* Therapy caps. These mirror risk_to_dose.py in the ML pipeline, enforced again here. */
#define PP_US_MAX_MS              (10u * 60u * 1000u)   /* US_LF max_min = 10 */
#define PP_LED_MAX_UW_CM2         10000u                /* LED_IRRADIANCE_MW = 10 mW/cm2 */
#define PP_LED_DAILY_CAP_UJ_CM2   36000000u             /* LED_DAILY_CAP_J = 36 J/cm2 */
#define PP_DAY_MS                 86400000u
#define PP_US_BURST_PERIOD_MS     1000u                 /* ultrasound pulses 500 ms on, 500 ms off */
#define PP_US_BURST_ON_MS         500u
#define PP_BATTERY_MIN_MV         3500

/* Moisture: electrode impedance at 1 kHz through a 47k reference resistor driven at 3.3 V. */
#define PP_Z_REF_OHMS             47000
#define PP_Z_DRIVE_UV             3300000
#define PP_Z_OPEN_OHMS            9999000
#define PP_LIFTED_OHMS            150000                /* LIFTED_KOHM = 150: patch not on skin, no therapy */

/* ASSUMED, not measured: ultrasound intensity at the wound with the drive at its full 10 V. Measure and replace.
 * The boost cannot go below about 5 V, so the weakest setting is half amplitude (a quarter of the intensity). */
#define PP_US_FULL_SCALE_UW_CM2   100000u
#define PP_US_MIN_AMPLITUDE       500u

/* ASSUMED, not measured: irradiance at the wound with the LED string at 100% duty. Measure and replace. */
#define PP_LED_FULL_SCALE_UW_CM2  30000u

/* Pad detection: 100k pull-up to 3.3 V on the board, ID resistor to ground inside the pad. */
#define PP_PAD_PULLUP_KOHM        100
#define PP_SUPPLY_UV              3300000
#define PP_PAD_ABSENT_UV          3000000

/* pH electrode calibration defaults: ideal slope at 25 C, zero offset at pH 7. Calibrate per pad. */
#define PP_PH_UV_AT_PH7           0
#define PP_PH_UV_PER_PH           (-59160)

#endif
