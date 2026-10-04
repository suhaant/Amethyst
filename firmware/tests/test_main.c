/* Host tests for the PulsePatch firmware core. Build and run with `make test`. */
#include <stdio.h>
#include <string.h>

#include "app.h"
#include "fake_hal.h"
#include "impedance.h"
#include "ph.h"
#include "pp_config.h"
#include "pp_hal.h"
#include "telemetry.h"
#include "therapy.h"
#include "tmp117.h"

static int checks, failures;

#define CHECK(cond) do { checks++; if (!(cond)) { failures++; \
    printf("  FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); } } while (0)
#define CHECK_EQ(a, b) do { long va = (long)(a), vb = (long)(b); checks++; if (va != vb) { failures++; \
    printf("  FAIL %s:%d  %s = %ld, expected %ld\n", __FILE__, __LINE__, #a, va, vb); } } while (0)
#define CHECK_STR(a, b) do { checks++; if (strcmp((a), (b)) != 0) { failures++; \
    printf("  FAIL %s:%d\n    got      \"%s\"\n    expected \"%s\"\n", __FILE__, __LINE__, (a), (b)); } } while (0)

static const therapy_inputs_t SAFE = { .pad_attached = true, .sensors_ok = true, .hw_alert = false,
                                       .wound_mC = 34000, .battery_mV = 3900 };
#define MIN_MS(m) ((uint32_t)(m) * 60u * 1000u)
#define US_FULL 100000u                                   /* 0.1 W/cm2 */

static void test_tmp117_conversion(void)
{
    CHECK_EQ(tmp117_raw_to_mC(0x0C80), 25000);            /* datasheet: 0x0C80 = 25 C */
    CHECK_EQ(tmp117_raw_to_mC(0x4B00), 150000);           /* 0x4B00 = 150 C */
    CHECK_EQ(tmp117_raw_to_mC((int16_t)0xE700), -50000);  /* 0xE700 = -50 C */
    CHECK_EQ(tmp117_raw_to_mC(1), 8);                     /* one count = 7.8125 m-degrees, rounded */
    CHECK_EQ(tmp117_raw_to_mC(-1), -8);
    CHECK_EQ(tmp117_mC_to_raw(42000), 0x1500);
    CHECK_EQ(tmp117_mC_to_raw(-50000), (int16_t)0xE700);
    CHECK_EQ(tmp117_raw_to_mC(tmp117_mC_to_raw(37125)), 37125);
}

static void test_tmp117_init_and_read(void)
{
    int32_t mC = 0;
    fake_reset();
    CHECK_EQ(tmp117_init(0x48, 42000, 40000), 0);
    CHECK_EQ(fake.tmp[0].high, 0x1500);                   /* 42.0 C */
    CHECK_EQ(fake.tmp[0].low, 0x1400);                    /* 40.0 C */
    CHECK_EQ(fake.tmp[0].config, 0x0230);                 /* continuous, 8 averages, thermostat alert */
    CHECK_EQ(tmp117_read_mC(0x48, &mC), 0);
    CHECK_EQ(mC, 34250);
    fake.tmp[1].id = 0x0075;                              /* some other chip at that address */
    CHECK(tmp117_init(0x49, 42000, 40000) != 0);
    fake.tmp[2].present = false;
    CHECK(tmp117_init(0x4A, 42000, 40000) != 0);
    CHECK(tmp117_read_mC(0x4A, &mC) != 0);
}

static void test_impedance(void)
{
    CHECK_EQ(impedance_ohms(660000), 11750);              /* a quarter of the reference resistor */
    CHECK_EQ(impedance_ohms(1650000), 47000);             /* half the drive voltage = equal to the reference */
    CHECK_EQ(impedance_ohms(2853026), 300000);            /* dry or lifted */
    CHECK_EQ(impedance_ohms(3299000), PP_Z_OPEN_OHMS);    /* nothing connected */
    CHECK_EQ(impedance_ohms(3300000), PP_Z_OPEN_OHMS);
    CHECK_EQ(impedance_ohms(0), 0);                       /* shorted electrodes */
    CHECK_EQ(impedance_ohms(-5000), 0);
}

static void test_ultrasound_strength(void)
{
    CHECK_EQ(therapy_us_amplitude(0), 0);
    CHECK_EQ(therapy_us_amplitude(100000), 1000);         /* the assumed full-scale intensity */
    CHECK_EQ(therapy_us_amplitude(500000), 1000);         /* the model's 0.5 W/cm2 is out of reach: clamped */
    CHECK_EQ(therapy_us_amplitude(25000), 500);           /* a quarter of the intensity = half the amplitude */
    CHECK_EQ(therapy_us_amplitude(49000), 700);
    CHECK_EQ(therapy_us_amplitude(10000), 500);           /* below what the boost can do: held at the minimum */
}

