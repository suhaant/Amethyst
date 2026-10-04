/* Top level: takes a reading every 30 minutes, runs therapy sessions on command, reports over the link. */
#ifndef APP_H
#define APP_H

#include <stdint.h>

#include "ph.h"
#include "telemetry.h"
#include "therapy.h"

typedef struct {
    ph_cal_t ph_cal;
    therapy_t therapy;
    pp_reading_t last;
    uint32_t next_sample_ms, last_read_ms;
} app_t;

void app_init(app_t *a, uint32_t now_ms);
void app_tick(app_t *a, uint32_t now_ms);                       /* call at least once a second */
void app_command(app_t *a, uint32_t now_ms, const char *line);  /* one received text line */

#endif
