#include "app.h"

#include "impedance.h"
#include "pp_config.h"
#include "pp_hal.h"
#include "tmp117.h"

static void send_event(char tag, int32_t a, int32_t b, int32_t c)
{
    char line[48];
    telemetry_format_event(tag, a, b, c, line, sizeof line);
    hal_link_write(line);
}

static void send_reading(const app_t *a)
{
    char line[96];
    telemetry_format_reading(&a->last, line, sizeof line);
    hal_link_write(line);
}

static void take_reading(app_t *a, uint32_t now_ms)
{
    pp_reading_t r = { 0 };
    int32_t uv;

    r.t_s = now_ms / 1000;
    if (tmp117_read_mC(PP_ADDR_TEMP_WOUND, &r.temp_wound_mC) != 0) {
        r.faults |= PP_FAULT_TEMP_WOUND;
    }
    if (tmp117_read_mC(PP_ADDR_TEMP_REFERENCE, &r.temp_ref_mC) != 0) {
        r.faults |= PP_FAULT_TEMP_REF;
    }
    if (tmp117_read_mC(PP_ADDR_TEMP_AMBIENT, &r.temp_ambient_mC) != 0) {
        r.faults |= PP_FAULT_TEMP_AMBIENT;
    }
    if (hal_moisture_measure_uv(&uv) == 0) {
        r.impedance_ohm = impedance_ohms(uv);
    } else {
        r.faults |= PP_FAULT_MOISTURE;
    }
    if (hal_adc_read_uv(PP_ADC_PH_DIFF, &uv) == 0) {
        r.ph_milli = ph_from_uv(&a->ph_cal, uv);
    } else {
        r.faults |= PP_FAULT_PH;
    }
    if (hal_adc_read_uv(PP_ADC_BATTERY, &uv) == 0) {
        r.battery_mV = uv / 500;                 /* 1:2 divider, microvolts to millivolts */
    } else {
        r.faults |= PP_FAULT_BATTERY;
    }
    r.pad_id_kohm = -1;
    if (hal_adc_read_uv(PP_ADC_PAD_ID, &uv) != 0) {
        r.faults |= PP_FAULT_PAD;
    } else if (uv < PP_PAD_ABSENT_UV) {
        r.pad_id_kohm = (int32_t)(((int64_t)PP_PAD_PULLUP_KOHM * uv) / (PP_SUPPLY_UV - uv));
    }
    a->last = r;
    a->last_read_ms = now_ms;
}

static therapy_inputs_t therapy_inputs(const app_t *a)
{
    therapy_inputs_t in;
    /* On the skin = pad detected and the moisture electrodes see tissue (the model's 150 kOhm rule). */
    in.pad_attached = a->last.pad_id_kohm >= 0 && (a->last.faults & PP_FAULT_MOISTURE) == 0 &&
                      a->last.impedance_ohm <= PP_LIFTED_OHMS;
    in.sensors_ok = (a->last.faults & PP_FAULT_TEMP_WOUND) == 0;
    in.hw_alert = hal_temp_alert_active();
    in.wound_mC = a->last.temp_wound_mC;
    in.battery_mV = a->last.battery_mV;
    return in;
}

static void report_end(app_t *a, therapy_end_t reason)
{
    hal_status_led(false);
    send_event('E', (int32_t)reason, (int32_t)(a->therapy.dose_uj_cm2 / 1000u), 0);
}

void app_init(app_t *a, uint32_t now_ms)
{
    *a = (app_t){ 0 };
    a->ph_cal.uv_at_ph7 = PP_PH_UV_AT_PH7;
    a->ph_cal.uv_per_ph = PP_PH_UV_PER_PH;
    therapy_init(&a->therapy);
    hal_status_led(false);
    /* A sensor that fails here keeps failing its reads, which sets its fault bit in every reading. */
    (void)tmp117_init(PP_ADDR_TEMP_WOUND, PP_ALERT_HIGH_MC, PP_ALERT_LOW_MC);
    (void)tmp117_init(PP_ADDR_TEMP_REFERENCE, PP_ALERT_HIGH_MC, PP_ALERT_LOW_MC);
    (void)tmp117_init(PP_ADDR_TEMP_AMBIENT, PP_AMBIENT_ALERT_HIGH_MC, PP_AMBIENT_ALERT_LOW_MC);
    take_reading(a, now_ms);
    send_reading(a);
    a->next_sample_ms = now_ms + PP_SAMPLE_PERIOD_MS;
}

void app_tick(app_t *a, uint32_t now_ms)
{
    bool active = a->therapy.state != TH_IDLE;
    bool due = (int32_t)(now_ms - a->next_sample_ms) >= 0;

    if (due || (active && now_ms - a->last_read_ms >= PP_THERAPY_CHECK_MS)) {
        take_reading(a, now_ms);
    }
    if (due) {
        send_reading(a);
        a->next_sample_ms += PP_SAMPLE_PERIOD_MS;
    }
    if (active) {
        therapy_inputs_t in = therapy_inputs(a);
        therapy_end_t end = therapy_tick(&a->therapy, now_ms, &in);
        if (end != TH_END_NONE) {
            report_end(a, end);
        }
    }
}

void app_command(app_t *a, uint32_t now_ms, const char *line)
{
    command_t cmd = telemetry_parse(line);

    switch (cmd.type) {
    case CMD_THERAPY: {
        therapy_inputs_t in;
        therapy_result_t result;
        take_reading(a, now_ms);
        in = therapy_inputs(a);
        result = therapy_start(&a->therapy, now_ms, cmd.us_ms, cmd.us_uw_cm2, cmd.led_ms, cmd.led_uw_cm2, &in);
        if (result == TH_OK) {
            hal_status_led(true);
            send_event('A', 0, (int32_t)a->therapy.us_ms, (int32_t)a->therapy.led_ms);
        } else {
            send_event('A', (int32_t)result, 0, 0);
        }
        break;
    }
    case CMD_STOP:
        if (a->therapy.state != TH_IDLE) {
            therapy_stop(&a->therapy, now_ms);
            report_end(a, TH_END_STOPPED);
        }
        break;
    case CMD_READ:
        take_reading(a, now_ms);
        send_reading(a);
        break;
    default:
        send_event('A', -1, 0, 0);
        break;
    }
}