static void test_ph(void)
{
    ph_cal_t ideal = { 0, -59160 };
    ph_cal_t pad = { 12000, -52000 };                     /* a real electrode: offset and weaker slope */
    CHECK_EQ(ph_from_uv(&ideal, 0), 7000);
    CHECK_EQ(ph_from_uv(&ideal, 59160), 6000);            /* more positive = more acidic */
    CHECK_EQ(ph_from_uv(&ideal, -118320), 9000);
    CHECK_EQ(ph_from_uv(&ideal, 2000000), 0);             /* clamped */
    CHECK_EQ(ph_from_uv(&ideal, -2000000), 14000);
    CHECK_EQ(ph_from_uv(&pad, 12000), 7000);
    CHECK_EQ(ph_from_uv(&pad, 12000 - 52000), 8000);
}

static void test_telemetry_format(void)
{
    char line[96], tiny[8];
    pp_reading_t r = { .t_s = 1800, .ph_milli = 7412, .temp_wound_mC = 34250, .temp_ref_mC = 32875,
                       .temp_ambient_mC = -1500, .impedance_ohm = 9720, .battery_mV = 3912,
                       .pad_id_kohm = 47, .faults = 0x0009 };
    size_t n = telemetry_format_reading(&r, line, sizeof line);
    CHECK_STR(line, "R,1800,7.412,34.250,9.720,32.875,-1.500,3912,47,0009\n");
    CHECK_EQ(n, strlen(line));
    telemetry_format_event('E', 3, 12000, 0, line, sizeof line);
    CHECK_STR(line, "E,3,12000,0\n");
    telemetry_format_event('A', -1, 0, 0, line, sizeof line);
    CHECK_STR(line, "A,-1,0,0\n");
    n = telemetry_format_reading(&r, tiny, sizeof tiny);  /* too small: truncated, still terminated */
    CHECK(n > sizeof tiny);
    CHECK_EQ(strlen(tiny), sizeof tiny - 1);
}

static void test_command_parse(void)
{
    command_t c = telemetry_parse("T,4.0,0.10,20.0,10.0\n");   /* a plan straight from risk_to_dose.py */
    CHECK_EQ(c.type, CMD_THERAPY);
    CHECK_EQ(c.us_ms, MIN_MS(4));
    CHECK_EQ(c.us_uw_cm2, 100000);
    CHECK_EQ(c.led_ms, MIN_MS(20));
    CHECK_EQ(c.led_uw_cm2, 10000);
    c = telemetry_parse("T,0,0,6.7,10");
    CHECK_EQ(c.type, CMD_THERAPY);
    CHECK_EQ(c.us_ms, 0);
    CHECK_EQ(c.led_ms, 402000);
    CHECK_EQ(telemetry_parse("S\r\n").type, CMD_STOP);
    CHECK_EQ(telemetry_parse("?").type, CMD_READ);
    CHECK_EQ(telemetry_parse("").type, CMD_INVALID);
    CHECK_EQ(telemetry_parse("T,4.0,20.0,10.0").type, CMD_INVALID);   /* missing field */
    CHECK_EQ(telemetry_parse("T,-4,0.1,20,10").type, CMD_INVALID);        /* negative */
    CHECK_EQ(telemetry_parse("T,4,0.1,20,10,99").type, CMD_INVALID);      /* extra field */
    CHECK_EQ(telemetry_parse("T,99999,0.1,1,1").type, CMD_INVALID);       /* absurd value */
    CHECK_EQ(telemetry_parse("X").type, CMD_INVALID);
}

