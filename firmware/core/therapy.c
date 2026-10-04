#include "therapy.h"

#include "pp_config.h"
#include "pp_hal.h"

static void finish(therapy_t *t)
{
    hal_ultrasound_set(0);
    hal_led_set_permille(0);
    t->state = TH_IDLE;
}

void therapy_init(therapy_t *t)
{
    *t = (therapy_t){ 0 };
    finish(t);
}

static therapy_end_t unsafe(const therapy_inputs_t *in)
{
    if (in->hw_alert) {
        return TH_END_ALERT;
    }
    if (!in->sensors_ok) {
        return TH_END_SENSOR;
    }
    if (in->wound_mC >= PP_WOUND_MAX_MC) {
        return TH_END_OVERTEMP;
    }
    if (!in->pad_attached) {
        return TH_END_PAD;
    }
    return TH_END_NONE;
}

static uint32_t isqrt(uint32_t v)
{
    uint32_t root = 0, bit = 1u << 30;
    while (bit > v) {
        bit >>= 2;
    }
    while (bit) {
        if (v >= root + bit) {
            v -= root + bit;
            root = (root >> 1) + bit;
        } else {
            root >>= 1;
        }
        bit >>= 2;
    }
    return root;
}

uint16_t therapy_us_amplitude(uint32_t us_uw_cm2)
{
    uint32_t amplitude;
    if (us_uw_cm2 == 0) {
        return 0;
    }
    if (us_uw_cm2 >= PP_US_FULL_SCALE_UW_CM2) {
        return 1000;
    }
    amplitude = isqrt((uint32_t)(((uint64_t)us_uw_cm2 * 1000000u) / PP_US_FULL_SCALE_UW_CM2));
    return (uint16_t)(amplitude < PP_US_MIN_AMPLITUDE ? PP_US_MIN_AMPLITUDE : amplitude);
}

static void roll_day(therapy_t *t, uint32_t now_ms)
{
    uint32_t day = now_ms / PP_DAY_MS;
    if (day != t->day) {
        t->day = day;
        t->dose_uj_cm2 = 0;
    }
}

static void begin_light(therapy_t *t, uint32_t now_ms)
{
    uint32_t duty = (uint32_t)(((uint64_t)t->led_uw_cm2 * 1000u) / PP_LED_FULL_SCALE_UW_CM2);
    t->state = TH_LIGHT;
    t->phase_start_ms = now_ms;
    t->last_tick_ms = now_ms;
    hal_led_set_permille((uint16_t)(duty > 1000u ? 1000u : duty));
}

/* Add the light delivered since the last tick, never counting past the end of the light phase. */
static void account_light(therapy_t *t, uint32_t now_ms)
{
    uint32_t end_ms = t->phase_start_ms + t->led_ms;
    uint32_t upto = (now_ms - t->phase_start_ms) < t->led_ms ? now_ms : end_ms;
    uint32_t dt = upto - t->last_tick_ms;
    t->dose_uj_cm2 += (uint32_t)(((uint64_t)t->led_uw_cm2 * dt) / 1000u);
    t->last_tick_ms = upto;
}

therapy_result_t therapy_start(therapy_t *t, uint32_t now_ms, uint32_t us_ms, uint32_t us_uw_cm2,
                               uint32_t led_ms, uint32_t led_uw_cm2, const therapy_inputs_t *in)
{
    bool light_requested = led_ms > 0 && led_uw_cm2 > 0;

    if (t->state != TH_IDLE) {
        return TH_ERR_BUSY;
    }
    switch (unsafe(in)) {
    case TH_END_ALERT:
    case TH_END_OVERTEMP:
        return TH_ERR_HOT;
    case TH_END_SENSOR:
        return TH_ERR_SENSOR;
    case TH_END_PAD:
        return TH_ERR_NO_PAD;
    default:
        break;
    }
    if (in->battery_mV < PP_BATTERY_MIN_MV) {
        return TH_ERR_BATTERY;
    }
    roll_day(t, now_ms);

    if (us_uw_cm2 == 0) {
        us_ms = 0;
    }
    if (us_ms > PP_US_MAX_MS) {
        us_ms = PP_US_MAX_MS;
    }
    if (led_uw_cm2 > PP_LED_MAX_UW_CM2) {
        led_uw_cm2 = PP_LED_MAX_UW_CM2;
    }
    if (!light_requested) {
        led_ms = 0;
    } else {
        uint32_t remaining = PP_LED_DAILY_CAP_UJ_CM2 - t->dose_uj_cm2;
        uint64_t max_ms = ((uint64_t)remaining * 1000u) / led_uw_cm2;
        if (led_ms > max_ms) {
            led_ms = (uint32_t)max_ms;
        }
    }
    if (us_ms == 0 && led_ms == 0) {
        return light_requested ? TH_ERR_DAILY_CAP : TH_ERR_NOTHING;
    }

    t->us_ms = us_ms;
    t->led_ms = led_ms;
    t->led_uw_cm2 = led_uw_cm2;
    t->us_amplitude = therapy_us_amplitude(us_uw_cm2);
    t->phase_start_ms = now_ms;
    t->last_tick_ms = now_ms;
    if (us_ms > 0) {
        t->state = TH_ULTRASOUND;
        hal_ultrasound_set(t->us_amplitude);
    } else {
        begin_light(t, now_ms);
    }
    return TH_OK;
}

therapy_end_t therapy_tick(therapy_t *t, uint32_t now_ms, const therapy_inputs_t *in)
{
    therapy_end_t bad;
    uint32_t elapsed;

    if (t->state == TH_IDLE) {
        return TH_END_NONE;
    }
    if (t->state == TH_LIGHT) {
        account_light(t, now_ms);
    }
    bad = unsafe(in);
    if (bad != TH_END_NONE) {
        finish(t);
        return bad;
    }
    elapsed = now_ms - t->phase_start_ms;
    if (t->state == TH_ULTRASOUND) {
        if (elapsed < t->us_ms) {
            hal_ultrasound_set((elapsed % PP_US_BURST_PERIOD_MS) < PP_US_BURST_ON_MS ? t->us_amplitude : 0);
            return TH_END_NONE;
        }
        hal_ultrasound_set(0);
        if (t->led_ms > 0) {
            begin_light(t, now_ms);
            return TH_END_NONE;
        }
    } else if (elapsed < t->led_ms) {
        return TH_END_NONE;
    }
    finish(t);
    return TH_END_DONE;
}

void therapy_stop(therapy_t *t, uint32_t now_ms)
{
    if (t->state == TH_LIGHT) {
        account_light(t, now_ms);
    }
    finish(t);
}
