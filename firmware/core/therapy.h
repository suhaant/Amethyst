/* Therapy session control: ultrasound first, then 405 nm light, with interlocks and dose caps. */
#ifndef THERAPY_H
#define THERAPY_H

#include <stdbool.h>
#include <stdint.h>

typedef enum { TH_IDLE, TH_ULTRASOUND, TH_LIGHT } therapy_state_t;

typedef enum {
    TH_OK = 0,
    TH_ERR_BUSY,        /* a session is already running */
    TH_ERR_NO_PAD,      /* no disposable pad detected */
    TH_ERR_SENSOR,      /* wound temperature sensor not answering */
    TH_ERR_HOT,         /* wound already at the limit, or hardware alert active */
    TH_ERR_BATTERY,
    TH_ERR_DAILY_CAP,   /* today's light dose is used up */
    TH_ERR_NOTHING      /* request had zero ultrasound and zero light */
} therapy_result_t;

typedef enum {
    TH_END_NONE = 0,    /* still running, or idle */
    TH_END_DONE,
    TH_END_STOPPED,     /* stop command */
    TH_END_OVERTEMP,    /* firmware limit */
    TH_END_ALERT,       /* TMP117 hardware alert */
    TH_END_SENSOR,
    TH_END_PAD          /* pad removed mid-session */
} therapy_end_t;

typedef struct {
    bool pad_attached;
    bool sensors_ok;
    bool hw_alert;
    int32_t wound_mC;
    int32_t battery_mV;
} therapy_inputs_t;

typedef struct {
    therapy_state_t state;
    uint32_t us_ms, led_ms, led_uw_cm2;   /* the session actually running, after caps */
    uint16_t us_amplitude;                /* ultrasound drive level, 0..1000 */
    uint32_t phase_start_ms, last_tick_ms;
    uint32_t day;                         /* days since power-on; the daily dose resets when it changes */
    uint32_t dose_uj_cm2;                 /* light delivered today */
} therapy_t;

void therapy_init(therapy_t *t);
/* Drive level for a requested ultrasound intensity: amplitude scales with the square root of intensity,
 * limited to what the boost can produce. 0 for no ultrasound. */
uint16_t therapy_us_amplitude(uint32_t us_uw_cm2);
therapy_result_t therapy_start(therapy_t *t, uint32_t now_ms, uint32_t us_ms, uint32_t us_uw_cm2,
                               uint32_t led_ms, uint32_t led_uw_cm2, const therapy_inputs_t *in);
/* Call often while a session runs. Returns non-zero once, on the tick the session ends. */
therapy_end_t therapy_tick(therapy_t *t, uint32_t now_ms, const therapy_inputs_t *in);
void therapy_stop(therapy_t *t, uint32_t now_ms);

#endif