static void test_therapy_interlocks(void)
{
    therapy_t t;
    therapy_inputs_t in;
    fake_reset();
    therapy_init(&t);
    in = SAFE; in.pad_attached = false;
    CHECK_EQ(therapy_start(&t, 0, MIN_MS(4), US_FULL, MIN_MS(10), 10000, &in), TH_ERR_NO_PAD);
    in = SAFE; in.sensors_ok = false;
    CHECK_EQ(therapy_start(&t, 0, MIN_MS(4), US_FULL, MIN_MS(10), 10000, &in), TH_ERR_SENSOR);
    in = SAFE; in.wound_mC = 41000;
    CHECK_EQ(therapy_start(&t, 0, MIN_MS(4), US_FULL, MIN_MS(10), 10000, &in), TH_ERR_HOT);
    in = SAFE; in.hw_alert = true;
    CHECK_EQ(therapy_start(&t, 0, MIN_MS(4), US_FULL, MIN_MS(10), 10000, &in), TH_ERR_HOT);
    in = SAFE; in.battery_mV = 3499;
    CHECK_EQ(therapy_start(&t, 0, MIN_MS(4), US_FULL, MIN_MS(10), 10000, &in), TH_ERR_BATTERY);
    CHECK_EQ(therapy_start(&t, 0, 0, US_FULL, 0, 0, &SAFE), TH_ERR_NOTHING);
    CHECK_EQ(t.state, TH_IDLE);
    CHECK_EQ(fake.us_amplitude, 0);
    CHECK_EQ(fake.led_permille, 0);
    CHECK_EQ(therapy_start(&t, 0, MIN_MS(4), US_FULL, MIN_MS(10), 10000, &SAFE), TH_OK);
    CHECK_EQ(therapy_start(&t, 1, MIN_MS(4), US_FULL, MIN_MS(10), 10000, &SAFE), TH_ERR_BUSY);
}

static void test_therapy_sequence_and_caps(void)
{
    therapy_t t;
    uint32_t now;
    fake_reset();
    therapy_init(&t);
    /* Ask for more than the caps allow: 30 min ultrasound, 50 mW/cm2 light. */
    CHECK_EQ(therapy_start(&t, 0, MIN_MS(30), US_FULL, MIN_MS(10), 50000, &SAFE), TH_OK);
    CHECK_EQ(t.us_ms, PP_US_MAX_MS);
    CHECK_EQ(t.led_uw_cm2, PP_LED_MAX_UW_CM2);
    CHECK_EQ(t.state, TH_ULTRASOUND);
    CHECK(fake.us_amplitude > 0);
    CHECK_EQ(fake.led_permille, 0);
    CHECK_EQ(therapy_tick(&t, 250, &SAFE), TH_END_NONE);
    CHECK(fake.us_amplitude > 0);                                    /* first half of the 1 s burst */
    CHECK_EQ(therapy_tick(&t, 750, &SAFE), TH_END_NONE);
    CHECK_EQ(fake.us_amplitude, 0);                                   /* second half */
    CHECK_EQ(therapy_tick(&t, PP_US_MAX_MS - 1, &SAFE), TH_END_NONE);
    CHECK_EQ(t.state, TH_ULTRASOUND);
    CHECK_EQ(therapy_tick(&t, PP_US_MAX_MS, &SAFE), TH_END_NONE);
    CHECK_EQ(t.state, TH_LIGHT);                          /* ultrasound done, light begins */
    CHECK_EQ(fake.us_amplitude, 0);
    CHECK_EQ(fake.led_permille, 333);                     /* 10 of an assumed 30 mW/cm2 full scale */
    for (now = PP_US_MAX_MS + 1000; now < PP_US_MAX_MS + MIN_MS(10); now += 1000) {
        CHECK_EQ(therapy_tick(&t, now, &SAFE), TH_END_NONE);
    }
    CHECK_EQ(therapy_tick(&t, PP_US_MAX_MS + MIN_MS(10), &SAFE), TH_END_DONE);
    CHECK_EQ(t.state, TH_IDLE);
    CHECK_EQ(fake.led_permille, 0);
    CHECK_EQ(t.dose_uj_cm2, 6000000);                     /* 10 mW/cm2 x 600 s = 6 J/cm2 */
    CHECK_EQ(therapy_tick(&t, now + 5000, &SAFE), TH_END_NONE);   /* idle stays idle */
}

static void test_therapy_daily_cap(void)
{
    therapy_t t;
    uint32_t start = 0;
    fake_reset();
    therapy_init(&t);
    /* 36 J/cm2 at 10 mW/cm2 is exactly 60 minutes. Ask for 45, then 45 again. */
    CHECK_EQ(therapy_start(&t, start, 0, US_FULL, MIN_MS(45), 10000, &SAFE), TH_OK);
    CHECK_EQ(therapy_tick(&t, start + MIN_MS(45), &SAFE), TH_END_DONE);
    CHECK_EQ(t.dose_uj_cm2, 27000000);
    start = MIN_MS(120);
    CHECK_EQ(therapy_start(&t, start, 0, US_FULL, MIN_MS(45), 10000, &SAFE), TH_OK);
    CHECK_EQ(t.led_ms, MIN_MS(15));                       /* shortened to what is left today */
    CHECK_EQ(therapy_tick(&t, start + MIN_MS(15), &SAFE), TH_END_DONE);
    CHECK_EQ(t.dose_uj_cm2, PP_LED_DAILY_CAP_UJ_CM2);
    CHECK_EQ(therapy_start(&t, MIN_MS(180), 0, US_FULL, MIN_MS(5), 10000, &SAFE), TH_ERR_DAILY_CAP);
    /* Ultrasound is still allowed once the light cap is hit. */
    CHECK_EQ(therapy_start(&t, MIN_MS(180), MIN_MS(4), US_FULL, MIN_MS(5), 10000, &SAFE), TH_OK);
    CHECK_EQ(t.led_ms, 0);
    therapy_stop(&t, MIN_MS(181));
    /* Next day the allowance is back. */
    CHECK_EQ(therapy_start(&t, PP_DAY_MS + 1000, 0, US_FULL, MIN_MS(5), 10000, &SAFE), TH_OK);
    CHECK_EQ(t.dose_uj_cm2, 0);
}

static void test_therapy_aborts(void)
{
    therapy_t t;
    therapy_inputs_t in;
    fake_reset();

    therapy_init(&t);
    CHECK_EQ(therapy_start(&t, 0, 0, US_FULL, MIN_MS(10), 10000, &SAFE), TH_OK);
    in = SAFE; in.wound_mC = 41200;                       /* wound warms past the limit after 2 minutes */
    CHECK_EQ(therapy_tick(&t, MIN_MS(2), &in), TH_END_OVERTEMP);
    CHECK_EQ(fake.led_permille, 0);
    CHECK_EQ(t.state, TH_IDLE);
    CHECK_EQ(t.dose_uj_cm2, 1200000);                     /* the 2 minutes delivered still count */

    therapy_init(&t);
    CHECK_EQ(therapy_start(&t, 0, MIN_MS(4), US_FULL, 0, 0, &SAFE), TH_OK);
    in = SAFE; in.hw_alert = true;
    CHECK_EQ(therapy_tick(&t, 100, &in), TH_END_ALERT);
    CHECK_EQ(fake.us_amplitude, 0);

    therapy_init(&t);
    CHECK_EQ(therapy_start(&t, 0, MIN_MS(4), US_FULL, 0, 0, &SAFE), TH_OK);
    in = SAFE; in.pad_attached = false;
    CHECK_EQ(therapy_tick(&t, 100, &in), TH_END_PAD);

    therapy_init(&t);
    CHECK_EQ(therapy_start(&t, 0, MIN_MS(4), US_FULL, 0, 0, &SAFE), TH_OK);
    in = SAFE; in.sensors_ok = false;
    CHECK_EQ(therapy_tick(&t, 100, &in), TH_END_SENSOR);
}

static void test_app_sampling(void)
{
    app_t app;
    fake_reset();
    app_init(&app, 0);
    CHECK_EQ(fake.lines, 1);                              /* first reading goes out at start-up */
    CHECK_EQ(fake.tmp[0].high, 0x1500);                   /* alert limits were programmed */
    CHECK_EQ(fake.tmp[2].high, tmp117_mC_to_raw(PP_AMBIENT_ALERT_HIGH_MC));
    CHECK_STR(fake.reading_line, "R,0,7.000,34.250,11.750,32.875,24.500,3900,46,0000\n");
    app_tick(&app, PP_SAMPLE_PERIOD_MS - 1);
    CHECK_EQ(fake.lines, 1);                              /* nothing until 30 minutes are up */
    fake_set_temp_mC(0, 36500);
    app_tick(&app, PP_SAMPLE_PERIOD_MS);
    CHECK_EQ(fake.lines, 2);
    CHECK(strncmp(fake.reading_line, "R,1800,7.000,36.500,", 20) == 0);
    app_tick(&app, 2 * PP_SAMPLE_PERIOD_MS + 500);
    CHECK_EQ(fake.lines, 3);
}

static void test_app_faults(void)
{
    app_t app;
    fake_reset();
    fake.tmp[1].present = false;                          /* reference sensor missing */
    fake.moist_fail = true;                               /* moisture measurement failing */
    fake.adc_uv[PP_ADC_PAD_ID] = 3290000;                 /* nothing pulling the pad ID line down */
    app_init(&app, 0);
    CHECK_EQ(app.last.faults, PP_FAULT_TEMP_REF | PP_FAULT_MOISTURE);
    CHECK_EQ(app.last.pad_id_kohm, -1);
    CHECK(strstr(fake.reading_line, ",-1,000A\n") != NULL);
    app_command(&app, 1000, "T,4.0,0.1,10.0,10.0");
    CHECK_STR(fake.last_line, "A,2,0,0\n");               /* refused: no pad */
    CHECK_EQ(fake.us_amplitude, 0);
}

static void test_app_patch_lifted(void)
{
    app_t app;
    fake_reset();
    fake.moist_swing_uv = 2853026;                        /* 300 kOhm: pad attached but not on skin */
    app_init(&app, 0);
    CHECK(strstr(fake.reading_line, ",300.000,") != NULL);
    app_command(&app, 1000, "T,4.0,0.1,10.0,10.0");
    CHECK_STR(fake.last_line, "A,2,0,0\n");               /* refused, same rule as the model's LIFTED_KOHM */
    fake.moist_swing_uv = 660000;                         /* pressed back down */
    app_command(&app, 2000, "T,4.0,0.1,10.0,10.0");
    CHECK_STR(fake.last_line, "A,0,240000,600000\n");
    fake.moist_swing_uv = 3299000;                        /* peels off mid-session */
    app_tick(&app, 5000);
    CHECK(strncmp(fake.last_line, "E,6,", 4) == 0);
    CHECK_EQ(fake.us_amplitude, 0);
}

static void test_app_therapy_session(void)
{
    app_t app;
    uint32_t now;
    fake_reset();
    app_init(&app, 0);
    app_command(&app, 1000, "T,4.0,0.025,2.0,10.0\n");
    CHECK_STR(fake.last_line, "A,0,240000,120000\n");
    CHECK(fake.status_led);
    CHECK_EQ(fake.us_amplitude, 500);                     /* 0.025 W/cm2 = a quarter of full scale */
    for (now = 2000; now <= 1000 + MIN_MS(4); now += 1000) {
        app_tick(&app, now);
    }
    CHECK_EQ(app.therapy.state, TH_LIGHT);
    CHECK_EQ(fake.led_permille, 333);
    fake_set_temp_mC(0, 41500);                           /* wound overheats during the light phase */
    for (; now <= 1000 + MIN_MS(4) + 5000; now += 1000) {
        app_tick(&app, now);
    }
    CHECK_EQ(app.therapy.state, TH_IDLE);
    CHECK_EQ(fake.led_permille, 0);
    CHECK(!fake.status_led);
    CHECK(strncmp(fake.last_line, "E,3,", 4) == 0);       /* ended: over temperature */

    fake_set_temp_mC(0, 34000);
    app_command(&app, now, "T,4.0,0.1,0,0");
    CHECK_STR(fake.last_line, "A,0,240000,0\n");
    app_command(&app, now + 500, "S");
    CHECK(strncmp(fake.last_line, "E,2,", 4) == 0);       /* ended: stopped */
    CHECK_EQ(fake.us_amplitude, 0);
    app_command(&app, now + 600, "hello");
    CHECK_STR(fake.last_line, "A,-1,0,0\n");
    app_command(&app, now + 700, "?");
    CHECK(fake.last_line[0] == 'R');
}

int main(void)
{
    static const struct { const char *name; void (*run)(void); } tests[] = {
        { "tmp117 conversion", test_tmp117_conversion },
        { "tmp117 init and read", test_tmp117_init_and_read },
        { "moisture impedance", test_impedance },
        { "ultrasound strength", test_ultrasound_strength },
        { "pH conversion", test_ph },
        { "telemetry format", test_telemetry_format },
        { "command parsing", test_command_parse },
        { "therapy interlocks", test_therapy_interlocks },
        { "therapy sequence and caps", test_therapy_sequence_and_caps },
        { "therapy daily light cap", test_therapy_daily_cap },
        { "therapy aborts", test_therapy_aborts },
        { "app 30-minute sampling", test_app_sampling },
        { "app sensor faults", test_app_faults },
        { "app patch lifted off skin", test_app_patch_lifted },
        { "app therapy session", test_app_therapy_session },
    };
    for (size_t i = 0; i < sizeof tests / sizeof tests[0]; i++) {
        int before = failures;
        tests[i].run();
        printf("%s  %s\n", failures == before ? "ok  " : "FAIL", tests[i].name);
    }
    printf("\n%d checks, %d failed\n", checks, failures);
    return failures ? 1 : 0;
}
